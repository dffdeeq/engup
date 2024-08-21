import logging
import typing as T  # noqa

import numpy as np
import torch
from sqlalchemy.ext.asyncio import async_sessionmaker
from torchaudio.transforms import Resample

from data.nn_models.ai_pronunciation_trainer import pronunciationTrainer
from data.nn_models.ai_pronunciation_trainer.lambdaSpeechToScore import audioread_load
from src.libs.factories.gpt import GPTClient
from src.rabbitmq.worker.factory import RabbitMQWorkerFactory
from src.repos.factories.user_question_metric import TgUserQuestionMetricRepo


class PronunciationWorker(RabbitMQWorkerFactory):
    def __init__(
        self,
        session: async_sessionmaker,
        repo: TgUserQuestionMetricRepo,
        dsn_string: str,
        queue_name: str,
        gpt_client: GPTClient
    ):
        super().__init__(repo, dsn_string, queue_name)
        self.session = session
        self.repo = repo
        self.gpt_client = gpt_client

    async def process_pronuncation(self, data: T.Dict):
        filepaths = data['filepaths']
        results = {
            'score': [],
            'levenshtein_score': [],
            'pronunciation_accuracy': [],
            'real_and_transcribed_words_ipa': []
        }
        for filepath in filepaths:
            try:
                score, levenshtein_score, accuracy, transcribed_words = await self.get_pronunciation(filepath)
                results['score'].append(score)
                results['levenshtein_score'].append(levenshtein_score)
                results['pronunciation_accuracy'].append(accuracy)
                results['real_and_transcribed_words_ipa'].append(transcribed_words)
            except Exception as e:
                logging.exception(e)

        logging.info(f'result scores: {results["score"]}')
        score = np.mean(results['score'])
        logging.info(score)
        score = self.score_to_band(score)
        levenshtein_score = np.mean(results['levenshtein_score'])
        accuracy = np.mean(results['pronunciation_accuracy'])
        transcribed_words = []
        for ipa_list in results['real_and_transcribed_words_ipa']:
            transcribed_words.extend(ipa_list)
        pronunciation_text = ''

        uq_id = data["uq_id"]
        await self.repo.create(
            uq_id,
            'pr_score', score, f"leven: {levenshtein_score}, acc: {accuracy},"
                               f" errors: {transcribed_words}")

        await self.publish({'pronunciation_score': score, 'pronunciation_text': pronunciation_text},
                           routing_key=f'pronunciation_score_get_{uq_id}', priority=data['priority'])

    async def get_pronunciation(self, filepath: str):
        transform = Resample(orig_freq=48000, new_freq=16000)
        signal, fs = audioread_load(filepath)
        logging.info(signal)
        logging.info(fs)
        signal = transform(torch.Tensor(signal)).unsqueeze(0)
        logging.info(signal)

        trainer_sst_lambda = {'en': pronunciationTrainer.getTrainer("en")}
        try:
            recording_transcript, recording_ipa, word_locations = trainer_sst_lambda['en'].getAudioTranscript(
                signal)
        except Exception as e:
            logging.exception("Error during getAudioTranscript")
            raise e

        logging.info(recording_transcript)
        logging.info(recording_ipa)
        logging.info(word_locations)

        # if not is_english(recording_transcript):
        #     details = 'Lang is not Eng'
        #     return 1.0

        result = await self.gpt_client.generate_transcript(recording_transcript)
        real_text = result.text

        result = trainer_sst_lambda['en'].processAudioForGivenText(signal, real_text)
        result_score = int(result['pronunciation_accuracy']) / 100
        logging.info(f'result_score: {result_score}')

        levenshtein_score = self.similarity_score(recording_transcript, real_text)
        score = result_score * 0.5 + levenshtein_score * 0.5
        logging.info(score)

        real_and_transcribed_words_ipa = []
        for index, pair in enumerate(result["real_and_transcribed_words_ipa"]):
            if result['pronunciation_categories'][index] == 2:
                text =  (f"{result['real_and_transcribed_words'][index][0]}: you said '{pair[1]}', "
                         f"the correct phoneme is '{pair[0]}'")
                real_and_transcribed_words_ipa.append(text)

        return score, levenshtein_score, result['pronunciation_accuracy'], real_and_transcribed_words_ipa

    def levenshtein_distance(self, a, b):
        if len(a) < len(b):
            return self.levenshtein_distance(b, a)

        if len(b) == 0:
            return len(a)

        previous_row = np.arange(len(b) + 1)
        for i, c1 in enumerate(a):
            current_row = np.zeros(len(b) + 1)
            current_row[0] = i + 1
            for j, c2 in enumerate(b):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row[j + 1] = min(insertions, deletions, substitutions)  # noqa
            previous_row = current_row

        return int(previous_row[-1])

    def similarity_score(self, initial_text, supposed_text):
        distance = self.levenshtein_distance(initial_text, supposed_text)
        max_distance = max(len(initial_text), len(supposed_text))
        score = (max_distance - distance) / max_distance
        return score

    @staticmethod
    def score_to_band(score):
        if score >= 0.7:
            return 9
        elif score >= 0.65:
            return 8
        elif score >= 0.6:
            return 7
        elif score >= 0.55:
            return 6
        elif score >= 0.5:
            return 5
        elif score >= 0.45:
            return 4
        elif score >= 0.4:
            return 3
        elif score >= 0.35:
            return 2
        else:
            return 1
