# Code Understanding Report

**Generated on:** {{ generated_on }}

This report presents an automated understanding of the provided source code using LLMs and static analysis tools. The structure below outlines key findings across summarization, documentation, and quality metrics.

---

## Abstract

{{ overview }}

---

## Methodology

{% for block in summary %}
### Block {{ loop.index }}

**Summary**

{{ block.summary }}

{% endfor %}

---

## Documentation Insights

{% for block in docstring %}
### Block {{ loop.index }}

**Summary**

{{ block.summary }}

{% endfor %}

---

## Code Quality Evaluation

{% for result in code_quality %}
**Tool:** {{ result.tool }}

**Issues Detected:** {{ result.num_issues }}

{% endfor %}

---

## Conclusion

This automated evaluation synthesizes insights about your code's purpose, structure, and quality to assist with maintainability, onboarding, and documentation.
