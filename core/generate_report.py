import os
import uuid
from datetime import datetime
import markdown2
import hashlib

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

def sha1_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def build_report(sections: dict, output_dir: str = "data/reports") -> tuple[str, str]:
    """
    Build a research-style Markdown and PDF report from provided sections.

    Args:
        sections (dict): Dictionary containing report sections.
        output_dir (str): Directory where Markdown and PDF files will be saved.

    Returns:
        Tuple[str, str]: Paths to the Markdown and PDF files.
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    base_filename = f"report_{timestamp}_{unique_id}"
    md_path = os.path.join(output_dir, f"{base_filename}.md")
    pdf_path = os.path.join(output_dir, f"{base_filename}.pdf")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Automated Code Understanding Report\n\n")
        f.write(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("This report presents an automated analysis of source code using language models and static analysis tools.\n\n")

        if "Overview" in sections:
            f.write("## Abstract\n\n")
            f.write(sections["Overview"].strip() + "\n\n")

        if "Summary" in sections:
            f.write("## Methodology\n\n")
            for summary in sections["Summary"]:
                f.write(f"### Purpose\n\n{summary.get('purpose', '')}\n\n")
                f.write(f"### Structure\n\n{summary.get('structure', '')}\n\n")
                f.write(f"### Behavior\n\n{summary.get('behavior', '')}\n\n")

        if "Docstring" in sections:
            f.write("## Documentation Insights\n\n")
            for doc in sections["Docstring"]:
                f.write(f"### Inputs\n\n{doc.get('inputs', '')}\n\n")
                f.write(f"### Outputs\n\n{doc.get('outputs', '')}\n\n")
                f.write(f"### Intent\n\n{doc.get('intent', '')}\n\n")

        if "Code Quality" in sections:
            f.write("## Code Quality Evaluation\n\n")
            for qual in sections["Code Quality"]:
                f.write(f"**Linter:** {qual.get('tool', 'Unknown')}\n\n")
                f.write(f"**Score:** {qual.get('quality_score', 'N/A')}\n\n")
                f.write(f"**Issues Detected:** {qual.get('num_issues', 'N/A')}\n\n")

        f.write("## Conclusion\n\n")
        f.write("The system evaluated the provided codebase using pretrained models and linters. Results reveal documentation quality, design patterns, and maintainability signals useful for developers and stakeholders.\n")

    if WEASYPRINT_AVAILABLE:
        try:
            html = markdown2.markdown_path(md_path)
            HTML(string=html).write_pdf(pdf_path)
        except Exception as e:
            print(f"[WeasyPrint PDF error] {e}")
            pdf_path = None

    return md_path, pdf_path