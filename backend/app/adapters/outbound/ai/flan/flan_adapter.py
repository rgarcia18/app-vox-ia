"""
VoxIA FLAN Adapter — Análisis NLP con FLAN-T5
"""
import re
from app.domain.entities.audio_analysis import AnalysisResult
from app.domain.ports.outbound.providers.summarization_provider import ISummarizationProvider
from app.infrastructure.config.settings import settings

_flan_tokenizer = None
_flan_model = None


def _load_flan():
    global _flan_tokenizer, _flan_model
    if _flan_model is None:
        print("⏳ Cargando FLAN-T5...")
        from transformers import T5ForConditionalGeneration, T5Tokenizer
        _flan_tokenizer = T5Tokenizer.from_pretrained(settings.FLAN_T5_MODEL)
        _flan_model = T5ForConditionalGeneration.from_pretrained(settings.FLAN_T5_MODEL)
        print(f"✅ FLAN-T5 '{settings.FLAN_T5_MODEL}' listo")
    return _flan_tokenizer, _flan_model


def _parse_list(raw: str) -> list[str]:
    items = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        cleaned = re.sub(r'^[\d]+[.)]\s*|^[-•*]\s*', '', line).strip()
        if cleaned and len(cleaned) > 4:
            items.append(cleaned)
    return items


def _run_flan(prompt: str, max_new_tokens: int = 150) -> str:
    tokenizer, model = _load_flan()
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        max_length=512,
        truncation=True,
    )
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        num_beams=4,
        early_stopping=True,
        no_repeat_ngram_size=3,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()


def _truncate(text: str, max_chars: int = 1200) -> str:
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    last_period = cut.rfind(".")
    return cut[:last_period + 1] if last_period > max_chars // 2 else cut


def _is_bad_output(text: str) -> bool:
    bad_starts = [
        "resume ", "resumir", "summarize", "list ", "lista ", "extrae",
        "escribe un", "write a", "genera ", "generate"
    ]
    low = text.lower().strip()
    return any(low.startswith(b) for b in bad_starts)


def generate_summary(text: str, language: str = "es") -> str:
    if not text or len(text.strip()) < 30:
        return "El audio es demasiado corto para generar un resumen."
    truncated = _truncate(text, 1200)
    if language == "en":
        prompt = f"Summarize this text in 3 sentences: {truncated}"
    else:
        prompt = f"Resume este texto en 3 oraciones: {truncated}"
    result = _run_flan(prompt, max_new_tokens=150)
    if _is_bad_output(result) or len(result) < 10:
        return "No se pudo generar un resumen automático para este audio."
    return result


def extract_key_points(text: str, language: str = "es") -> list[str]:
    if not text or len(text.strip()) < 30:
        return []
    truncated = _truncate(text, 1000)
    if language == "en":
        prompt = f"List 3 key points from this text:\n{truncated}\n\n1."
    else:
        prompt = f"Lista 3 puntos importantes de este texto:\n{truncated}\n\n1."
    raw = "1." + _run_flan(prompt, max_new_tokens=200)
    result = _parse_list(raw)
    result = [r for r in result if len(r) > 10 and not _is_bad_output(r)]
    return result[:5]


def extract_tasks(text: str, language: str = "es") -> list[str]:
    if not text or len(text.strip()) < 30:
        return []
    truncated = _truncate(text, 1000)
    if language == "en":
        prompt = f"List all tasks and action items mentioned in this text:\n{truncated}\n\n1."
    else:
        prompt = f"Lista todas las tareas y compromisos mencionados en este texto:\n{truncated}\n\n1."
    raw = "1." + _run_flan(prompt, max_new_tokens=200)
    result = _parse_list(raw)
    result = [r for r in result if len(r) > 10 and not _is_bad_output(r)]
    return result


def extract_decisions(text: str, language: str = "es") -> list[str]:
    if not text or len(text.strip()) < 30:
        return []
    truncated = _truncate(text, 1000)
    if language == "en":
        prompt = f"List all decisions made in this text:\n{truncated}\n\n1."
    else:
        prompt = f"Lista todas las decisiones tomadas en este texto:\n{truncated}\n\n1."
    raw = "1." + _run_flan(prompt, max_new_tokens=200)
    result = _parse_list(raw)
    result = [r for r in result if len(r) > 10 and not _is_bad_output(r)]
    return result


class FlanAdapter(ISummarizationProvider):
    def analyze(self, text: str, language: str) -> AnalysisResult:
        return AnalysisResult(
            summary=generate_summary(text, language),
            key_points=extract_key_points(text, language),
            tasks=extract_tasks(text, language),
            decisions=extract_decisions(text, language),
            via_grpc=False,
        )
