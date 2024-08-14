import uuid

from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message

from src.bot.handlers.defaults.menu_default import answer_menu
from src.bot.injector import INJECTOR
from src.libs.factories.analytics.models.event_data import EventData
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.message(CommandStart(), INJECTOR.inject_tg_user)
async def command_start_handler(message: Message, command: CommandObject, tg_user_service: TgUserService) -> None:
    user_referrer_id = None
    command_args = command.args
    utm_source = None
    utm_medium = None
    utm_campaign = None
    utm_content = None
    if command_args:
        if '__' in command_args:
            args = command_args.split('__')
            variables = {}
            for item in args:
                key, value = item.split("=")
                variables[key] = value

                utm_source = variables.get('utm_source', 'None')
                utm_medium = variables.get('utm_medium', 'None')
                utm_campaign = variables.get('utm_campaign', 'None')
                utm_content = variables.get('utm_content', 'None')

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

        else:
            referral = await tg_user_service.repo.get_tg_user_by_tg_id(int(command_args))
            if referral:
                user_referrer_id = referral.id

    await tg_user_service.get_or_create_tg_user(message.from_user.id, message.from_user.username, user_referrer_id,
                                                utm_source, utm_medium, utm_campaign, utm_content)
    await tg_user_service.mark_user_activity(message.from_user.id, 'go to menu')
    await answer_menu(message)
