# 🚀 BigDocBot

BigDocBot is an AI-powered tool to automatically generate summaries, docstrings, and code quality reports for Python and JavaScript codebases. It uses advanced LLMs (DeepSeek-Coder, CodeT5+) and integrates seamlessly with both pasted code and real GitHub repositories.  
It outputs professional PDF reports combining code analysis and AI-generated documentation, making it perfect for developers, documentation teams, and technical audits.

---

## 💻 Features

- **Streamlit Web App** → Clean, interactive UI.
- **Model Selection** → Choose between lightweight (CodeT5+) or advanced (DeepSeek) LLMs.
- **Two Modes:**
  - **Paste Code** → Analyze any code snippet directly.
  - **GitHub Repo** → Analyze entire repositories (.py, .js, .ipynb files).
- **Static Code Analysis:**
  - Python → `pylint`
  - JavaScript → `eslint`
- **AI-Generated Outputs:**
  - Code summaries
  - Docstring generation
- **PDF Reports** → Export beautifully structured reports.
- **Optimizations:**
  - AMP (mixed precision)
  - Batching
  - 8-bit quantization (for DeepSeek)

---

## 📂 Project Structure

```
BigDocBot/
│
├── app.py
├── main.py
├── run_training_pipeline.py
├── requirements.txt
├── core/
│   ├── parser.py
│   ├── summarizer.py
│   ├── doc_generator.py
│   ├── language_detect.py
│   ├── code_quality.py
│   └── ...
├── ingest/
├── logs/
├── output/
├── report_builder/
│   ├── generate_report.py
│   └── ...
├── scripts/
├── train/
├── utils/
│   ├── config.py
│   ├── logger.py
│   └── ...
├── .eslintrc
└── .gitattributes
```

**Note:**
- `data/` → automatically created via scripts (not uploaded to GitHub).
- `models/` → Download from Google Drive link provided below.

---

## 🔗 Model Download

Download the trained models from this Google Drive link:  
➡️ [Google Drive Models Folder](https://drive.google.com/drive/folders/1fI3KLGIFVfyXzfNSl0_kX1LSgzFOcKow?usp=sharing)

After download, place the entire `models/` folder inside the root of the project directory.

---

## ⚙️ Installation

Create a virtual environment (optional but recommended):

```bash
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

Install Python requirements:

```bash
pip install -r requirements.txt
```

---

## ✅ How to Run the Project

Here’s the step-by-step flow:

### 1. Download Models

- Download the trained models from Google Drive.
- Place the downloaded `models/` folder inside your project root.

### 2. Generate Data (Optional)

If you want to extract fresh GitHub repos:

```bash
python run_training_pipeline.py
```

This will:
- Fetch code from GitHub repos.
- Create JSON datasets in `data/`.

### 3. Run the Web App

Launch Streamlit:

```bash
streamlit run app.py
```

This starts the BigDocBot UI.

### 4. Use the App

- **Paste Code** → Paste any Python/JS code snippet and generate reports.
- **GitHub Repo** → Enter a GitHub URL. The tool:
  - Clones the repo.
  - Detects files.
  - Runs static analysis + AI summarization.
  - Generates PDF reports.

Reports are saved in the `output/` folder.

---

## 🔍 Example Usage

### Paste Code Example

- Paste your Python or JavaScript code into the UI.
- Click “Generate Report”.
- Download the PDF report from the app.

---

### GitHub Repo Example

- Enter a public GitHub repo URL (e.g. `https://github.com/user/repo`).
- Wait for analysis.
- Download the combined PDF report.

---

## 🧪 Training Details

- Used CodeSearchNet and custom GitHub corpus as datasets.
- Fine-tuned LLMs with:
  - Transfer learning
  - AMP
  - Gradient checkpointing
  - 8-bit quantization (for DeepSeek)

---

## 🚀 Tech Stack

- Python
- Streamlit
- Hugging Face Transformers
- PyTorch
- Pylint / ESLint
- PDF Generation (markdown2 + WeasyPrint)

---

## 🙌 Authors

- Niraj Mohabey
- Manaswi Kulkarni
- Mansi Mantri
- Vaibhav Chavan

⭐ **Star this repo if you find it helpful!**

---

## 🔗 Quick Start Commands

If you just want to run the app quickly:

```bash
pip install -r requirements.txt
streamlit run app.py
```

That’s it. Happy coding!
