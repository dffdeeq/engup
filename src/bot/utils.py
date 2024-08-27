import re
import typing as T  # noqa

from langdetect import detect, LangDetectException


def is_copypaste(text):
    normalized_text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?]) +', normalized_text)

    sentence_count = len(sentences)
    if sentence_count < 2:
        return False
    for i in range(sentence_count):
        repetition_count = normalized_text.count(sentences[i])
        if repetition_count > 1:
            return True
    return False


def is_english(text):
    try:
        language = detect(text)
        return True if language == "en" else False
    except LangDetectException:
        return False
