import logging
import os
import typing as T  # noqa
from pathlib import Path

from sqlalchemy.ext.asyncio import async_sessionmaker

from data.other.constants import PRACTISE_REGULARLY
from data.other.criteria_json import GRAMMAR_AND_LEXICAL_ERRORS_ADVICE
from src.libs.adapter import Adapter
from src.libs.factories.gpt.models.result import Result
from src.libs.factories.gpt.models.suggestion import Suggestion
from src.neural_network import ScoreGeneratorNNModel, timeit
from src.postgres.enums import CompetenceEnum
from src.postgres.models.tg_user_question import TgUserQuestion
from src.rabbitmq.worker.factories.simple_worker import SimpleWorker
from src.repos.factories.question import QuestionRepo
from src.services.constants import NeuralNetworkConstants as NNConstants
from src.services.factories.S3 import S3Service
from src.services.factories.answer_process import AnswerProcessService
from src.services.factories.tg_user import TgUserService
from src.services.factory import ServiceFactory
from src.services.factories.user_question import UserQuestionService as UQService
from src.settings import Settings


class ResultService(ServiceFactory):
    def __init__(
        self,
        repo: QuestionRepo,
        adapter: Adapter,
        session: async_sessionmaker,
        settings: Settings,
        nn_service: ScoreGeneratorNNModel,
        user_service: TgUserService,
        simple_worker: SimpleWorker,
        s3_service: S3Service
    ) -> None:
        super().__init__(repo, adapter, session, settings)
        self.repo = repo
        self.nn_service = nn_service
        self.user_service = user_service
        self.simple_worker = simple_worker
        self.s3_service = s3_service

    @timeit
    def check_or_load_models(self):
        if not self.nn_service.models:
            self.nn_service.load_models(NNConstants.predict_params['to_load'])

    async def generate_result(
        self,
        instance: TgUserQuestion,
        competence: CompetenceEnum,
        premium: bool = False,
        **kwargs
    ) -> T.Tuple[T.List, str, T.Dict]:
        self.check_or_load_models()
        request_text = await UQService.format_user_qa_to_full_text(instance.user_answer_json, competence)

        if competence == CompetenceEnum.speaking:
            answers_text_only = await UQService.format_user_qa_to_answers_only(instance.user_answer_json)
            file_paths = await AnswerProcessService.get_temp_data_filepaths(self.session, instance.id)
        else:
            answers_text_only = None
            file_paths = None

        additional_dict = None
        if premium:
            additional_dict = await self.generate_gpt_result_and_format(instance.user_answer_json, competence)
            await self.user_service.mark_user_activity(instance.user_id, 'use gpt request')

        result, extended_output, raw_results = await self._generate_result_local_model(
            request_text, competence, premium, **kwargs,
            answers_text_only=answers_text_only, file_paths=file_paths,
            user_qa=instance.user_answer_json, uq_id=instance.id, additional_dict=additional_dict
        )

        general_text = PRACTISE_REGULARLY
        if premium:
            if vocabulary := additional_dict.get('Vocabulary', None):
                general_text += f'\n - <b>Expand your vocabulary(Premium):</b>\n{vocabulary}'
            result.append(general_text)

        if competence == CompetenceEnum.speaking:
            self._clear_temp_files(file_paths)

        return result, extended_output, raw_results

    async def generate_gpt_result_and_format(self, user_answer_json: T.Dict, competence: CompetenceEnum) -> T.Dict:
        additional_request_text = await UQService.format_user_qa_to_text_for_gpt(user_answer_json, competence)
        for attempt in range(1, 5):
            try:
                additional_result = await self.adapter.gpt_client.generate_gpt_result(
                    additional_request_text, competence=competence)
                if additional_result:
                    break
            except Exception as e:
                logging.info(e)
                pass
        else:
            logging.error('GPT generation failed 5/5 (ValidationError)')
            return {}

        premium_results_dict = self.format_premium_result(additional_result)
        return premium_results_dict

    async def _generate_result_local_model(
        self,
        text: str,
        competence: CompetenceEnum,
        premium: bool = False,
        **kwargs
    ) -> T.Tuple[T.List[str], str, T.Dict]:
        additional_dict = kwargs.get('additional_dict', {})
        pronunciation_text = ''
        predict_params = NNConstants.predict_params[competence]
        if competence == CompetenceEnum.speaking:
            file_paths = kwargs.get('file_paths')
            self.s3_service.download_files_list([os.path.basename(key) for key in file_paths])

        results = self.nn_service.predict_all(
            text, predict_params, competence=competence, **kwargs)

        gr_score, gr_errors, lxc_errors, pnkt_errors = results.pop('clear_grammar_result')
        if gr_score < 5:
            gr_score = 5

        if competence == CompetenceEnum.writing:
            results['gr_Clear and correct grammar'] = gr_score
        elif competence == CompetenceEnum.speaking:
            results['gr_Error density'] = gr_score
            user_qa = kwargs.get('user_qa')

            user_p1_p3_qa = user_qa['part_1']
            try:
                user_p1_p3_qa.extend(user_qa['part_3'])
            except KeyError:
                pass

            lr_paraphrase_score, lr_premium_result = self.nn_service.lr_paraphrase_effectively(
                questions_and_answers=user_p1_p3_qa, premium=premium, **kwargs)
            results['lr_Paraphrases Effectively'] = lr_paraphrase_score

        advice_dict = self.nn_service.select_random_advice(results, competence)

        if competence == CompetenceEnum.writing:
            advice_dict['Grammatical Range']['Clear and correct grammar'] = GRAMMAR_AND_LEXICAL_ERRORS_ADVICE[gr_score]

        result = self.format_advice(advice_dict, results, competence, pronunciation_text, additional_dict)
        if premium:
            if competence == CompetenceEnum.speaking:
                result.extend(lr_premium_result)  # noqa
                pass

            grammar_errors = self.format_grammar_errors(gr_errors, lxc_errors, pnkt_errors, competence)
            result.extend(grammar_errors)
        extended_output = self.dict_to_string(results)
        return result, extended_output, results

    async def get_pronunciation(self, uq_id: int, filepaths, premium: bool = False):
        await self.simple_worker.initialize()
        await self.simple_worker.publish(
            {'filepaths': filepaths, 'uq_id': uq_id},
            'pronunciation_score_generate',
            self.simple_worker.get_priority(premium)
        )
        payload = await self.simple_worker.try_get_one_message(f'pronunciation_score_get_{uq_id}')
        if payload is None:
            return None
        return payload['pronunciation_score'], payload['pronunciation_text']

    @staticmethod
    def format_premium_result(result: Result) -> T.Dict[str, str]:
        def format_suggestion(suggestion: T.Optional[Suggestion]) -> T.Optional[str]:
            if suggestion is None:
                return None
            formatted_text = ""
            for enhancement in suggestion.enhancements:
                formatted_text += (
                    f"\n{enhancement.basic_suggestion}\n"
                    f"<b>Your answer:</b> {enhancement.source_text}\n"
                    f"<b>Enhanced answer:</b> {enhancement.enhanced_text}\n"
                )
            return formatted_text.strip()

        premium_dict = {}
        competence_results = result.competence_results
        suggestion_names = [
            ("Task Achievement", competence_results.task_achievement),
            ("Coherence and Cohesion", competence_results.fluency_coherence),
            ("Lexical Resources", competence_results.lexical_resources),
            ("Grammatical Range", competence_results.grammatical_range)
        ]
        for name, suggestion in suggestion_names:
            formatted_text = format_suggestion(suggestion)
            if formatted_text:
                premium_dict[name] = formatted_text
        vocabulary = '\n'.join(f'- {word}' for word in result.vocabulary)
        premium_dict["Vocabulary"] = vocabulary
        logging.info(f'premium_dict: {premium_dict}')
        return premium_dict

    @staticmethod
    def dict_to_string(d):
        return '\n'.join([f"{key}: {value}" for key, value in d.items()])

    @staticmethod
    def format_advice(advice_dict, results, competence: CompetenceEnum, pronunciation_text: str, premium_dict):
        premium_dict = {}
        output_texts = []
        all_category_min_scores = []
        for category, subcategories in advice_dict.items():
            sorted_advice = sorted(
                ((results.get(key, 0), advice) for subcategory, advice in subcategories.items() for key in results if
                 subcategory in key),
                reverse=False, key=lambda x: x[0]
            )
            if sorted_advice:
                category_min_score = sorted_advice[0][0]
                all_category_min_scores.append(category_min_score)
                # if category == 'Pronunciation' and pronunciation_text:
                #     category_advice_text = pronunciation_text
                # else:
                #     category_advice_texts = [f"{'✅' if score >= 7 else '⚠️'} {advice}" for score, advice in sorted_advice]  # noqa
                #     category_advice_text = "\n".join(category_advice_texts)
                category_advice_texts = [f"{'✅' if score >= 7 else '⚠️'} {advice}" for score, advice in sorted_advice]
                category_advice_text = "\n".join(category_advice_texts)
                category_text = f"<b>{category} (score {category_min_score}):</b>\n\n" + category_advice_text
                output_texts.append(category_text)
                if premium_text := premium_dict.get(category, None):
                    output_texts.append(premium_text)
        if all_category_min_scores:
            average_score = round(sum(all_category_min_scores) / len(all_category_min_scores) * 2) / 2
            output_texts.insert(0, f"\nYour <b>IELTS</b> {competence.value} <b>score</b> is <b>{average_score:.1f}</b>")
        return output_texts

    @staticmethod
    def format_error_examples(error_list, error_type):
        examples = [f"    <b>{error_type} Mistakes</b> ({len(error_list)}):\n"]
        for i, error in enumerate(error_list, 1):
            highlighted_text = error.context.replace(error.matchedText, f"<u>{error.matchedText}</u>")
            examples.append(f"        <b>Example {i}:</b> \"{highlighted_text}\" (Comment: \"{error.message}\")\n")
        return examples

    @staticmethod
    def format_grammar_errors(
        grammar_errors: T.List,
        lexical_errors: T.List,
        punctuation_errors: T.List,
        competence: CompetenceEnum = CompetenceEnum.writing
    ) -> T.List[str]:
        mistakes_text = ''
        if competence == CompetenceEnum.writing:
            mistakes_text = (f'<b>{len(grammar_errors)} grammar mistakes, {len(lexical_errors)} lexical mistakes </b> '
                             f'and <b>{len(punctuation_errors)} punctuation mistakes</b>. ')
        elif competence == CompetenceEnum.speaking:
            mistakes_text = f'<b>{len(grammar_errors)} grammar mistakes and {len(lexical_errors)} lexical mistakes </b>'
        output = [[
            "<b>Grammar and lexical errors (Premium):</b>\n\n",
            f"During the review of your text, we identified a total of {mistakes_text}"
        ]]
        if len(grammar_errors + lexical_errors + punctuation_errors) > 0:
            output[0].append("Below are some examples of each type of error:\n\n")

            if len(grammar_errors) > 0:
                grammar_output = ResultService.format_error_examples(grammar_errors, "Grammar")
                grammar_output = [grammar_output[i:i + 5] for i in range(0, len(grammar_output), 5)]
                output.extend(grammar_output)

            if len(lexical_errors) > 0:
                lexical_output = ResultService.format_error_examples(lexical_errors, "Lexical")
                lexical_output = [lexical_output[i:i + 5] for i in range(0, len(lexical_output), 5)]
                output.extend(lexical_output)

            if competence == CompetenceEnum.writing and len(punctuation_errors) > 0:
                punctuation_output = ResultService.format_error_examples(punctuation_errors, "Punctuation")
                punctuation_output = [punctuation_output[i:i + 5] for i in range(0, len(punctuation_output), 5)]
                output.extend(punctuation_output)

        final_output = []
        for part in output:
            final_output.append(''.join(part))
        return final_output

    @staticmethod
    def _clear_temp_files(filepaths: T.List[str]) -> None:
        for file in filepaths:
            path = Path(file)
            if path.exists():
                path.unlink()
