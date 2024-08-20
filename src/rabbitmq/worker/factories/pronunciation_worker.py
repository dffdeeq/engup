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

    async def get_pronuncation(self, data: T.Dict):
        try:
            transform = Resample(orig_freq=48000, new_freq=16000)
            filepath = data['filepath']
            signal, fs = audioread_load(filepath)
            logging.info(signal)
            logging.info(fs)
            signal = transform(torch.Tensor(signal)).unsqueeze(0)
            logging.info(signal)

            trainer_sst_lambda = {'en': pronunciationTrainer.getTrainer("en")}
            recording_transcript, recording_ipa, word_locations = trainer_sst_lambda['en'].getAudioTranscript(
                signal)

            logging.info(recording_transcript)
            logging.info(recording_ipa)
            logging.info(word_locations)

            # if not is_english(recording_transcript):
            #     details = 'Lang is not Eng'
            #     return 1.0

            result = await self.gpt_client.generate_transcript(recording_transcript)
            real_text = result.text

            logging.info(f'real_text sssss: {real_text}')
            result = trainer_sst_lambda['en'].processAudioForGivenText(signal, real_text)
            logging.info(result)
            result_score = int(result['pronunciation_accuracy']) / 100
            logging.info(f'result_score: {result_score}')

            levenshtein_score = self.similarity_score(recording_transcript, real_text)
            logging.info(levenshtein_score)
            score = result_score * 0.5 + levenshtein_score * 0.5
            logging.info(score)
            score = self.score_to_band(score)
            pronunciation_text = ''

            uq_id = data["uq_id"]

            await self.repo.create(
                uq_id,
                'pr_score', score, f"leven: {levenshtein_score}, acc: {result['pronunciation_accuracy']},"
                                   f" errors: {result['real_and_transcribed_words_ipa']}")

            await self.publish({'pronunciation_score': score, 'pronunciation_text': pronunciation_text},
                               routing_key=f'pronunciation_score_get_{uq_id}', priority=data['priority'])
            return score
        except Exception as e:
            logging.exception(e)

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
        if score >= 0.9:
            return 9
        elif score >= 0.85:
            return 8
        elif score >= 0.8:
            return 7
        elif score >= 0.75:
            return 6
        elif score >= 0.7:
            return 5
        elif score >= 0.65:
            return 4
        elif score >= 0.6:
            return 3
        elif score >= 0.55:
            return 2
        else:
            return 1
