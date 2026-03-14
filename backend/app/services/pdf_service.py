"""
VoxIA PDF Service — Generación de reportes con ReportLab
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from io import BytesIO
from datetime import datetime


# ─── Paleta de colores ────────────────────────────────────────────────────────
VIOLET     = colors.HexColor("#7c3aed")
INDIGO     = colors.HexColor("#4f46e5")
EMERALD    = colors.HexColor("#059669")
AMBER      = colors.HexColor("#d97706")
BLUE       = colors.HexColor("#2563eb")
DARK_BG    = colors.HexColor("#0f0f23")
LIGHT_GREY = colors.HexColor("#f3f4f6")
MID_GREY   = colors.HexColor("#6b7280")
DARK_TEXT  = colors.HexColor("#111827")
BODY_TEXT  = colors.HexColor("#374151")


def _make_styles():
    base = getSampleStyleSheet()

    title = ParagraphStyle(
        "VoxTitle",
        parent=base["Normal"],
        fontSize=22,
        fontName="Helvetica-Bold",
        textColor=DARK_TEXT,
        spaceAfter=4,
        leading=28,
    )
    subtitle = ParagraphStyle(
        "VoxSubtitle",
        parent=base["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=MID_GREY,
        spaceAfter=0,
    )
    section_header = ParagraphStyle(
        "VoxSection",
        parent=base["Normal"],
        fontSize=12,
        fontName="Helvetica-Bold",
        textColor=DARK_TEXT,
        spaceBefore=14,
        spaceAfter=6,
        leading=16,
    )
    body = ParagraphStyle(
        "VoxBody",
        parent=base["Normal"],
        fontSize=9.5,
        fontName="Helvetica",
        textColor=BODY_TEXT,
        leading=15,
        spaceAfter=4,
    )
    bullet_item = ParagraphStyle(
        "VoxBullet",
        parent=base["Normal"],
        fontSize=9.5,
        fontName="Helvetica",
        textColor=BODY_TEXT,
        leading=15,
        leftIndent=14,
        spaceAfter=3,
        bulletIndent=0,
    )
    mono = ParagraphStyle(
        "VoxMono",
        parent=base["Normal"],
        fontSize=8.5,
        fontName="Courier",
        textColor=colors.HexColor("#4b5563"),
        leading=13,
        spaceAfter=2,
    )
    caption = ParagraphStyle(
        "VoxCaption",
        parent=base["Normal"],
        fontSize=8,
        fontName="Helvetica",
        textColor=MID_GREY,
        leading=12,
    )
    return {
        "title": title,
        "subtitle": subtitle,
        "section_header": section_header,
        "body": body,
        "bullet": bullet_item,
        "mono": mono,
        "caption": caption,
    }


def _section_block(label: str, color, styles, elements):
    """Añade un bloque de sección con línea de color."""
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=color, spaceAfter=4))
    elements.append(Paragraph(label, styles["section_header"]))


def _meta_table(data: list[tuple[str, str]], styles):
    """Tabla de metadatos en dos columnas."""
    table_data = []
    for i in range(0, len(data), 2):
        row = []
        for k, v in data[i:i+2]:
            row.append(Paragraph(f"<b>{k}:</b> {v}", styles["caption"]))
        if len(row) == 1:
            row.append(Paragraph("", styles["caption"]))
        table_data.append(row)

    t = Table(table_data, colWidths=["50%", "50%"])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY),
        ("ROUNDEDCORNERS", [4]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def generate_pdf_report(
    file_name: str,
    language: str,
    duration_seconds: float,
    processing_time_seconds: float,
    transcript: str,
    summary: str,
    key_points: list[str],
    tasks: list[str],
    decisions: list[str],
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2.2*cm,
        bottomMargin=2*cm,
        title=f"VoxIA - Reporte: {file_name}",
        author="VoxIA Sistema de IA",
    )

    styles = _make_styles()
    elements = []

    # ── Encabezado ────────────────────────────────────────────────────────────
    elements.append(Paragraph("🎙 VoxIA", styles["title"]))
    elements.append(Paragraph("Reporte de Análisis Inteligente de Audio", styles["subtitle"]))
    elements.append(Spacer(1, 10))

    # Metadata
    def fmt_dur(s):
        if s < 60: return f"{round(s)}s"
        return f"{int(s//60)}m {round(s%60)}s"

    meta = [
        ("Archivo", file_name),
        ("Generado", datetime.now().strftime("%d/%m/%Y %H:%M")),
        ("Idioma", "Español" if language == "es" else "English"),
        ("Duración del audio", fmt_dur(duration_seconds)),
        ("Tiempo de procesamiento", fmt_dur(processing_time_seconds)),
        ("Modelos utilizados", "Whisper Base + FLAN-T5 Base"),
    ]
    elements.append(_meta_table(meta, styles))
    elements.append(Spacer(1, 8))

    # ── Resumen ejecutivo ─────────────────────────────────────────────────────
    _section_block("📋  Resumen Ejecutivo", BLUE, styles, elements)
    if summary:
        elements.append(Paragraph(summary, styles["body"]))
    else:
        elements.append(Paragraph("Sin resumen disponible.", styles["body"]))

    # ── Puntos clave ──────────────────────────────────────────────────────────
    _section_block("🔑  Puntos Clave", INDIGO, styles, elements)
    if key_points:
        for i, point in enumerate(key_points, 1):
            elements.append(Paragraph(f"{i}.  {point}", styles["bullet"]))
    else:
        elements.append(Paragraph("No se identificaron puntos clave.", styles["body"]))

    # ── Tareas y compromisos ──────────────────────────────────────────────────
    _section_block("✅  Tareas y Compromisos", EMERALD, styles, elements)
    if tasks:
        for task in tasks:
            elements.append(Paragraph(f"▸  {task}", styles["bullet"]))
    else:
        elements.append(Paragraph("No se identificaron tareas o compromisos.", styles["body"]))

    # ── Decisiones ────────────────────────────────────────────────────────────
    _section_block("⚖️  Decisiones Tomadas", AMBER, styles, elements)
    if decisions:
        for dec in decisions:
            elements.append(Paragraph(f"→  {dec}", styles["bullet"]))
    else:
        elements.append(Paragraph("No se identificaron decisiones.", styles["body"]))

    # ── Transcripción completa ────────────────────────────────────────────────
    _section_block("📝  Transcripción Completa", VIOLET, styles, elements)
    if transcript:
        # Dividir en párrafos para que ReportLab pueda paginar correctamente
        paragraphs = [p.strip() for p in transcript.split("\n") if p.strip()]
        for para in paragraphs:
            # Escapar caracteres especiales XML
            safe = para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            elements.append(Paragraph(safe, styles["mono"]))
    else:
        elements.append(Paragraph("Sin transcripción disponible.", styles["body"]))

    # ── Pie de página (nota) ──────────────────────────────────────────────────
    elements.append(Spacer(1, 16))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb")))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        "Generado automáticamente por VoxIA · Universidad Autónoma de Occidente · "
        "Los resultados son generados por modelos de IA y pueden contener imprecisiones.",
        styles["caption"]
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
