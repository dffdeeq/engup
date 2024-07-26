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

    LOW_POINTS_BALANCE_ALERT = """
<b>Low Points Balance Alert</b>
It looks like you have less than 3 points remaining in your balance. To continue using our IELTS Speaking Practice service, you have three options to refill your points:

    1. <b>Buy Points:</b> Purchase additional points to keep practicing without interruption.

    2. <b>Recommend/Share Our Service:</b> Share our service with friends or on social media to earn extra points.

    3. <b>Leave Feedback:</b> Provide feedback on your experience to help us improve and earn points as a thank you.

Choose the option that works best for you and continue your IELTS Speaking journey without any delays. Thank you for being a part of our community!
    """


class SpeakingMessages:
    DEFAULT_MESSAGE = """
<b>Welcome to IELTS Speaking Practice!</b>
Let's get you ready for the IELTS Speaking exam. Here’s a brief overview of what to expect in the test:

<b>IELTS Speaking Exam Overview</b>
The IELTS Speaking test is designed to assess your spoken English skills and is divided into three parts. The entire test lasts between 11 and 14 minutes.

<b>Part 1: Introduction and Interview (4-5 minutes)</b>
In this part, the examiner will introduce themselves and ask you to do the same. You’ll be asked general questions about yourself, your home, family, work, studies, and interests. This part aims to relax you and get you comfortable with speaking English.

<b>Part 2: Long Turn (3-4 minutes)</b>
You will be given a task card with a topic and have 1 minute to prepare your answer. You’ll then speak for 1-2 minutes on the topic without interruption. This part tests your ability to speak at length on a given topic.

<b>Part 3: Discussion (4-5 minutes)</b>
The examiner will ask further questions related to the topic in Part 2. This is an opportunity to discuss more abstract ideas and issues. This part assesses your ability to express and justify opinions, analyze, discuss, and speculate about issues.
    """

    FIRST_PART_MESSAGE_1 = """
Welcome to Part 1 of the IELTS Speaking test. This part lasts 4-5 minutes. You will be asked general questions about yourself, your home, family, work, studies, and interests. The goal is to get you comfortable and speaking freely

Please note that if your recording exceeds 1.5 minutes, it will be cut off at the 1.5-minute mark, and any additional content will not be counted. 

This part tests your ability to speak at length on a given topic.


Let's begin!“
    """
    COULDNT_FIND_AUDIO = 'Sorry, I couldn\'t find the audio.\n\nPlease, send me an voice message'
    SECOND_PART_MESSAGE = """
Welcome to Part 2 of the IELTS Speaking test. This part lasts 3-4 minutes. You will be given a task card with a topic and have 1 minute to prepare your answer. You’ll then speak for 1-2 minutes on the topic without interruption. This part tests your ability to speak at length on a given topic.

Please note that if your recording exceeds 2 minutes, it will be cut off at the 2-minute mark, and any additional content will not be counted. This part tests your ability to speak at length on a given topic.

Here’s your topic. Take a minute to prepare.”
    """

    THIRD_PART_MESSAGE = """
Welcome to Part 3 of the IELTS Speaking test. This part lasts 4-5 minutes. You will be asked  further questions related to the topic in Part 2. This is an opportunity to discuss more abstract ideas and issues. 

Please note that if your recording exceeds 1.5 minutes, it will be cut off at the 1.5-minute mark, and any additional content will not be counted. 

This part assesses your ability to express and justify opinions, analyze, discuss, and speculate about issues.

Let’s dive into the discussion!
    """

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
