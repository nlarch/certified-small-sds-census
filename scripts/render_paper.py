#!/usr/bin/env python3
"""Render the project note from its Markdown source using ReportLab."""

from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper" / "two_small_order_classifications.md"
OUTPUT = ROOT / "output" / "pdf" / "two_small_order_classifications.pdf"


def inline(text: str) -> str:
    value = escape(text)
    value = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    return value


def page_decor(canvas, document):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#B7BCC5"))
    canvas.setLineWidth(0.35)
    canvas.line(18 * mm, height - 15 * mm, width - 18 * mm, height - 15 * mm)
    canvas.setFillColor(colors.HexColor("#4B5563"))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(18 * mm, height - 11.8 * mm, "Two Small-Order Classification Theorems for Signed Difference Sets")
    canvas.drawRightString(width - 18 * mm, 10.5 * mm, str(document.page))
    canvas.restoreState()


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "PaperTitle", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=20, leading=24, alignment=TA_CENTER, textColor=colors.HexColor("#172554"),
            spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "Section", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=14, leading=17, textColor=colors.HexColor("#1E3A5F"),
            spaceBefore=5, spaceAfter=7,
        ),
        "h3": ParagraphStyle(
            "Subsection", parent=base["Heading3"], fontName="Helvetica-Bold",
            fontSize=11, leading=14, textColor=colors.HexColor("#334155"),
            spaceBefore=4, spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="Times-Roman",
            fontSize=9.4, leading=12.0, alignment=TA_JUSTIFY,
            textColor=colors.HexColor("#111827"), spaceAfter=5.2,
        ),
        "reference": ParagraphStyle(
            "Reference", parent=base["BodyText"], fontName="Times-Roman",
            fontSize=9.1, leading=11.5, alignment=TA_LEFT,
            textColor=colors.HexColor("#111827"), spaceAfter=4.5,
        ),
        "author": ParagraphStyle(
            "Author", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10, leading=14, alignment=TA_CENTER, spaceAfter=10,
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=base["BodyText"], fontName="Times-Roman",
            fontSize=9.3, leading=11.8, leftIndent=12, firstLineIndent=-7,
            alignment=TA_LEFT, spaceAfter=3,
        ),
        "code": ParagraphStyle(
            "Code", parent=base["Code"], fontName="Courier", fontSize=7.7,
            leading=9.7, leftIndent=8, rightIndent=8, textColor=colors.HexColor("#1F2937"),
            backColor=colors.HexColor("#F1F5F9"), borderPadding=6, spaceBefore=2, spaceAfter=6,
        ),
        "table": ParagraphStyle(
            "TableText", parent=base["BodyText"], fontName="Helvetica",
            fontSize=6.4, leading=7.7, alignment=TA_LEFT,
        ),
    }


def parse_table(lines, style):
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append([Paragraph(inline(cell), style) for cell in cells])
    widths = [None] * len(rows[0])
    if len(widths) == 3:
        widths = [42 * mm, 31 * mm, 101 * mm]
    elif len(widths) == 4:
        widths = [41 * mm, 43 * mm, 48 * mm, 33 * mm]
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#172554")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#94A3B8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    return table


def build_story(text: str):
    style = styles()
    story = []
    lines = text.splitlines()
    paragraph = []
    index = 0
    first_heading = True
    in_references = False

    def flush():
        if paragraph:
            joined = " ".join(item.strip() for item in paragraph)
            chosen = style["author"] if first_heading else (style["reference"] if in_references else style["body"])
            story.append(Paragraph(inline(joined).replace("  ", "<br/>"), chosen))
            paragraph.clear()

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped == "<!-- pagebreak -->":
            flush()
            story.append(PageBreak())
            index += 1
            continue
        if stripped.startswith("```"):
            flush()
            code = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code.append(lines[index])
                index += 1
            story.append(Preformatted("\n".join(code), style["code"]))
            index += 1
            continue
        if stripped.startswith("|"):
            flush()
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            story.append(parse_table(table_lines, style["table"]))
            story.append(Spacer(1, 5))
            continue
        if stripped.startswith("# "):
            flush()
            story.append(Spacer(1, 28))
            story.append(Paragraph(inline(stripped[2:]), style["title"]))
            first_heading = True
            index += 1
            continue
        if stripped.startswith("## "):
            flush()
            story.append(Paragraph(inline(stripped[3:]), style["h2"]))
            first_heading = False
            in_references = stripped[3:] == "References"
            index += 1
            continue
        if stripped.startswith("### "):
            flush()
            story.append(Paragraph(inline(stripped[4:]), style["h3"]))
            first_heading = False
            index += 1
            continue
        if stripped.startswith("- "):
            flush()
            story.append(Paragraph(inline(stripped[2:]), style["bullet"], bulletText="-"))
            index += 1
            continue
        if not stripped:
            flush()
            index += 1
            continue
        paragraph.append(line)
        index += 1
    flush()
    return story


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = BaseDocTemplate(
        str(OUTPUT), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=19 * mm, bottomMargin=17 * mm,
        title="Two Small-Order Classification Theorems for Signed Difference Sets",
        author="Nicolas Masselot", subject="Certified signed difference set classifications",
    )
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="main")
    document.addPageTemplates([PageTemplate(id="paper", frames=[frame], onPage=page_decor)])
    document.build(build_story(SOURCE.read_text()))
    print(OUTPUT)


if __name__ == "__main__":
    main()
