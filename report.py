from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def create_report(summary,path="InsightRAG_Report.pdf"):

    doc=SimpleDocTemplate(path)

    styles=getSampleStyleSheet()

    story=[Paragraph(
        "<b>InsightRAG Report</b>",
        styles["Heading1"]
    )]

    for k,v in summary.items():

        story.append(
            Paragraph(f"{k}: {v}",styles["BodyText"])
        )

    doc.build(story)

    return path