import gradio as gr
from bioscore import reproducibility, data_quality, model_readiness
import tempfile
import os


def check_reproducibility(file):
    if file is None:
        return "Please upload a .ipynb or .py file"
    result = reproducibility(file.name)
    level_emoji = {"full": "✅", "partial": "⚠️", "minimal": "❌"}
    emoji = level_emoji.get(result["level"], "")
    output = f"{emoji} Level: **{result['level']}** (score: {result['score']})\n\n"
    if result["issues"]:
        output += "**Issues found:**\n"
        for issue in result["issues"]:
            output += f"- {issue}\n"
    else:
        output += "No issues found — fully reproducible!"
    return output


def check_data_quality(file, domain):
    if file is None:
        return "Please upload a .csv file"
    result = data_quality(file.name, domain=domain)
    output = f"**Overall quality:** {result['overall']} / 1.0\n\n"
    output += f"- Completeness: {result['completeness']}\n"
    output += f"- Consistency: {result['consistency']}\n"
    if result["overall"] >= 0.8:
        output += "\n✅ Quality is good — safe to proceed with training"
    elif result["overall"] >= 0.5:
        output += "\n⚠️ Quality is moderate — review before training"
    else:
        output += "\n❌ Quality is low — fix data issues before training"
    return output


def check_model_readiness(file):
    if file is None:
        return "Please upload a .pkl model file"
    result = model_readiness(file.name)
    status = "✅ Ready for production" if result["ready"] else "❌ Not ready for production"
    output = f"{status} (score: {result['score']})\n\n"
    if result["gaps"]:
        output += "**Gaps to fix:**\n"
        for gap in result["gaps"]:
            output += f"- {gap}\n"
    else:
        output += "No gaps — model passes all readiness checks!"
    return output


with gr.Blocks(title="bioscore — Biomedical Scoring Toolkit", theme=gr.themes.Base()) as demo:
    gr.Markdown("# 🧬 bioscore\nBiomedical scoring toolkit — reproducibility, data quality, model readiness")
    gr.Markdown("[pip install bioscore](https://pypi.org/project/bioscore/) · [Source](https://github.com/K-RnD-Lab/SPHERE-III-TECHNOLOGY)")

    with gr.Tab("Reproducibility"):
        gr.Markdown("Upload a Jupyter notebook (.ipynb) or Python script (.py) to check reproducibility")
        rep_file = gr.File(label="Upload notebook/script", file_types=[".ipynb", ".py"])
        rep_btn = gr.Button("Check Reproducibility", variant="primary")
        rep_out = gr.Markdown()
        rep_btn.click(check_reproducibility, inputs=[rep_file], outputs=[rep_out])

    with gr.Tab("Data Quality"):
        gr.Markdown("Upload a CSV dataset to assess quality")
        dq_file = gr.File(label="Upload CSV", file_types=[".csv"])
        dq_domain = gr.Dropdown(["general", "oncology", "agriculture"], value="general", label="Domain")
        dq_btn = gr.Button("Check Data Quality", variant="primary")
        dq_out = gr.Markdown()
        dq_btn.click(check_data_quality, inputs=[dq_file, dq_domain], outputs=[dq_out])

    with gr.Tab("Model Readiness"):
        gr.Markdown("Upload a pickled ML model (.pkl) to check production readiness")
        mr_file = gr.File(label="Upload model (.pkl)", file_types=[".pkl"])
        mr_btn = gr.Button("Check Model Readiness", variant="primary")
        mr_out = gr.Markdown()
        mr_btn.click(check_model_readiness, inputs=[mr_file], outputs=[mr_out])


if __name__ == "__main__":
    demo.launch()
