import os
import markdown2

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


def markdown_to_html(md_path: str) -> str:
    """
    Convert a Markdown file to HTML string.

    Args:
        md_path (str): Path to the .md file.

    Returns:
        str: HTML content as string.
    """
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"{md_path} not found.")
    return markdown2.markdown_path(md_path)


def html_to_pdf(html_str: str, output_path: str) -> bool:
    """
    Convert HTML string to PDF file using WeasyPrint.

    Args:
        html_str (str): HTML content.
        output_path (str): Output .pdf path.

    Returns:
        bool: True if successful, False otherwise.
    """
    if not WEASYPRINT_AVAILABLE:
        print("[report_utils] WeasyPrint not installed — skipping PDF.")
        return False

    try:
        HTML(string=html_str).write_pdf(output_path)
        return True
    except Exception as e:
        print(f"[report_utils] PDF generation failed: {e}")
        return False


def convert_markdown_to_pdf(md_path: str, pdf_path: str) -> bool:
    """
    Wrapper to convert a Markdown file to a PDF.

    Args:
        md_path (str): Input Markdown path.
        pdf_path (str): Output PDF path.

    Returns:
        bool: True if PDF was generated, else False.
    """
    try:
        html_str = markdown_to_html(md_path)
        return html_to_pdf(html_str, pdf_path)
    except Exception as e:
        print(f"[report_utils] Conversion failed: {e}")
        return False
