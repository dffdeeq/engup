import typing as T # noqa

from pydantic import Field

from src.settings.factory import SettingsFactory


class NNModelsSettings(SettingsFactory):
    pyannotate_auth_token: str = Field(description="pyannotate auth token")
    fal_key: str = Field(description="fal.ai key")

    @classmethod
    def from_dict(cls, settings_dict: T.Dict[str, str]) -> 'NNModelsSettings':
        return NNModelsSettings(
            pyannotate_auth_token=settings_dict.get('NN_SETTINGS_PYANNOTE_AUTH_TOKEN'),
            fal_key=settings_dict.get('NN_SETTINGS_FAL_KEY'),
        )
