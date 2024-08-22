import typing as T # noqa

from aiohttp import FormData

from src.libs.http_client import HttpClient, HttpClientResponse
from src.settings.factories.analytics import AnalyticsSettings


class BaseAnalyticsClient:
    def __init__(self, http_client: HttpClient, settings: AnalyticsSettings) -> None:
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
            'Content-Type': 'application/json'
        }
        params['api_secret'] = self.settings.api_secret
        url = self.settings.url + route
        print(url)
        return await self.http_client.request(
            method,
            url,
            data=data,
            json_=json,
            headers=headers,
            params=params,
        )
