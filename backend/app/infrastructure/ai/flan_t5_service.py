from transformers import pipeline

from app.domain.entities.meeting import MeetingAnalysis, Transcription
from app.domain.interfaces.summarization_service import ISummarizationService

_FLAN_T5_MODEL = "google/flan-t5-base"

# flan-t5-base supports up to 512 tokens; ~1.3 chars/token → ~390 words safe limit
_MAX_INPUT_WORDS = 350


class FlanT5SummarizationService(ISummarizationService):
    """
    Summarization service backed by Google Flan-T5 (base) via HuggingFace Transformers.

    Performs two inference passes:
    1. General meeting summary.
    2. Extraction of action items / tasks.

    Both results are combined into a single MeetingAnalysis entity.
    """

    def __init__(self) -> None:
        self._pipeline = pipeline(
            task="text2text-generation",
            model=_FLAN_T5_MODEL,
        )

    def summarize(self, transcription: Transcription) -> MeetingAnalysis:
        truncated_text = self._truncate(transcription.text)

        summary = self._generate_summary(truncated_text)
        tasks = self._extract_tasks(truncated_text)

        combined = f"{summary}\n\nTareas y puntos de acción:\n{tasks}"

        return MeetingAnalysis(
            transcription=transcription.text,
            summary=combined,
        )

    def _generate_summary(self, text: str) -> str:
        prompt = (
            "Summarize the following meeting transcript highlighting the most "
            "important discussion points and decisions made:\n\n"
            f"{text}"
        )
        result = self._pipeline(prompt, max_new_tokens=256, do_sample=False)
        return result[0]["generated_text"].strip()  # type: ignore[index]

    def _extract_tasks(self, text: str) -> str:
        prompt = (
            "Extract all action items, pending tasks, and commitments mentioned "
            "in the following meeting transcript as a numbered list:\n\n"
            f"{text}"
        )
        result = self._pipeline(prompt, max_new_tokens=256, do_sample=False)
        return result[0]["generated_text"].strip()  # type: ignore[index]

    @staticmethod
    def _truncate(text: str) -> str:
        words = text.split()
        if len(words) <= _MAX_INPUT_WORDS:
            return text
        return " ".join(words[:_MAX_INPUT_WORDS]) + " [...]"
