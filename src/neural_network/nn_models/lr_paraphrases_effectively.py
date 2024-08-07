import logging
import typing as T  # noqa
import os.path

from sklearn.metrics.pairwise import cosine_similarity
import nltk
from collections import Counter

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

from src.neural_network.nn_models.utils.timeit import timeit
from src.neural_network.base import NeuralNetworkBase
from src.repos.factories.user_question_metric import TgUserQuestionMetricRepo
from src.settings import NNModelsSettings
from src.settings.static import NN_MODELS_DIR


class LrParaphraseEffectively(NeuralNetworkBase):
    def __init__(self, settings: NNModelsSettings, uq_metric_repo: TgUserQuestionMetricRepo):
        super().__init__(settings, uq_metric_repo)
        self.lr_paraphrase_model = None
        self.nltk_perceptron_dir = os.path.join(self._nn_models_dir, 'averaged_perceptron_tagger')  # noqa

    def load(self):
        if not self.lr_paraphrase_model:
            model_load_path = os.path.join(NN_MODELS_DIR, 'bge-m3')
            self.lr_paraphrase_model = SentenceTransformer(model_load_path)
            tokenizer = AutoTokenizer.from_pretrained(model_load_path)
            self.lr_paraphrase_model.tokenizer = tokenizer
        if not os.path.exists(self.nltk_perceptron_dir):
            nltk.download('averaged_perceptron_tagger', download_dir=self.nltk_perceptron_dir)
        nltk.data.path.append(self.nltk_perceptron_dir)
        super().load()

    @timeit
    def lr_paraphrase_effectively(self, **kwargs) -> T.Tuple[float, T.List[str]]:
        questions_and_answers: T.Optional[T.List[T.Dict[str, str]]] = kwargs.get('questions_and_answers', None)
        premium: bool = kwargs.get('premium', False)
        if questions_and_answers is None:
            logging.info('questions_and_answers is None!!!!!!!!!!!!!!!\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            return 4.0, []

        paraphrasing_results = []
        good_paraphrasing_count = 0
        for qa in questions_and_answers:
            result = self.check_paraphrasing(
                qa['card_text'], qa['user_answer'])
            result.extend([qa['card_text'], qa['user_answer']])
            paraphrasing_results.append(result)
            if result[0]:
                good_paraphrasing_count += 1

        premium_result = []
        if premium:
            premium_result = self.format_premium_result(paraphrasing_results, good_paraphrasing_count)  # noqa

        good_paraphrasing_percent = good_paraphrasing_count / len(paraphrasing_results) * 100
        bands = [
            (90, 9.0),
            (80, 8.0),
            (70, 7.0),
            (40, 6.0),
            (0, 5.0)
        ]
        for band_percent, grade in bands:
            if good_paraphrasing_percent >= band_percent:
                return grade, premium_result

    def check_paraphrasing(self, question: str, answer: str):
        question_preprocessed = question.lower()
        answer_preprocessed = answer.lower()

        identical_pos_count, common_words = self.count_identical_pos(question_preprocessed, answer_preprocessed)
        bge_m3_sim = self.bge_m3_similarity(question_preprocessed, answer_preprocessed)

        identical_pos_threshold = 5
        bge_m3_threshold = 0.5

        is_good_paraphrasing = identical_pos_threshold > identical_pos_count and bge_m3_sim > bge_m3_threshold

        return [is_good_paraphrasing, common_words, identical_pos_count, bge_m3_sim]

    @staticmethod
    def count_identical_pos(text1, text2):
        tokens1 = nltk.word_tokenize(text1)
        tokens2 = nltk.word_tokenize(text2)
        pos_tags1 = nltk.pos_tag(tokens1)
        pos_tags2 = nltk.pos_tag(tokens2)
        exclude_words = {'is', 'are', 'was', 'were', 'be', 'being', 'been',
                         'am', 'isn\'t', 'aren\'t', 'wasn\'t', 'weren\'t',
                         'has', 'have', 'had', 'hasn\'t', 'haven\'t', 'hadn\'t'}
        pos_of_interest = {
            'RB', 'RBR', 'RBS',
            'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',
            'JJ', 'JJR', 'JJS',
            'NN', 'NNS', 'NNP', 'NNPS'
        }
        filtered_words1 = [word for word, pos in pos_tags1 if pos in pos_of_interest
                           and word.lower() not in exclude_words]
        filtered_words2 = [word for word, pos in pos_tags2 if pos in pos_of_interest
                           and word.lower() not in exclude_words]

        counter1 = Counter(filtered_words1)
        counter2 = Counter(filtered_words2)
        common_words = counter1 & counter2
        identical_word_count = sum(common_words.values())

        return identical_word_count, common_words

    def bge_m3_similarity(self, text1, text2):
        embeddings1 = self.lr_paraphrase_model.encode([text1])
        embeddings2 = self.lr_paraphrase_model.encode([text2])

        cosine_sim = cosine_similarity(embeddings1, embeddings2)
        return cosine_sim[0][0]

    @staticmethod
    def format_premium_result(
        paraphrasing_results: T.List[T.Tuple[bool, Counter, int, float, str, str]],
        good_paraphrasing_count: int
    ) -> T.List[str]:
        good_example = None
        bad_example = None
        paraphrasing_text_chunks = []
        current_chunk = ''
        example_count = 0

        for paraphrasing in paraphrasing_results:
            if paraphrasing[0]:
                good_example = paraphrasing[4] + ' - ' + paraphrasing[5]
            else:
                common_words, identical_pos_count, bge_m3_sim = paraphrasing[1], paraphrasing[2], paraphrasing[3]
                bad_example = paraphrasing[4] + ' - ' + paraphrasing[5]
                current_chunk += f'\n\n<b>{bad_example}</b>'

                unique_elements = common_words.keys()
                following_terms = f'<b>({", ".join(unique_elements)})</b>'

                if bge_m3_sim > 0.5 and identical_pos_count >= 5:
                    current_chunk += (
                        '\nIn this instance, you successfully addressed the query, but you repeated the'
                        f' following terms {following_terms} from it.')
                elif bge_m3_sim <= 0.5 and identical_pos_count < 5:
                    current_chunk += '\nIn this instance, you failed to address the query.'
                elif bge_m3_sim <= 0.5 and identical_pos_count >= 5:
                    current_chunk += (f'\nIn this instance, you have repeated the following terms'
                                      f'{following_terms} from the query and '
                                      f'failed to address the query.')
                # current_chunk += f'\nbge: {bge_m3_sim}, identical_pos_count: {identical_pos_count}'  # additional

                example_count += 1
                if example_count == 5:
                    paraphrasing_text_chunks.append(current_chunk)
                    current_chunk = ''
                    example_count = 0

        if current_chunk:
            paraphrasing_text_chunks.append(current_chunk)

        text_intro = (f"You have successfully rephrased the responses to {good_paraphrasing_count} "
                      f"questions out of {len(paraphrasing_results)}.\n\n")
        text_intro += f"An example of a successful rephrasing:\n<b>{good_example}</b> ✅" if good_example else ''
        text_intro += f"\n\nAn instance of an unsuccessful rephrase:\n<b>{bad_example}</b> ⚠️" if bad_example else ''

        final_text_chunks = paraphrasing_text_chunks
        final_text_chunks.insert(0, text_intro)

        for text_chunk in final_text_chunks:
            logging.info(text_chunk)

        return final_text_chunks
