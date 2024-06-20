import typing as T  # noqa

from src.libs.factories.gpt.models.result import Result
from src.libs.factories.gpt.models.suggestion import Enhancement


async def generate_section(title: str, score: float, enhancements: T.List[Enhancement]) -> str:
    section = f'<b>{title}</b> - {score}'
    if not enhancements:
        return section + '\n\nThere are no enhancements for this section.'
    section += '\n\nThere are some enhancements that you can apply:\n'
    for enhancement in enhancements:
        section += (f'\n{enhancement.basic_suggestion}\n<b>You wrote:</b> {enhancement.source_text}\n'
                    f'<b>Enhanced answer:</b> {enhancement.enhanced_text}\n')
    return section


async def answer_parts_async_generator(answer: Result) -> T.AsyncGenerator[str, None]:
    overall_score = f'Your <b>IELTS</b> writing <b>score</b> is <b>{answer.overall_score}</b>'
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
