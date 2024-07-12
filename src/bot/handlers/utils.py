import re
import typing as T  # noqa

from langdetect import detect, LangDetectException

from src.libs.factories.gpt.models.result import Result
from src.libs.factories.gpt.models.suggestion import Enhancement
from src.postgres.enums import CompetenceEnum


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


async def generate_section(title: str, score: float, enhancements: T.List[Enhancement]) -> str:
    section = f'<b>{title} (score {score}):</b>\n'
    if not enhancements:
        return section + '\n\nThere are no enhancements for this section.'
    for enhancement in enhancements:
        section += (f'\n{enhancement.basic_suggestion}\n<b>Your answer:</b> {enhancement.source_text}\n'
                    f'<b>Enhanced answer:</b> {enhancement.enhanced_text}\n')
    return section


async def answer_parts_async_generator(answer: Result, competence: CompetenceEnum) -> T.AsyncGenerator[str, None]:
    overall_score = f'Your <b>IELTS</b> {competence} <b>score</b> is <b>{answer.overall_score}</b>'
    yield overall_score

    criteria_titles = [
        "Task Response",
        "Coherence and Cohesion",
        "Lexical Resource",
        "Grammatical Range and Accuracy"
    ]

    criteria_results = [
        answer.competence_results.task_achievement,
        answer.competence_results.fluency_coherence,
        answer.competence_results.lexical_resources,
        answer.competence_results.grammatical_range
    ]

    for title, result in zip(criteria_titles, criteria_results):
        if result is not None:
            section = await generate_section(title, result.score, result.enhancements)
            yield section
