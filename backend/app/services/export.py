from io import BytesIO

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

from app.models.draft import DraftOutput


def draft_to_docx(draft: DraftOutput, court_name: str, proceeding_name: str) -> bytes:
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(f"IN THE {court_name.upper()}")
    run.bold = True

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run(proceeding_name.upper()).bold = True
    doc.add_paragraph()

    for section in draft.sections:
        heading = doc.add_paragraph()
        heading.add_run(section.heading).bold = True
        for block in section.blocks:
            doc.add_paragraph(block.text)
        doc.add_paragraph()

    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
