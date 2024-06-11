class Messages:
    TOO_SHORT_TEXT_WARNING = "Your input text is too short. Please enter at least 150 words."
    ASSESSMENT_FAILURE = "Sorry, but we could not assess your text, please try again with another card."


class Constants:
    TG_CHANNEL_LINK = "https://t.me/engupclub"


class MessageTemplates:
    CARD_TEXT_TEMPLATE = (
        "<b>Card title:</b> {card_title}\n\n"
        "<b>Card body:</b> {card_body}"
    )

    GENERAL_RECOMMENDATIONS_TEMPLATE = (
        "<b>General Recommendations:\n\n"
        "1. Expand Your Vocabulary:</b>\n"
        "{vocabulary}\n\n"
        "<b>2. Practice Regularly:</b>\n"
        " - Consistent practice is key to improvement. Write essays on a variety of topics and get feedback. "
        "Reviewing and revising your essays based on feedback will help you identify and correct recurring issues.\n\n"
        f"<b>3. Visit our channel</b> to get some useful tips: {Constants.TG_CHANNEL_LINK}"
    )
