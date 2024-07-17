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


class PrPronunciation(NeuralNetworkBase):
    def __init__(self, settings: NNModelsSettings) -> None:
        super().__init__(settings)
        self.voice_model_dir = os.path.join(NN_MODELS_DIR, 'pr_pronunciation_model')
        self.voice_model: T.Optional[SimpleNN] = None
        self.device = torch.device('cpu')

    def load(self):
        if not self.voice_model:
            self.voice_model = SimpleNN()
            self.voice_model.load_state_dict(torch.load(os.path.join(self.voice_model_dir, 'best_model.pth')))
            self.voice_model.eval()
        super().load()

    def get_pronunciation_score(self, **kwargs) -> float:
        ogg_file_paths: T.Optional[T.List[str]] = kwargs.get('file_paths', None)
        if ogg_file_paths is None:
            print('ogg file paths is None')
            return 4
        final_scores = []
        for ogg_file_path in ogg_file_paths:
            embs = self._get_embs_by_ogg(ogg_file_path)
            scores = [self._get_raw_score(emb) for emb in embs]
            average = sum(scores) / len(scores)
            converted_average = ((average - 1) / (10 - 1)) * (9 - 1) + 1
            score = math.floor(converted_average * 2) / 2
            final_scores.append(score)
        return math.floor(sum(final_scores) / len(final_scores) * 2) / 2

    def _get_raw_score(self, emb) -> int:
        with open(os.path.join(self.voice_model_dir, 'scaler.pkl'), 'rb') as f:
            scaler = pickle.load(f)
        with open(os.path.join(self.voice_model_dir, 'label_mappings.pkl'), 'rb') as f:
            mappings = pickle.load(f)
            int_to_label = mappings['int_to_label']

        new_embedding = list(emb)
        new_embedding = scaler.transform([new_embedding])[0]
        new_embedding_tensor = torch.tensor(new_embedding, dtype=torch.float32)

        with torch.no_grad():
            output = self.voice_model(new_embedding_tensor)
            _, predicted = torch.max(output.data, 0)

        return int(int_to_label[predicted.item()])

    def _get_embs_by_ogg(self, file_path) -> T.List[np.ndarray]:
        file_path = file_path.replace('.ogg', '')
        model = Model.from_pretrained(
            "pyannote/embedding", use_auth_token=self.settings.pyannotate_auth_token).to(self.device)
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

    def transform_wav_to_emb(self, wav_path, model) -> np.ndarray:
        inference = Inference(model, window="whole", device=self.device)
        embedding = inference(wav_path)
        return embedding

    @staticmethod
    def _clear_temp_files(filepaths: T.List[str]) -> None:
        for file in filepaths:
            path = Path(file)
            if path.exists():
                path.unlink()
