from app.infrastructure.config.settings import settings
from app.adapters.outbound.ai.whisper.whisper_adapter import WhisperAdapter
from app.adapters.outbound.ai.grpc.grpc_adapter import GrpcAdapter
from app.adapters.outbound.export.pdf_adapter import PDFAdapter
from app.adapters.outbound.tracking.mlflow_adapter import MLflowAdapter
from app.adapters.outbound.auth.jwt_provider import JWTProvider
from app.adapters.outbound.persistence.repositories.in_memory_user_repository import InMemoryUserRepository
from app.domain.ports.inbound.audio_ports import IAnalyzeAudioUseCase, IExportPDFUseCase
from app.domain.ports.inbound.auth_ports import ILoginUseCase, IRefreshTokenUseCase
from app.domain.ports.outbound.providers.metrics_provider import IMetricsProvider
from app.domain.ports.outbound.providers.health_provider import IHealthProvider
from app.domain.use_cases.analyze_audio import AnalyzeAudioUseCase
from app.domain.use_cases.export_pdf import ExportPDFUseCase
from app.domain.use_cases.login import LoginUseCase
from app.domain.use_cases.refresh_token import RefreshTokenUseCase

def get_analyze_audio_use_case() -> IAnalyzeAudioUseCase:
    return AnalyzeAudioUseCase(
        transcriber=WhisperAdapter(),
        analyzer=GrpcAdapter(),
        tracker=MLflowAdapter(),
        whisper_model=settings.WHISPER_MODEL,
        flan_model=settings.FLAN_T5_MODEL,
    )

def get_export_pdf_use_case() -> IExportPDFUseCase:
    return ExportPDFUseCase(generator=PDFAdapter())

def get_metrics_provider() -> IMetricsProvider:
    return MLflowAdapter()

def get_health_provider() -> IHealthProvider:
    return GrpcAdapter()

def get_login_use_case() -> ILoginUseCase:
    return LoginUseCase(
        user_repo=InMemoryUserRepository(),
        auth_provider=JWTProvider(),
    )

def get_refresh_token_use_case() -> IRefreshTokenUseCase:
    return RefreshTokenUseCase(auth_provider=JWTProvider())
