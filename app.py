import os
import streamlit as st
import plotly.express as px

from ingestion import load_csv
from eda import (
    get_dataset_summary,
    get_column_info,
    get_missing_values,
    remove_duplicates
)
from report import create_report


def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")

    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(
    page_title="InsightRAG",
    page_icon="📊",
    layout="wide"
)

load_css()

st.sidebar.markdown("""
# 🚀 InsightRAG

### AI Analytics Platform
""")

page=st.sidebar.radio(
    "Navigation",
    ["Dashboard","AI Chat","Report"]
)

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV",
    type="csv"
)

# ---------------- MAIN APP ----------------

if uploaded_file:

    # Load Dataset
    df = load_csv(uploaded_file)

    # Create summary (THIS FIXES THE ERROR)
    summary = get_dataset_summary(df)

    if page == "Dashboard":

        # Hero Section
        st.markdown("""
        <div class="hero">
            <h1>🚀 InsightRAG</h1>
            <p>AI-Powered Exploratory Data Analysis with RAG</p>
        </div>
        """, unsafe_allow_html=True)

        # KPI Cards
        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            st.markdown(
                f"""
                <div class="card">
                    <h3>Rows</h3>
                    <h1>{summary['rows']:,}</h1>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                f"""
                <div class="card">
                    <h3>Columns</h3>
                    <h1>{summary['columns']}</h1>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c3:
            st.markdown(
                f"""
                <div class="card">
                    <h3>Missing</h3>
                    <h1>{summary['missing']}</h1>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c4:
            st.markdown(
                f"""
                <div class="card">
                    <h3>Duplicates</h3>
                    <h1>{summary['duplicates']}</h1>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c5:
            st.markdown(
                f"""
                <div class="card">
                    <h3>Memory</h3>
                    <h1>{summary['memory']} KB</h1>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Two-column layout
        left, right = st.columns([1.6, 1])

        with left:
            st.markdown("<div class='section-box'>", unsafe_allow_html=True)
            st.subheader("📄 Dataset Preview")
            st.dataframe(df.head(10), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown("<div class='section-box'>", unsafe_allow_html=True)
            st.subheader("📊 Quick Info")
            st.write(f"**Rows:** {summary['rows']:,}")
            st.write(f"**Columns:** {summary['columns']}")
            st.write(f"**Missing:** {summary['missing']}")
            st.write(f"**Duplicates:** {summary['duplicates']}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.subheader("📈 Missing Value Analysis")
        st.dataframe(get_missing_values(df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Charts
        numeric = df.select_dtypes(include="number").columns

        if len(numeric) > 0:

            st.markdown("<div class='section-box'>", unsafe_allow_html=True)
            st.subheader("📊 Interactive Distribution")

            col = st.selectbox("Choose Numeric Column", numeric)

            fig = px.histogram(
                df,
                x=col,
                template="plotly_dark"
            )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    elif page == "AI Chat":

        from chunking import dataframe_to_documents
        from embeddings import get_embedding_model
        from vector_store import create_vector_store
        from retrieval import retrieve_documents
        from ai_chat import ask_ai

        st.title("🤖 Chat with Your Dataset")

        if "db" not in st.session_state:
            docs = dataframe_to_documents(df.to_csv(index=False))
            emb = get_embedding_model()
            st.session_state.db = create_vector_store(docs, emb)

        question = st.chat_input("Ask anything about your dataset...")

        if question:
            with st.chat_message("user"):
                st.write(question)

            docs = retrieve_documents(st.session_state.db, question)
            answer = ask_ai(question, docs)

            with st.chat_message("assistant"):
                st.write(answer)

    elif page == "Report":

    # Hero Banner
        st.markdown("""
        <div class="hero">
            <h1>📄 AI Report Generator</h1>
            <p>Generate a professional PDF report of your dataset analysis.</p>
        </div>
        """, unsafe_allow_html=True)

    # Two-column layout
    left, right = st.columns([1.6, 1])

    # Left - Dataset Summary
    with left:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)

        st.subheader("📊 Dataset Summary")

        st.write(f"**📄 Rows:** {summary['rows']:,}")
        st.write(f"**📑 Columns:** {summary['columns']}")
        st.write(f"**⚠️ Missing Values:** {summary['missing']}")
        st.write(f"**🔁 Duplicate Rows:** {summary['duplicates']}")
        st.write(f"**💾 Memory Usage:** {summary['memory']} KB")

        st.markdown("</div>", unsafe_allow_html=True)

    # Right - Export Card
    with right:
        st.markdown(f"""
        <div class="card">
            <h3>📥 Export Report</h3>
            <h1>{summary['rows']:,}</h1>
            <p>Rows included</p>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        if st.button("📄 Generate PDF", use_container_width=True):
            path = create_report(summary)

            with open(path, "rb") as pdf_file:
                st.download_button(
                    label="⬇ Download Report",
                    data=pdf_file,
                    file_name="InsightRAG_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

    st.write("")

    # Bottom Section
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)

    st.subheader("✨ Report Includes")

    col1, col2 = st.columns(2)

    with col1:
        st.write("✅ Dataset Summary")
        st.write("✅ Rows & Columns")
        st.write("✅ Missing Value Count")

    with col2:
        st.write("✅ Duplicate Count")
        st.write("✅ Memory Usage")
        st.write("🚀 AI-Ready Format")

    st.markdown("</div>", unsafe_allow_html=True)

else:

    st.markdown("""
    <div class="hero">
        <h1>🚀 InsightRAG</h1>
        <p>Upload a CSV from the sidebar to begin.</p>
    </div>
    """, unsafe_allow_html=True)