from src.postgres.enums import CompetenceEnum


class DefaultMessages:
    START_MESSAGE = """
💬 This chatbot will help you prepare for IELTS. 

📝 It gives you tasks to complete and checks how well you are doing, providing you with feedback on your progress. 

✅ The chatbot meets the standards of IELTS. If you follow its recommendations, your IELTS score will be higher 🎯
"""

    DEFAULT_TEXT = """
<b>Welcome to IELTS Writing Practice!</b>
    
Let's get you ready for the IELTS Writing exam, essay part 2. Here’s a brief overview of what to expect in the test:
    
IELTS Writing Exam Overview
    
The IELTS Writing test is designed to assess your writing skills and is divided into two parts. The entire test lasts for 60 minutes.
    
Part 1: Task 1 (20 minutes)
    
In this part, you are required to write a short report based on visual information such as charts, graphs, or diagrams. You should summarize the information, highlight key features, and make comparisons where relevant. This task tests your ability to interpret and describe data in a clear and organized manner.
    
Part 2: Essay (40 minutes)
    
You will be given a prompt that presents a point of view, argument, or problem. You are required to write an essay in response to the prompt. Your essay should be at least 250 words long and should address all parts of the question. You will need to present a clear position, support your ideas with relevant examples and evidence, and demonstrate a logical progression of ideas. This part tests your ability to construct a coherent argument and express your thoughts in a structured and persuasive manner.
    
<b>Here, we will assess your ability to produce a coherent and well-structured IELTS part 2 essay.</b>
"""
    WRITING_FIRST_PARAGRAPH_1 = """
Here is your card with the essay topic: <b>"{card_text}"</b>
"""
    WRITING_FIRST_PARAGRAPH_2 = """
Your essay type is <b>"{essay_type}"</b>, which means you should have four paragraphs. Here is a brief description of this type of essay: {essay_description}.
"""
    WRITING_FIRST_PARAGRAPH_3 = """
The first paragraph should include the following information: 
<b>Paragraph {first_paragraph_info}.</b>

Please write the first paragraph using the chat.
"""
    WRITING_PARAGRAPH_DEFAULT = """
The {paragraph} paragraph should include the following information: 
<b>Paragraph {paragraph_info}.</b>

Please write the {paragraph} paragraph using the chat.
"""

    TOO_SHORT_TEXT_WARNING = "You have used a very short paragraph in this text. Please try to expand your writing to at least <b>30 words.</b>"
    TEXT_IS_NOT_ENGLISH = ("It appears that your text is not written in English. Unfortunately, "
                           "I cannot process such an answer. Please rewrite it using English words and content.")
    TEXT_IS_COPY_PASTE = ('It appears that your text contains repeated phrases and seems to be copied and pasted '
                          'multiple times. Unfortunately, I cannot process such an answer. Please rewrite it with '
                          'original and meaningful content.')
    ASSESSMENT_FAILURE = "Sorry, but we could not assess your text, please try again with another card."
    DONT_HAVE_POINTS = ('You do not have neither premium tests, nor active subscription left in your account. '
                        'To continue, top up your balance in premium tests or purchase a subscription.')
    HAVE_POINTS = ('Thank you for completing all the questions! To confirm your response, '
                   'please click "Continue":')
    CALCULATING_RESULT = "Once you have confirmed, we have started evaluating your answers. Your answers are currently being processed, and we expect to provide you with results in a few minutes. Thank you for your patience."

    LOW_POINTS_BALANCE_ALERT = """
<b>Low Points Balance Alert</b>
It looks like you have less than 3 points remaining in your balance. To continue using our IELTS Speaking Practice service, you have three options to refill your points:

    1. <b>Buy PTs or subscription:</b> Purchase additional points or subscribe to keep practicing without interruption.

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
"""
    FIRST_PART_MESSAGE_2 = """
    
<b>You will be asked a question and you will need to respond using the voice recording feature available in Telegram. To activate this feature, please hold down the microphone button 🎙 and speak your response.</b>
    
<u><a href='https://telegra.ph/How-to-Record-an-Audio-File-in-Telegram-07-04'>How to Record an Audio File in Telegram</a></u>

Let's begin!
    """
    COULDNT_FIND_AUDIO = 'Sorry, I couldn\'t find the audio.\n\nPlease, send me an voice message'

    SECOND_PART_MESSAGE = """
Welcome to Part 2 of the IELTS Speaking test. This part lasts 3-4 minutes. You will be given a task card with a topic and have 1 minute to prepare your answer. You’ll then speak for 1-2 minutes on the topic without interruption. This part tests your ability to speak at length on a given topic.

Please note that if your recording exceeds 2 minutes, it will be cut off at the 2-minute mark, and any additional content will not be counted. This part tests your ability to speak at length on a given topic.

<b>Below is your topic. Take a minute to prepare.</b>
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
