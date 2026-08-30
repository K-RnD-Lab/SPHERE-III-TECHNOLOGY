from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent

# Cloud deployment starts from the repository root; make this module's package explicit.
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except (FileNotFoundError, KeyError):
    pass

from evidence_gap_navigator.config import get_settings
from evidence_gap_navigator.evaluation import evaluation_overview
from evidence_gap_navigator.monitoring import MonitoringStore
from evidence_gap_navigator.rag import RAGService
from evidence_gap_navigator.retrieval import EvidenceSearchEngine

st.set_page_config(
    page_title="Evidence Gap Navigator",
    page_icon="E",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,500;6..72,650&display=swap');
    :root { --ink:#172019; --fern:#2d5a3c; --sage:#dfe9dc; --paper:#f5f1e7; --amber:#cc7a29; }
    .stApp { background:
      radial-gradient(circle at 86% 5%, rgba(204,122,41,.12), transparent 22rem),
      linear-gradient(135deg, #f7f4eb 0%, #eef3e9 100%); color:var(--ink); }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
    h1, h2, h3 { font-family:'Newsreader',serif !important; letter-spacing:-.02em; }
    .hero { border:1px solid rgba(45,90,60,.16); border-radius:28px; padding:2.6rem 3rem;
      background:linear-gradient(120deg,rgba(255,255,255,.82),rgba(223,233,220,.72));
      box-shadow:0 24px 70px rgba(40,60,44,.10); margin-bottom:1.25rem; }
    .eyebrow { color:var(--fern); font-size:.76rem; font-weight:700; letter-spacing:.14em;
      text-transform:uppercase; }
    .hero h1 { font-size:3.25rem; line-height:.95; margin:.45rem 0 .75rem; color:var(--ink); }
    .hero p { max-width:760px; font-size:1.03rem; color:#4b584e; }
    .metric-card { background:rgba(255,255,255,.72); border:1px solid rgba(45,90,60,.13);
      border-radius:18px; padding:1rem 1.15rem; min-height:104px; }
    .source-card { background:rgba(255,255,255,.72); border-left:4px solid var(--amber);
      border-radius:4px 16px 16px 4px; padding:1rem 1.2rem; margin:.65rem 0; }
    .source-card a { color:var(--fern); font-weight:700; text-decoration:none; }
    [data-testid="stSidebar"] { background:#172019; }
    [data-testid="stSidebar"] * { color:#f5f1e7; }
    .stTabs [data-baseweb="tab-list"] { gap:.45rem; }
    .stTabs [data-baseweb="tab"] { border-radius:999px; padding:.65rem 1rem; background:#e7ede3; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Loading scholarly index...")
def get_engine() -> EvidenceSearchEngine:
    settings = get_settings(ROOT)
    return EvidenceSearchEngine(
        settings.documents_path,
        settings.index_dir,
        settings.embedding_model,
        settings.reranker_model,
    )


@st.cache_resource
def get_store() -> MonitoringStore:
    return MonitoringStore(get_settings(ROOT).monitoring_db)


settings = get_settings(ROOT)
st.markdown(
    """
    <section class="hero">
      <div class="eyebrow">K-R&amp;D Lab · T3 Open Research Infrastructure</div>
      <h1>Evidence Gap<br>Navigator</h1>
      <p>Ask focused questions about retrieval-augmented generation evaluation and monitoring.
      The system retrieves open scholarly evidence, cites the sources it used, and surfaces
      limitations and unanswered research questions.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

if not settings.documents_path.exists():
    st.error("The knowledge base has not been ingested yet.")
    st.code("python scripts/ingest.py --max-works 240", language="bash")
    st.stop()

engine = get_engine()
store = get_store()
summary = engine.corpus_summary()

with st.sidebar:
    st.markdown("## Research controls")
    retrieval_method = st.selectbox(
        "Retrieval strategy",
        ["hybrid_rerank", "hybrid", "dense", "bm25"],
        format_func=lambda value: {
            "hybrid_rerank": "Hybrid + reranker",
            "hybrid": "Hybrid",
            "dense": "Dense vector",
            "bm25": "BM25 keyword",
        }[value],
    )
    top_k = st.slider("Evidence excerpts", 3, 10, 6)
    rewrite_query = st.toggle("LLM query rewrite", value=False, disabled=not settings.groq_api_key)
    st.caption(
        "LLM answering is active." if settings.groq_api_key else
        "Retrieval preview mode. Add GROQ_API_KEY for generated answers."
    )
    st.divider()
    st.markdown(f"**{summary['works']}** open scholarly works")
    st.markdown(f"**{summary['chunks']}** searchable evidence chunks")

ask_tab, explore_tab, evaluation_tab, monitoring_tab, method_tab = st.tabs(
    ["Ask", "Explore evidence", "Evaluation", "Monitoring", "Method"]
)

with ask_tab:
    st.subheader("Ask an evidence-focused question")
    examples = [
        "How should retrieval quality be evaluated in RAG systems?",
        "What failure modes are missed by end-to-end answer metrics?",
        "Which monitoring signals can reveal retrieval drift?",
        "What evidence gaps remain in RAG evaluation benchmarks?",
    ]
    selected_example = st.selectbox("Start with an example", ["Write my own question", *examples])
    question = st.text_area(
        "Research question",
        value="" if selected_example == "Write my own question" else selected_example,
        height=100,
        placeholder="Ask about methods, metrics, limitations, or open evidence gaps...",
    )
    if st.button("Navigate the evidence", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Enter a research question first.")
        else:
            with st.spinner("Retrieving and synthesizing evidence..."):
                response = RAGService(settings, engine).answer(
                    question.strip(),
                    retrieval_method=retrieval_method,
                    top_k=top_k,
                    rewrite_query=rewrite_query,
                )
                interaction_id = store.log_interaction(response)
                st.session_state["interaction_id"] = interaction_id
                st.session_state["last_response"] = response.model_dump()

    if "last_response" in st.session_state:
        response = st.session_state["last_response"]
        st.markdown("### Evidence-backed response")
        if response["provider"] == "retrieval-only-preview":
            st.info("No LLM key is configured, so this is a transparent retrieval preview.")
        st.markdown(response["answer"])
        metrics = st.columns(4)
        metrics[0].metric("Method", response["retrieval_method"])
        metrics[1].metric("Sources", len(response["sources"]))
        metrics[2].metric("Latency", f"{response['latency_ms']:.0f} ms")
        metrics[3].metric("Provider", response["provider"])

        st.markdown("### Retrieved sources")
        for index, result in enumerate(response["sources"], start=1):
            document = result["document"]
            authors = ", ".join(document["authors"][:3]) or "Authors unavailable"
            st.markdown(
                f"""<div class="source-card"><strong>[{index}] {document['title']}</strong><br>
                <small>{authors} · {document.get('year') or 'n.d.'} · score {result['score']:.3f}</small><br>
                {document['text'][:480]}…<br><a href="{document['url']}" target="_blank">Open source ↗</a></div>""",
                unsafe_allow_html=True,
            )

        st.markdown("### Was this useful?")
        left, middle, right = st.columns([1, 1, 5])
        if left.button("Useful", use_container_width=True):
            store.add_feedback(st.session_state["interaction_id"], 1)
            st.success("Feedback recorded.")
        if middle.button("Needs work", use_container_width=True):
            store.add_feedback(st.session_state["interaction_id"], -1)
            st.info("Feedback recorded.")

with explore_tab:
    st.subheader("Inspect the knowledge base directly")
    exploration_query = st.text_input("Search the evidence", "retrieval evaluation metrics")
    if exploration_query:
        results = engine.search(exploration_query, method=retrieval_method, top_k=10)
        for result in results:
            with st.expander(f"{result.rank}. {result.document.title}"):
                st.write(result.document.text)
                st.caption(
                    f"{result.document.year or 'n.d.'} · {result.document.source_name or 'OpenAlex'} · "
                    f"{result.method} score {result.score:.4f}"
                )
                st.link_button("Open scholarly record", result.document.url)

with evaluation_tab:
    st.subheader("Measured quality, not demo intuition")
    frames = evaluation_overview(settings.artifact_dir / "evaluation")
    if not frames:
        st.warning("Evaluation artifacts have not been generated yet.")
        st.code("python scripts/evaluate_retrieval.py\npython scripts/evaluate_rag.py", language="bash")
    else:
        for name, frame in frames.items():
            st.markdown(f"#### {name.replace('_', ' ').title()}")
            st.dataframe(frame, use_container_width=True, hide_index=True)
            numeric = [column for column in frame.columns if column != frame.columns[0]]
            if numeric:
                chart = frame.melt(id_vars=frame.columns[0], value_vars=numeric)
                st.plotly_chart(
                    px.bar(chart, x=frame.columns[0], y="value", color="variable", barmode="group"),
                    use_container_width=True,
                )
        st.caption("The highest-scoring evaluated retrieval and prompt configuration is used by default.")

with monitoring_tab:
    st.subheader("Usage, quality, and operational signals")
    interactions = store.interactions()
    feedback = store.feedback()
    if interactions.empty:
        st.info("Use the Ask tab to create the first monitored interaction.")
    else:
        interactions["created_at"] = pd.to_datetime(interactions["created_at"], utc=True)
        interactions["day"] = interactions["created_at"].dt.date
        feedback_rate = len(feedback) / len(interactions) if len(interactions) else 0
        columns = st.columns(4)
        columns[0].metric("Queries", len(interactions))
        columns[1].metric("Median latency", f"{interactions['latency_ms'].median():.0f} ms")
        columns[2].metric("Feedback coverage", f"{feedback_rate:.0%}")
        positive_rate = (feedback["rating"] > 0).mean() if not feedback.empty else 0
        columns[3].metric("Positive feedback", f"{positive_rate:.0%}")

        daily = interactions.groupby("day", as_index=False).size()
        st.plotly_chart(px.line(daily, x="day", y="size", markers=True, title="Queries by day"), use_container_width=True)
        row1 = st.columns(2)
        row1[0].plotly_chart(px.histogram(interactions, x="latency_ms", title="Latency distribution"), use_container_width=True)
        methods = interactions.groupby("retrieval_method", as_index=False).size()
        row1[1].plotly_chart(px.bar(methods, x="retrieval_method", y="size", title="Retrieval strategy usage"), use_container_width=True)
        row2 = st.columns(2)
        providers = interactions.groupby("provider", as_index=False).size()
        row2[0].plotly_chart(px.pie(providers, names="provider", values="size", title="Provider mix"), use_container_width=True)
        row2[1].plotly_chart(px.scatter(interactions, x="retrieved_count", y="citation_count", title="Retrieved evidence vs citations"), use_container_width=True)
        if not feedback.empty:
            feedback_counts = feedback.groupby("rating", as_index=False).size()
            st.plotly_chart(px.bar(feedback_counts, x="rating", y="size", title="Feedback distribution"), use_container_width=True)

with method_tab:
    st.subheader("How the system works")
    st.markdown(
        """
        1. **Ingest:** a `dlt` pipeline downloads open scholarly metadata and abstracts from OpenAlex.
        2. **Index:** each work is chunked and indexed for BM25 and dense semantic retrieval.
        3. **Retrieve:** keyword, dense, hybrid, and hybrid-plus-reranker approaches are evaluated.
        4. **Answer:** the LLM receives only retrieved evidence and must cite numbered sources.
        5. **Evaluate:** retrieval metrics and end-to-end LLM-as-judge scores select the defaults.
        6. **Monitor:** interactions, latency, citation coverage, and explicit user feedback are recorded.

        This tool supports literature navigation; it does not replace systematic review or expert judgment.
        """
    )
    st.json(summary)
