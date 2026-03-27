from app.domain.entities.audio_analysis import AnalysisResult
from app.domain.ports.outbound.providers.summarization_provider import ISummarizationProvider
from app.domain.ports.outbound.providers.health_provider import IHealthProvider
from app.grpc_service.grpc_client import analyze_text_via_grpc, health_check_grpc

class GrpcAdapter(ISummarizationProvider, IHealthProvider):
    def analyze(self, text: str, language: str) -> AnalysisResult:
        result = analyze_text_via_grpc(text, language)
        return AnalysisResult(
            summary=result["summary"],
            key_points=result["key_points"],
            tasks=result["tasks"],
            decisions=result["decisions"],
            via_grpc=result.get("via_grpc", False),
        )

    def is_healthy(self) -> bool:
        return health_check_grpc()
