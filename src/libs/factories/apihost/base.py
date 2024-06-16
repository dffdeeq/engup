import typing as T # noqa

from aiohttp import FormData

from src.libs.http_client import HttpClient, HttpClientResponse
from src.settings.factories.apihost import ApiHostSettings


class BaseApiHostClient:
    def __init__(self, http_client: HttpClient, settings: ApiHostSettings) -> None:
        self.http_client = http_client
        self.settings = settings

    async def request(
        self,
        method: str,
        route: str,
        data: T.Optional[T.Dict[str, T.Any] | FormData] = None,
        json: T.Optional[T.Dict[str, T.Any]] = None,
        params: T.Optional[T.Dict[str, T.Any]] = None,
    ) -> HttpClientResponse:
        headers = {
            'Authorization': f'Bearer {self.settings.auth_token}',
        }
        url = self.settings.url + route
        return await self.http_client.request(
            method,
            url,
            data=data,
            json_=json,
            headers=headers,
            params=params,
        )
