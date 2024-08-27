import asyncio
import typing as T  # noqa
import re

import librosa
import numpy as np
from pydub import AudioSegment

from data.other.self_correction_patterns import SELF_CORRECTION_PATTERNS
from src.neural_network.base import NeuralNetworkBase
from src.neural_network.nn_models.utils.timeit import timeit


class FluencyCoherence(NeuralNetworkBase):
    @timeit
    def fc_speech_speed(self, text: str, **kwargs) -> float:
        file_paths: T.Optional[T.List] = kwargs.get('file_paths', None)
        if file_paths is None:
            return 4
        words_len = len(text.split())
        scores = []
        for file_path in file_paths:
            _, _, audio_duration = self.analyze_pauses(file_path)
            score = words_len / audio_duration
            scores.append(score)
        score = sum(scores) / len(scores)
        result_score = self.get_speech_speed_score(score)

        uq_id: T.Optional[int] = kwargs.get('uq_id', None)
        if uq_id is not None:
            asyncio.create_task(self.save_metric_data(uq_id, 'fc_f_ss', result_score, str(score)))

        return result_score

    @timeit
    def fc_self_corrections(self, text, **kwargs):
        _, corrections_len = self.identify_self_corrections(self.preprocess_text(text))
        score = 9.0 if corrections_len < 4 else 6.0

        uq_id: T.Optional[int] = kwargs.get('uq_id', None)
        if uq_id is not None:
            asyncio.create_task(self.save_metric_data(uq_id, 'fc_f_sc_msc', score))

        return score

    @staticmethod
    def preprocess_text(text):
        text = re.sub(r'[^\w\s]', '', text)
        return text.lower()

    @staticmethod
    def identify_self_corrections(text):
        corrections = []
        for pattern in SELF_CORRECTION_PATTERNS:
            matches = re.findall(pattern, text)
            corrections.extend(matches)
        return corrections, len(corrections)

    @staticmethod
    def analyze_pauses(file_name, min_pause_length=1.0):
        audio = AudioSegment.from_file(file_name)
        audio_data = np.array(audio.get_array_of_samples())
        sr = audio.frame_rate
        audio_duration = librosa.get_duration(y=audio_data, sr=sr)
        non_silent_intervals = librosa.effects.split(y=audio_data, top_db=30, frame_length=2048, hop_length=512)
        pauses = []
        prev_end = 0
        for interval in non_silent_intervals:
            start, end = interval
            pause_length = (start - prev_end) / sr
            if pause_length > 0:
                pauses.append((prev_end / sr, start / sr, pause_length))
            prev_end = end
        bad_pauses = [pause for pause in pauses if pause[2] > min_pause_length]
        return len(pauses), len(bad_pauses), audio_duration

    @staticmethod
    def get_speech_speed_score(value) -> float:
        ranges = [
            (0, 0.4, 4.0),
            (0.4, 0.6, 6.0),
            (0.6, 0.7, 7.0),
            (0.7, float('inf'), 9.0),
        ]
        for min_val, max_val, score in ranges:
            if min_val <= value < max_val:
                return score
        return 4.0
