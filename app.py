import warnings
import logging
warnings.filterwarnings("ignore", category=RuntimeWarning)
logging.getLogger('py.warnings').setLevel(logging.ERROR)

import sys
import types

# ✅ Final fix: Patch torch.classes to avoid Streamlit watcher crash
import torch
class FakePath(types.SimpleNamespace):
    _path = []
try:
    torch.classes.__path__ = FakePath()
except Exception:
    pass

import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
from streamlit.runtime.caching import cache_resource

from utils.config import MODEL_PATHS, REPORT_DIR
from utils.logger import get_logger
from core.language_detect import detect_language
from core.parser import extract_code_snippets
from core.summarizer import generate_summary
from core.doc_generator import generate_docstring
from core.code_quality import run_code_quality
from core.github_fetcher import fetch_python_and_js_files_from_repo
from report_builder.generate_report import build_report
from report_builder.section_writer import (
    format_summary_blocks, format_docstring_blocks, format_quality_result
)

logger = get_logger("app")

st.set_page_config(page_title="CodeDocGen", layout="wide")
st.title("🧠 Code Documentation & Report Generator")

# Sidebar UI
model_choice = st.sidebar.selectbox("Choose Model", list(MODEL_PATHS.keys()))
model_path = MODEL_PATHS[model_choice]
mode = st.sidebar.radio("Input Mode", ["Paste Code", "GitHub Repo"])

# Load model with cache
from main import load_doc_model

@cache_resource
def get_cached_model(path):
    return load_doc_model(path)

model_result = get_cached_model(model_path)
if model_result is None:
    st.error("⚠️ Failed to load model. Check model path or weights.")
    st.stop()

tokenizer, model = model_result

def display_quality_issues(quality_result: dict):
    st.error("⚠️ Code issues detected. Please review before generating full report.")
    st.markdown(f"**Tool:** `{quality_result['tool']}`")
    st.markdown(f"**Issues:** {quality_result['num_issues']}")
    st.code(quality_result['raw_output'], language="text")
    st.stop()

def process_code_blocks(code_snippets, full_code_text, language, model_choice):
    quality_result = run_code_quality(full_code_text, language)
    if quality_result["num_issues"] > 0 or "[AST Parse Error]" in quality_result["raw_output"]:
        display_quality_issues(quality_result)

    summaries = generate_summary(code_snippets, tokenizer, model, model_choice)
    docstrings = generate_docstring(code_snippets, tokenizer, model, model_choice)

    if not any(s.strip() for s in summaries) and not any(d.strip() for d in docstrings):
        st.warning("⚠️ No meaningful summary or docstring output from model.")
        st.stop()

    sections = {
        "Summary": format_summary_blocks(summaries),
        "Docstring": format_docstring_blocks(docstrings),
        "Code Quality": format_quality_result([quality_result])
    }

    md_path, pdf_path = build_report(sections, output_dir=REPORT_DIR)
    return summaries, docstrings, quality_result, md_path, pdf_path

# Paste Code Mode
if mode == "Paste Code":
    st.subheader("Paste your code below:")
    code_input = st.text_area("Your code", height=300)

    if st.button("🔍 Generate Report"):
        if not code_input.strip():
            st.warning("Please paste some code.")
            st.stop()

        language = detect_language(code_input)
        if language == "unknown":
            st.error("Language not supported. Only Python and JavaScript are allowed.")
            st.stop()

        quality_result = run_code_quality(code_input, language)
        if quality_result["num_issues"] > 0 and "[AST Parse Error]" in quality_result["raw_output"]:
            display_quality_issues(quality_result)

        snippets = extract_code_snippets(code_input, language)
        if not snippets:
            snippets = [code_input.strip()]  # fallback to full script

        st.success(f"Language detected: {language.capitalize()} — {len(snippets)} block(s) found.")
        st.info("Analyzing code blocks...")

        summaries, docstrings, quality_result, md_path, pdf_path = process_code_blocks(
            snippets, code_input, language, model_choice
        )

        with st.expander("📚 Summary"):
            for s in summaries:
                st.markdown(f"- {s}")

        with st.expander("📋 Docstring"):
            for d in docstrings:
                st.markdown(f"- {d}")

        with st.expander("📉 Code Quality"):
            st.markdown(f"**Tool:** `{quality_result['tool']}`")
            st.markdown(f"**Issues:** {quality_result['num_issues']}")

        st.markdown("---")
        st.success("✅ Report generated!")
        with open(md_path, "r", encoding="utf-8") as f:
            st.download_button("📅 Download Markdown", f, file_name=os.path.basename(md_path))
        if pdf_path:
            with open(pdf_path, "rb") as f:
                st.download_button("📄 Download PDF", f, file_name=os.path.basename(pdf_path))

# GitHub Repo Mode
if mode == "GitHub Repo":
    st.subheader("Enter a GitHub Repository URL:")
    repo_url = st.text_input("GitHub URL")

    if st.button("🖱 Fetch and Generate Report"):
        if not repo_url.strip():
            st.warning("Please enter a valid GitHub repo URL.")
            st.stop()

        code_files = fetch_python_and_js_files_from_repo(repo_url)
        if not code_files:
            st.error("No .py/.js/.ipynb code files found in the repo.")
            st.stop()

        full_code = "\n\n".join(code_files)
        detected_lang = detect_language(full_code)
        if detected_lang == "unknown":
            st.error("Language not supported.")
            st.stop()

        code_snippets = []
        for code in code_files:
            code_snippets.extend(extract_code_snippets(code, detected_lang))

        if not code_snippets:
            code_snippets = [full_code.strip()]  # fallback for script-style code

        st.success(f"Detected {len(code_snippets)} code block(s) in {detected_lang.title()}.")

        summaries, docstrings, quality_result, md_path, pdf_path = process_code_blocks(
            code_snippets, full_code, detected_lang, model_choice
        )

        with st.expander("📚 Summary"):
            for s in summaries:
                st.markdown(f"- {s}")

        with st.expander("📋 Docstring"):
            for d in docstrings:
                st.markdown(f"- {d}")

        with st.expander("📉 Code Quality"):
            st.markdown(f"**Tool:** `{quality_result['tool']}`")
            st.markdown(f"**Issues:** {quality_result['num_issues']}")

        st.markdown("---")
        st.success("✅ Report generated!")
        with open(md_path, "r", encoding="utf-8") as f:
            st.download_button("📅 Download Markdown", f, file_name=os.path.basename(md_path))
        if pdf_path:
            with open(pdf_path, "rb") as f:
                st.download_button("📄 Download PDF", f, file_name=os.path.basename(pdf_path))

st.markdown("---")
st.caption("Developed for BDA Project | Models: DeepSeek, CodeT5p")
