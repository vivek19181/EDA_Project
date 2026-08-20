import random
import textwrap

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from ingestion import load_csv
from eda import (
    get_dataset_summary,
    get_column_info,
    get_missing_values,
    remove_duplicates
)
from report import create_report


# ---------------- THEME / CSS ----------------

APP_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Background */
.stApp{
    background: radial-gradient(circle at top, #2a1454 0%, #120a2e 35%, #05010f 75%);
    color:white;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #1b1140 0%, #120a2e 100%);
    border-right:1px solid rgba(255,255,255,.08);
}
section[data-testid="stSidebar"] > div{
    padding-top: 1.2rem;
}

/* Sidebar logo */
.brand{
    display:flex;
    align-items:center;
    gap:10px;
    margin-bottom:22px;
    padding: 0 4px;
}
.brand .mark{
    width:34px;
    height:34px;
    border-radius:10px;
    background: conic-gradient(from 180deg,#f97316,#a855f7,#22d3ee,#f97316);
    box-shadow: 0 6px 16px rgba(124,58,237,.45);
}
.brand h2{
    margin:0;
    font-size:22px;
    font-weight:800;
    letter-spacing:-0.5px;
}

/* Pill navigation (built on top of st.radio) */
div[data-testid="stRadio"] > div{
    flex-direction: column;
    gap: 6px;
}
div[data-testid="stRadio"] label{
    background: transparent;
    border-radius: 14px;
    padding: 10px 14px !important;
    margin: 0 !important;
    transition: .2s ease;
    cursor: pointer;
    width: 100%;
}
div[data-testid="stRadio"] label > div:first-child{
    display:none;
}
div[data-testid="stRadio"] label p{
    font-size: 15px !important;
    font-weight: 500;
    color: #cbd5e1;
}
div[data-testid="stRadio"] label:hover{
    background: rgba(255,255,255,.06);
}
div[data-testid="stRadio"] label:has(input:checked){
    background: linear-gradient(90deg,#7c3aed,#4f46e5);
    box-shadow: 0 10px 24px rgba(124,58,237,.35);
}
div[data-testid="stRadio"] label:has(input:checked) p{
    color:#ffffff;
    font-weight: 700;
}

/* Sidebar tip card */
.tip-card{
    margin-top: 30px;
    background: radial-gradient(circle at 30% 20%, #6d28d9, #1e1240 70%);
    border-radius: 20px;
    padding: 22px 18px;
    text-align:center;
    border: 1px solid rgba(255,255,255,.08);
}
.tip-card h4{
    margin: 0 0 6px 0;
    font-size: 16px;
}
.tip-card p{
    margin:0;
    font-size:12.5px;
    color: rgba(255,255,255,.75);
    line-height:1.4;
}

/* Top bar pills */
.pill{
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:8px 16px;
    border-radius:999px;
    font-size:13px;
    font-weight:600;
}
.pill-active{
    background: linear-gradient(90deg,#7c3aed,#4f46e5);
    color:white;
}

/* Hero Title */
.hero{
    background:linear-gradient(135deg,#2563eb,#7c3aed);
    border-radius:22px;
    padding:35px;
    color:white;
    box-shadow:0 15px 35px rgba(0,0,0,.35);
    margin-bottom:25px;
}
.hero h1{
    margin:0;
    font-size:38px;
    font-weight:800;
    letter-spacing:-0.5px;
}
.hero p{
    margin-top:8px;
    color:#dbeafe;
}

/* KPI Cards */
.kpi-card{
    background: rgba(255,255,255,.05);
    backdrop-filter: blur(16px);
    border:1px solid rgba(255,255,255,.08);
    border-radius:20px;
    padding:20px;
    transition:.25s;
    box-shadow:0 10px 30px rgba(0,0,0,.25);
    height: 100%;
}
.kpi-card:hover{
    transform: translateY(-4px);
    border-color: rgba(124,58,237,.6);
}
.kpi-top{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    margin-bottom: 18px;
}
.kpi-icon{
    width:38px;
    height:38px;
    border-radius:11px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:18px;
}
.kpi-label{
    color:#94a3b8;
    font-size:13px;
    font-weight:600;
    margin-bottom:4px;
}
.kpi-value{
    color:white;
    font-size:28px;
    font-weight:800;
    letter-spacing:-0.5px;
}
.kpi-sub{
    color: rgba(255,255,255,.45);
    font-size:12px;
    margin-top:4px;
}

/* Glass Cards (generic) */
.card{
    background:rgba(255,255,255,.06);
    backdrop-filter:blur(16px);
    border:1px solid rgba(255,255,255,.08);
    border-radius:18px;
    padding:22px;
    text-align:center;
    transition:.3s;
    box-shadow:0 10px 30px rgba(0,0,0,.25);
}
.card:hover{
    transform:translateY(-5px);
    border-color:#3b82f6;
}
.card h3{
    color:#94a3b8;
    margin-bottom:10px;
}
.card h1{
    color:white;
    margin:0;
}

/* Section Box */
.section-box{
    background:rgba(255,255,255,.04);
    backdrop-filter: blur(10px);
    border-radius:20px;
    padding:22px;
    border:1px solid rgba(255,255,255,.07);
    margin-top:18px;
}
.section-box h3{
    margin-top:0;
}

/* Chart header */
.chart-head{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
}
.chart-big-num{
    font-size:34px;
    font-weight:800;
    letter-spacing:-0.5px;
}
.badge-green{
    display:inline-block;
    background: rgba(74,222,128,.15);
    color:#4ade80;
    padding:3px 10px;
    border-radius:999px;
    font-size:12.5px;
    font-weight:700;
    margin-left:8px;
}

/* Buttons */
.stButton>button{
    background:linear-gradient(90deg,#2563eb,#7c3aed);
    color:white;
    border:none;
    border-radius:12px;
    padding:10px 18px;
    font-weight:600;
}

/* Text input (search bar) */
div[data-testid="stTextInput"] input{
    background: rgba(255,255,255,.05);
    border: 1px solid rgba(255,255,255,.1);
    border-radius: 14px;
    color: white;
    padding: 10px 14px;
}
"""


def load_css():
    st.markdown(f"<style>{APP_CSS}</style>", unsafe_allow_html=True)


def html_block(text, target=None):
    """Render a multi-line HTML string safely.

    Streamlit's markdown parser treats lines indented 4+ spaces as a code
    block, which prints raw HTML as literal text instead of rendering it.
    Multi-line f-strings written inline in this file inherit the Python
    source's indentation, so we strip that common leading whitespace here
    before handing the string to st.markdown.

    Pass target=st.sidebar to render into the sidebar instead of the
    main area.
    """
    (target or st).markdown(textwrap.dedent(text).strip(), unsafe_allow_html=True)


def sparkline_svg(seed, color, width=100, height=36, points=14):
    """Small deterministic decorative sparkline as inline SVG (no extra deps)."""
    # summary values can be numpy int64/float64 (from pandas), which
    # random.Random() doesn't accept directly — coerce to a plain Python int.
    seed = int(seed)
    rng = random.Random(seed)
    values = [rng.uniform(0.15, 0.95) for _ in range(points)]
    step = width / (points - 1)
    coords = []
    for i, v in enumerate(values):
        x = i * step
        y = height - (v * height)
        coords.append(f"{x:.1f},{y:.1f}")
    path = " ".join(coords)
    # Kept as a single line on purpose: Streamlit's markdown parser treats
    # lines indented 4+ spaces as a code block, which would print this
    # SVG/HTML as literal text instead of rendering it.
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<polyline points="{path}" fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/></svg>'
    )


def kpi_card(label, value, icon, icon_bg, sub, seed, spark_color):
    # Built as one line on purpose — see the note in sparkline_svg() above.
    html = (
        f'<div class="kpi-card">'
        f'<div class="kpi-top">'
        f'<div class="kpi-icon" style="background:{icon_bg};">{icon}</div>'
        f'{sparkline_svg(seed, spark_color)}'
        f'</div>'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{sub}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


st.set_page_config(
    page_title="InsightRAG",
    page_icon="📊",
    layout="wide"
)

load_css()

# ---------------- SIDEBAR ----------------

html_block("""
    <div class="brand">
        <div class="mark"></div>
        <h2>InsightRAG</h2>
    </div>
    """, target=st.sidebar)

page = st.sidebar.radio(
    "Navigation",
    ["⊞  Dashboard", "✨  AI Chat", "📄  Report"],
    label_visibility="collapsed"
)
page = page.split("  ", 1)[1]

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV",
    type="csv"
)

html_block("""
    <div class="tip-card">
        <h4>💡 Quick Tip</h4>
        <p>Head to <b>AI Chat</b> to ask questions about your dataset in plain English.</p>
    </div>
    """, target=st.sidebar)

# ---------------- MAIN APP ----------------

if uploaded_file:

    # Load Dataset
    df = load_csv(uploaded_file)

    # Create summary
    summary = get_dataset_summary(df)

    if page == "Dashboard":

        # Top bar: title + status pills
        top_left, top_right = st.columns([3, 1])

        with top_left:
            html_block("""
            <div class="hero">
                <h1>🚀 InsightRAG</h1>
                <p>AI-Powered Exploratory Data Analysis with RAG</p>
            </div>
            """)

        with top_right:
            html_block("""
                <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:14px;">
                    <span class="pill pill-active">🟢 Data Loaded</span>
                </div>
                """)

        # Optional column search
        search_term = st.text_input(
            "🔎 Search columns",
            placeholder="Search columns in your dataset...",
            label_visibility="collapsed"
        )

        # KPI Cards
        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            kpi_card(
                "Rows", f"{summary['rows']:,}", "📊",
                "linear-gradient(135deg,#f97316,#ea580c)",
                "records in dataset", seed=summary['rows'], spark_color="#fb923c"
            )
        with c2:
            kpi_card(
                "Columns", summary['columns'], "🧬",
                "linear-gradient(135deg,#7c3aed,#4f46e5)",
                "features tracked", seed=summary['columns'] + 1, spark_color="#a78bfa"
            )
        with c3:
            kpi_card(
                "Missing", summary['missing'], "⚠️",
                "linear-gradient(135deg,#0ea5e9,#0284c7)",
                "empty cells found", seed=summary['missing'] + 2, spark_color="#38bdf8"
            )
        with c4:
            kpi_card(
                "Duplicates", summary['duplicates'], "🔁",
                "linear-gradient(135deg,#22c55e,#16a34a)",
                "repeated rows", seed=summary['duplicates'] + 3, spark_color="#4ade80"
            )
        with c5:
            kpi_card(
                "Memory", f"{summary['memory']} KB", "💾",
                "linear-gradient(135deg,#ec4899,#db2777)",
                "in-memory footprint", seed=int(summary['memory']) + 4, spark_color="#f472b6"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Two-column layout: preview + quick info
        left, right = st.columns([1.6, 1])

        with left:
            st.markdown("<div class='section-box'>", unsafe_allow_html=True)
            st.subheader("📄 Dataset Preview")
            preview_df = df.head(10)
            if search_term:
                matched_cols = [c for c in df.columns if search_term.lower() in c.lower()]
                if matched_cols:
                    preview_df = df[matched_cols].head(10)
                else:
                    st.caption(f"No columns match '{search_term}' — showing all columns.")
            st.dataframe(preview_df, width="stretch")
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
        st.dataframe(get_missing_values(df), width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

        # Charts row: distribution + completeness gauge
        numeric = df.select_dtypes(include="number").columns

        if len(numeric) > 0:

            chart_col, gauge_col = st.columns([1.7, 1])

            with chart_col:
                st.markdown("<div class='section-box'>", unsafe_allow_html=True)

                col = st.selectbox("Choose Numeric Column", numeric)
                mean_val = df[col].mean()

                html_block(f"""
                    <div class="chart-head">
                        <div>
                            <div class="kpi-label">📊 Interactive Distribution — {col}</div>
                            <span class="chart-big-num">{mean_val:,.2f}</span>
                            <span class="badge-green">avg</span>
                        </div>
                    </div>
                    """)

                fig = px.histogram(df, x=col, template="plotly_dark")
                fig.update_traces(marker_color="#7c3aed")
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=20, l=10, r=10, b=10)
                )
                st.plotly_chart(fig, width="stretch")
                st.markdown("</div>", unsafe_allow_html=True)

            with gauge_col:
                st.markdown("<div class='section-box'>", unsafe_allow_html=True)
                st.markdown("<div class='kpi-label'>🎯 Data Completeness</div>", unsafe_allow_html=True)

                total_cells = summary['rows'] * summary['columns']
                completeness = 100.0 if total_cells == 0 else round(
                    (1 - summary['missing'] / total_cells) * 100, 1
                )

                gauge_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=completeness,
                    number={"suffix": "%", "font": {"color": "white", "size": 34}},
                    gauge={
                        "axis": {"range": [0, 100], "tickcolor": "rgba(255,255,255,.3)"},
                        "bar": {"color": "#22d3ee"},
                        "bgcolor": "rgba(0,0,0,0)",
                        "borderwidth": 0,
                        "steps": [
                            {"range": [0, 60], "color": "rgba(234,179,8,.35)"},
                            {"range": [60, 100], "color": "rgba(34,211,238,.2)"},
                        ],
                    }
                ))
                gauge_fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=10, b=10, l=20, r=20),
                    height=260,
                    font={"color": "white"}
                )
                st.plotly_chart(gauge_fig, width="stretch")
                st.caption("Share of cells that are not missing across the whole dataset.")
                st.markdown("</div>", unsafe_allow_html=True)

    elif page == "AI Chat":

        from vector_store import build_vector_store
        from retrieval import retrieve_documents
        from ai_chat import ask_ai

        html_block("""
        <div class="hero">
            <h1>🤖 Chat with Your Dataset</h1>
            <p>Ask questions in plain English and get answers grounded in your data.</p>
        </div>
        """)

        csv_text = df.to_csv(index=False)
        dataset_key = (uploaded_file.name, len(csv_text), hash(csv_text))
        if st.session_state.get("dataset_key") != dataset_key:
            st.session_state.db = build_vector_store(csv_text)
            st.session_state.dataset_key = dataset_key

        question = st.chat_input("Ask anything about your dataset...")

        if question:
            with st.chat_message("user"):
                st.write(question)

            docs = retrieve_documents(st.session_state.db, question)
            answer = ask_ai(question, docs, summary)

            with st.chat_message("assistant"):
                st.write(answer)

    elif page == "Report":

        # Hero Banner
        html_block("""
        <div class="hero">
            <h1>📄 AI Report Generator</h1>
            <p>Generate a professional PDF report of your dataset analysis.</p>
        </div>
        """)

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
            html_block(f"""
            <div class="card">
                <h3>📥 Export Report</h3>
                <h1>{summary['rows']:,}</h1>
                <p>Rows included</p>
            </div>
            """)

            st.write("")

            if st.button("📄 Generate PDF", width="stretch"):
                path = create_report(summary)

                with open(path, "rb") as pdf_file:
                    st.download_button(
                        label="⬇ Download Report",
                        data=pdf_file,
                        file_name="InsightRAG_Report.pdf",
                        mime="application/pdf",
                        width="stretch"
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

    html_block("""
    <div class="hero">
        <h1>🚀 InsightRAG</h1>
        <p>Upload a CSV from the sidebar to begin.</p>
    </div>
    """)