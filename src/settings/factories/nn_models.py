import typing as T # noqa

from pydantic import Field

from src.settings.factory import SettingsFactory


class NNModelsSettings(SettingsFactory):
    pyannotate_auth_token: str = Field(description="pyannotate auth token")

    @classmethod
    def from_dict(cls, settings_dict: T.Dict[str, str]) -> 'NNModelsSettings':
        return NNModelsSettings(
            pyannotate_auth_token=settings_dict.get('NN_SETTINGS_PYANNOTE_AUTH_TOKEN'),
        )
