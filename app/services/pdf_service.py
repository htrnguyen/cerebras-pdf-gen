import io
import re
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import xml.etree.ElementTree as ET

import os

try:
    current_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    regular_font_path = os.path.join(current_dir, "fonts", "SVN-Arial-Regular.ttf")
    bold_font_path = os.path.join(current_dir, "fonts", "SVN-Arial-Bold.ttf")

    pdfmetrics.registerFont(TTFont("SVN-Arial", regular_font_path))
    pdfmetrics.registerFont(TTFont("SVN-Arial-Bold", bold_font_path))
    default_font = "SVN-Arial"
    bold_font = "SVN-Arial-Bold"
except Exception as e:
    print(f"Warning: Could not load local fonts: {e}")
    try:
        pdfmetrics.registerFont(TTFont("Arial", "C:\\Windows\\Fonts\\arial.ttf"))
        pdfmetrics.registerFont(TTFont("Arial-Bold", "C:\\Windows\\Fonts\\arialbd.ttf"))
        default_font = "Arial"
        bold_font = "Arial-Bold"
    except:
        default_font = "Helvetica"
        bold_font = "Helvetica-Bold"


class PDFService:
    @staticmethod
    def create_pdf(output_path, markdown_text) -> bool:
        """Creates a PDF file from the generated markdown-like text using ReportLab Platypus.
        Outputs to the provided path or BytesIO buffer.
        """
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40,
            )

            styles = getSampleStyleSheet()
            custom_style = ParagraphStyle(
                "CustomStyle",
                parent=styles["Normal"],
                fontName=default_font,
                fontSize=12,
                leading=16,
                spaceAfter=10,
                alignment=0,
            )

            title_style = ParagraphStyle(
                "TitleStyle",
                parent=styles["Title"],
                fontName=bold_font,
                fontSize=18,
                spaceAfter=15,
                alignment=1,
            )

            heading_style = ParagraphStyle(
                "HeadingStyle",
                parent=styles["Heading2"],
                fontName=bold_font,
                fontSize=14,
                spaceBefore=10,
                spaceAfter=10,
                alignment=0,
            )

            story = []

            lines = markdown_text.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("# "):
                    story.append(Paragraph(line[2:], title_style))
                elif line.startswith("## "):
                    story.append(Paragraph(line[3:], heading_style))
                elif line.startswith("### "):
                    story.append(Paragraph(line[4:], heading_style))
                else:
                    # Hỗ trợ in đậm bằng font bold tốn tại
                    line = re.sub(r'\*\*(.*?)\*\*', rf'<font name="{bold_font}">\1</font>', line)
                    # Loại bỏ các kí tự markdown in nghiêng/in đậm thừa để text được trong sáng
                    line = re.sub(r'\*(.*?)\*', r'\1', line)
                    line = re.sub(r'__(.*?)__', rf'<font name="{bold_font}">\1</font>', line)
                    line = re.sub(r'_(.*?)_', r'\1', line)
                    
                    # Dọn dẹp nốt dấu # nếu AI lỡ rải rác
                    line = line.replace("### ", "").replace("## ", "")
                    
                    story.append(Paragraph(line, custom_style))

            def add_footer(canvas, doc):
                canvas.saveState()
                canvas.setFont(default_font, 9)
                canvas.setFillColorRGB(0.5, 0.5, 0.5)
                canvas.drawCentredString(
                    A4[0] / 2.0,
                    20,
                    "Nội dung được tạo bởi Cerebras Llama-3 70B. Vui lòng kiểm tra lại nội dung trước khi sử dụng.",
                )
                canvas.restoreState()

            doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
            return True
        except Exception as e:
            print(f"Error drawing PDF: {e}")
            return False
