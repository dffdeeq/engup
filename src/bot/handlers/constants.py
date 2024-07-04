from src.postgres.enums import CompetenceEnum


class DefaultMessages:
    TOO_SHORT_TEXT_WARNING = ("Your essay must contain at least 150 words to meet the requirement. "
                              "However, for a better evaluation, aim for at least 250 words.")
    TEXT_IS_NOT_ENGLISH = ("It appears that your text is not written in English. Unfortunately, "
                           "I cannot process such an answer. Please rewrite it using English words and content.")
    TEXT_IS_COPY_PASTE = ('It appears that your text contains repeated phrases and seems to be copied and pasted '
                          'multiple times. Unfortunately, I cannot process such an answer. Please rewrite it with '
                          'original and meaningful content.')
    ASSESSMENT_FAILURE = "Sorry, but we could not assess your text, please try again with another card."
    DONT_HAVE_POINTS = ("<i>You don't have enough points on your balance to pass the test in advanced mode. "
                        "The advanced mode provides additional recommendations for effectively growing your skills "
                        "and increasing your grades, and also provides a priority pass to minimize waiting in line. "
                        "You can always buy additional points in the menu.</i>")
    CALCULATING_RESULT = ("Your result is being calculated and may take a couple of minutes.\n"
                          "We'll send it to you as soon as it's ready.")


class SpeakingMessages:
    FIRST_PART_MESSAGE_1 = ("Great! I will ask you some questions.\nPlease record audio to answer them\n"
                            "<u><a href='https://telegra.ph/How-to-Record-an-Audio-File-in-Telegram-07-04'>"
                            "How to Record an Audio File in Telegram</a></u>")
    FIRST_PART_MESSAGE_2 = "Let's start with part 1"
    COULDNT_FIND_AUDIO = 'Sorry, I couldn\'t find the audio.\n\nPlease, send me an voice message'
    SECOND_PART_MESSAGE = ("Ok! Let's proceed to <b>part 2</b>. Here is your card:\n\n<b>{question}</b>\n\n"
                           "You have 1 minute to prepare. Then record an audio up to 2 minutes")

    THIRD_PART_MESSAGE = "Great! Let's continue to the part 3"

    HOW_TO_RECORD_AUDIO = ("How to Record an Audio File in Telegram:\n\n"
                           "1. Tap on the microphone icon at the bottom right corner of the chat screen. "
                           "If you see a paperclip icon instead, tap on it to switch to the microphone.)\n"
                           "2. Hold down the microphone icon to start recording your voice message.\n"
                           "3. Speak clearly into your device's microphone.\n"
                           "4. Release the microphone icon when you are done recording. The audio message will be "
                           "automatically sent to the chat.")


class Constants:
    TG_CHANNEL_LINK = "https://t.me/IELTS_TEST_EXAM"

    PRACTICE_SPEAKING = ('Consistent practice is key to improvement. Train your speaking skills on a variety '
                         'of topics and receive feedback. Reviewing and revising your results based on feedback will '
                         'help you identify and correct recurring issues.')
    PRACTICE_WRITING = ('    Consistent practice is key to improvement. Write essays on a variety of topics and get '
                        'feedback. Reviewing and revising your essays based on feedback will help you identify and '
                        'correct recurring issues.')
    PRACTICE_REGULARLY_DICT = {CompetenceEnum.speaking: PRACTICE_SPEAKING, CompetenceEnum.writing: PRACTICE_WRITING}


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
        "{practice_regularly}\n\n"
        f"<b>3. Visit our channel</b> to get some useful tips: {Constants.TG_CHANNEL_LINK}"
    )
