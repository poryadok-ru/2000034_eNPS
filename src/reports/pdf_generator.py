import markdown
import pdfkit

class PDFGenerator:
    @staticmethod
    def md_to_pdf(md_text, pdf_path, wkhtmltopdf_path):
        try:
            html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
            html = f"""<html>
            <head>
                <meta charset='utf-8'>
                <style>
                    body {{ font-family: Arial; margin: 40px; line-height: 1.5; font-size: 13px; }}
                    h1, h2 {{ color: #1a588b; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                    th, td {{ border: 1px solid #ccc; padding: 8px; }}
                    th {{ background: #f5f5f5; }}
                    .positive {{ color: green; }}
                    .negative {{ color: #cc0000; }}
                </style>
            </head>
            <body>{html_content}</body>
            </html>"""

            config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
            pdfkit.from_string(html, str(pdf_path), configuration=config)

        except Exception as e:
            raise e