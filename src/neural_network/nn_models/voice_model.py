import typing as T  # noqa
import io
import math
import os.path
from pathlib import Path

import numpy as np
import torch
import pickle
from pyannote.audio import Inference
from pydub import AudioSegment
from pyannote.audio import Model

from src.neural_network.base import NeuralNetworkBase
from src.neural_network.nn_models.utils.simple_nn_model import SimpleNN
from src.settings import NNModelsSettings
from src.settings.static import NN_MODELS_DIR


class VoiceModel(NeuralNetworkBase):
    def __init__(self, settings: NNModelsSettings) -> None:
        super().__init__(settings)
        self.model_dir = os.path.join(NN_MODELS_DIR, 'voice_model')
        self.nn_model: T.Optional[SimpleNN] = None

    def load(self):
        if not self.nn_model:
            self.nn_model = SimpleNN()
            self.nn_model.load_state_dict(torch.load(os.path.join(self.model_dir, 'best_model.pth')))
            self.nn_model.eval()
            print('loaded+')
        super().load()

    def get_pronunciation_score(self, ogg_file_paths: T.List[str]) -> float:
        final_scores = []
        for ogg_file_path in ogg_file_paths:
            ogg_file_path = ogg_file_path.replace('.ogg', '')
            embs = self._get_embs_by_ogg(ogg_file_path)
            scores = [self._get_raw_score(emb) for emb in embs]
            self._clear_temp_files([f"{ogg_file_path}.wav"])
            average = sum(scores) / len(scores)
            converted_average = ((average - 1) / (10 - 1)) * (9 - 1) + 1
            score = math.floor(converted_average * 2) / 2
            final_scores.append(score)
        return math.floor(sum(final_scores) / len(final_scores) * 2) / 2

    def _get_raw_score(self, emb) -> int:
        with open(os.path.join(self.model_dir, 'scaler.pkl'), 'rb') as f:
            scaler = pickle.load(f)
        with open(os.path.join(self.model_dir, 'label_mappings.pkl'), 'rb') as f:
            mappings = pickle.load(f)
            int_to_label = mappings['int_to_label']

        new_embedding = list(emb)
        new_embedding = scaler.transform([new_embedding])[0]
        new_embedding_tensor = torch.tensor(new_embedding, dtype=torch.float32)

        with torch.no_grad():
            output = self.nn_model(new_embedding_tensor)
            _, predicted = torch.max(output.data, 0)

        return int(int_to_label[predicted.item()])

    def _get_embs_by_ogg(self, file_path) -> T.List[np.ndarray]:
        model = Model.from_pretrained(
            "pyannote/embedding", use_auth_token=self.settings.pyannotate_auth_token)
        emb_list = [
            self.transform_wav_to_emb(f"{file_path}.wav", model)
            for bit_rate in [40, 64, 128, 256]
            if self.convert_ogg_to_wav(file_path, bit_rate)
        ]
        return emb_list

    @staticmethod
    def convert_ogg_to_wav(file_path, target_bitrate=16):
        ogg_audio = AudioSegment.from_file(f"{file_path}.ogg", format="ogg")
        audio_zipped_mp3_io = io.BytesIO()
        ogg_audio.export(audio_zipped_mp3_io, format="mp3", bitrate=f"{target_bitrate}k")
        audio_mp3 = AudioSegment.from_file(audio_zipped_mp3_io, format='mp3')
        audio_mp3.export(f"{file_path}.wav", format="wav")
        return True

    @staticmethod
    def transform_wav_to_emb(wav_path, model) -> np.ndarray:
        inference = Inference(model, window="whole")
        embedding = inference(wav_path)
        return embedding

    @staticmethod
    def _clear_temp_files(filepaths: T.List[str]) -> None:
        for file in filepaths:
            path = Path(file)
            if path.exists():
                path.unlink()
