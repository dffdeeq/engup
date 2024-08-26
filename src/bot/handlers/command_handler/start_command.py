import logging
import uuid

from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message

from src.bot.handlers.defaults.menu_default import answer_menu
from src.bot.injector import INJECTOR
from src.libs.factories.analytics.models.event_data import EventData
from src.services.factories.metrics import MetricsService
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.message(
    CommandStart(),
    INJECTOR.inject_tg_user,
    INJECTOR.inject_metrics_service
)
async def command_start_handler(
    message: Message,
    command: CommandObject,
    tg_user_service: TgUserService,
    metrics_service: MetricsService
) -> None:
    user_referrer_id = None
    command_args = command.args
    utm_source = None
    utm_medium = None
    utm_campaign = None
    utm_content = None
    utm_term = None
    gad_source = None
    gclid = None
    if command_args:
        try:
            try:
                metrics_uuid = uuid.UUID(command_args)
                metrics_data = await metrics_service.get_metrics_data(metrics_uuid)
                metrics_string = metrics_data.metrics_string.split('__')
                logging.info(f'args: {metrics_string}')
                variables = {}
                for item in metrics_string:
                    key, value = item.split("=")
                    variables[key] = value

                utm_source = variables.get('utm_source', 'None')
                utm_medium = variables.get('utm_medium', 'None')
                utm_campaign = variables.get('utm_campaign', 'None')
                utm_content = variables.get('utm_content', 'None')
                utm_term = variables.get('utm_term', 'None')
                gad_source = variables.get('gad_source', 'None')
                gclid = variables.get('gclid', 'None')

                await tg_user_service.adapter.analytics_client.send_event(
                    str(uuid.uuid4()),
                    EventData(
                        utm_source=utm_source,
                        utm_medium=utm_medium,
                        utm_campaign=utm_campaign,
                        utm_content=utm_content,
                        event_name='conversion_event_signup',
                    )
                )

            except ValueError:
                referral = await tg_user_service.repo.get_tg_user_by_tg_id(int(command_args))
                if referral:
                    user_referrer_id = referral.id
        except Exception as e:
            logging.error(e)

    await tg_user_service.get_or_create_tg_user(
        message.from_user.id, message.from_user.username, user_referrer_id, utm_source, utm_medium, utm_campaign,
        utm_content, utm_term, gad_source, gclid
    )
    await tg_user_service.mark_user_activity(message.from_user.id, 'go to menu')
    await answer_menu(message)
