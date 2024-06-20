class DefaultMessages:
    TOO_SHORT_TEXT_WARNING = "Your text contains fewer than 150 words. Please rewrite it to meet the required length."
    ASSESSMENT_FAILURE = "Sorry, but we could not assess your text, please try again with another card."


class SpeakingMessages:
    FIRST_PART_MESSAGE_1 = "Great! I will ask you some questions. Please record audio to answer them"
    FIRST_PART_MESSAGE_2 = "Let's start with part 1"
    COULDNT_FIND_AUDIO = 'Sorry, I couldn\'t find the audio.\n\nPlease, send me an voice message'
    SECOND_PART_MESSAGE = ("Ok! Let's proceed to <b>part 2</b>. Here is your card:\n\n<b>{question}</b>\n\n"
                           "You have 1 minute to prepare. Then record an audio up to 2 minutes")

    THIRD_PART_MESSAGE = "Great! Let's continue to the part 3"

    CALCULATING_RESULT = ("Your result is being calculated and may take a couple of minutes.\n"
                          "We'll send it to you as soon as it's ready.")


class Links:
    TG_CHANNEL_LINK = "https://t.me/IELTS_TEST_EXAM"


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
        f"<b>3. Visit our channel</b> to get some useful tips: {Links.TG_CHANNEL_LINK}"
    )
