from app.domain.ports.inbound.audio_ports import IExportPDFUseCase
from app.domain.entities.audio_analysis import ReportData
from app.domain.ports.outbound.providers.export_provider import IExportProvider

class ExportPDFUseCase(IExportPDFUseCase):
    def __init__(self, generator: IExportProvider):
        self._generator = generator

    def execute(self, data: ReportData) -> bytes:
        return self._generator.generate(data)
