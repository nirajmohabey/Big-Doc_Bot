import os
import uuid
from datetime import datetime
import hashlib
import markdown2

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


def sha1_hash(text: str) -> str:
    """Generate SHA1 hash of text (can be used for caching later)."""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def build_report(sections: dict, output_dir: str = "data/reports") -> tuple[str, str | None]:
    """
    Build a Markdown + optional PDF report.

    Args:
        sections (dict): Dictionary with keys like 'Overview', 'Summary', 'Docstring', 'Code Quality'.
        output_dir (str): Folder to save Markdown and PDF reports.

    Returns:
        Tuple[str, str|None]: (Markdown path, PDF path or None)
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    base_name = f"report_{timestamp}_{unique_id}"
    md_path = os.path.join(output_dir, f"{base_name}.md")
    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Code Understanding Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("This report presents automated insights based on large language models and code analysis tools.\n\n")

        # Abstract (if available)
        if "Overview" in sections:
            f.write("## Abstract\n\n")
            f.write(sections["Overview"].strip() + "\n\n")

        # Summary
        if "Summary" in sections:
            f.write("## Methodology\n\n")
            for i, block in enumerate(sections["Summary"]):
                f.write(f"### Block {i+1}\n\n")
                f.write("**Summary**\n\n")
                f.write(f"{block.get('summary', '').strip()}\n\n")

        # Docstring Section
        if "Docstring" in sections:
            f.write("## Documentation Insights\n\n")
            for i, block in enumerate(sections["Docstring"]):
                f.write(f"### Block {i+1}\n\n")
                f.write("**Summary**\n\n")
                f.write(f"{block.get('summary', '').strip()}\n\n")

        # Code Quality Section
        if "Code Quality" in sections:
            f.write("## Code Quality Evaluation\n\n")
            for result in sections["Code Quality"]:
                f.write(f"**Tool:** `{result.get('tool', 'unknown')}`  \n")
                f.write(f"**Issues:** {result.get('num_issues', 'N/A')}\n\n")
                if result.get("raw_output"):
                    f.write("```text\n")
                    f.write(f"{result['raw_output'].strip()}\n")
                    f.write("```\n\n")

        # Conclusion
        f.write("## Conclusion\n\n")
        f.write("This automated evaluation synthesizes code understanding, docstring quality, and static analysis results. It assists developers with code maintenance, onboarding, and overall clarity of complex systems.\n")

    # Optional PDF
    if WEASYPRINT_AVAILABLE:
        try:
            html = markdown2.markdown_path(md_path)
            HTML(string=html).write_pdf(pdf_path)
        except Exception as e:
            print(f"[WeasyPrint PDF Error] {e}")
            pdf_path = None
    else:
        pdf_path = None

    return md_path, pdf_path