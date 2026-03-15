import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Reads API_URL from environment in production
# Falls back to localhost for development
API_BASE = os.getenv("API_URL", os.getenv("API_BASE", "http://localhost:8000/api"))

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Data Intelligence Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CONSTANTS ─────────────────────────────────────────────────
API_BASE = "http://localhost:8000/api"

# ── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #aaa;        /* 🆕 lighter gray for dark theme */
        margin-top: 0;
    }
    .answer-box {
        background: #1a2744;          /* 🆕 dark blue background */
        border-left: 4px solid #667eea;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        color: #e8eaf6;               /* 🆕 light text */
    }
    .history-item {
        background: #1e1e2e;          /* 🆕 dark background */
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #667eea;
        color: #e0e0e0;               /* 🆕 light text */
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE INIT ────────────────────────────────────────
if "file_id" not in st.session_state:
    st.session_state.file_id = None
if "filename" not in st.session_state:
    st.session_state.filename = None
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "file_info" not in st.session_state:
    st.session_state.file_info = None
if "current_question" not in st.session_state:      # 🆕
    st.session_state.current_question = ""
if "trigger_query" not in st.session_state:         # 🆕
    st.session_state.trigger_query = False

# ── HELPER FUNCTIONS ──────────────────────────────────────────
def upload_file(file) -> dict:
    """Upload file to FastAPI"""
    try:
        response = requests.post(
            f"{API_BASE}/upload",
            files={"file": (file.name, file.getvalue(), file.type)}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def query_data(question: str, use_agent: bool, file_id: int = None) -> dict:
    """Send query to FastAPI"""
    try:
        response = requests.post(
            f"{API_BASE}/query",
            json={
                "question": question,
                "use_agent": use_agent,
                "file_id": file_id
            },
            timeout=120
        )
        return response.json()
    except requests.Timeout:
        return {"error": "Request timed out. Try a simpler question."}
    except Exception as e:
        return {"error": str(e)}

def get_stats() -> dict:
    """Get MLflow stats from FastAPI"""
    try:
        response = requests.get(f"{API_BASE}/stats", timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_files() -> list:
    """Get list of uploaded files"""
    try:
        response = requests.get(f"{API_BASE}/files", timeout=10)
        return response.json()
    except Exception as e:
        return []

# ── HEADER ────────────────────────────────────────────────────
st.markdown('<p class="main-header">🤖 Data Intelligence Platform</p>',
            unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload your data, ask questions in natural language, get AI-powered insights</p>',
            unsafe_allow_html=True)
st.divider()

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    use_agent = st.toggle(
    "Use AI Agent",
    value=False,    # ← already False, make sure it stays False
    help="⚠️ Agent works best with larger LLMs. Keep OFF for reliable answers."
)

    st.divider()

    # Show uploaded files
    st.header("📁 Uploaded Files")
    files = get_files()
    if files:
        for f in files:
            st.markdown(f"""
            **{f['filename']}**
            Rows: {f['rows']} | Uploaded: {str(f['uploaded_at'])[:10]}
            """)
            if st.button(f"Use this file", key=f"file_{f['id']}"):
                st.session_state.file_id = f['id']
                st.session_state.filename = f['filename']
                st.success(f"✅ Using {f['filename']}")
    else:
        st.info("No files uploaded yet")

    st.divider()
    st.caption("Built with FastAPI + LangChain + Qdrant + MLflow")

# ── MAIN TABS ─────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📁 Upload Data", "💬 Query Data", "📊 Analytics"])


# ═══════════════════════════════════════════════════════════════
# TAB 1: UPLOAD
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.header("📁 Upload Your Data")
    st.write("Upload a CSV or Excel file to get started. The AI will automatically process and index your data.")

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx"],
        help="Supports CSV and Excel files up to 200MB"
    )

    if uploaded_file is not None:
        # Show file preview
        st.subheader("📋 File Preview")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            size_kb = round(uploaded_file.size / 1024, 1)
            st.metric("File Size", f"{size_kb} KB")
        with col3:
            st.metric("File Type", uploaded_file.type.split("/")[-1].upper())

        # Preview data
        try:
            if uploaded_file.name.endswith(".csv"):
                df_preview = pd.read_csv(uploaded_file)
            else:
                df_preview = pd.read_excel(uploaded_file)

            uploaded_file.seek(0)  # reset file pointer after reading

            st.write(f"**{len(df_preview)} rows × {len(df_preview.columns)} columns**")
            st.dataframe(df_preview.head(5), use_container_width=True)

        except Exception as e:
            st.error(f"Could not preview file: {e}")

        st.divider()

        # Upload button
        if st.button("🚀 Upload & Process with AI", use_container_width=True):
            with st.spinner("Uploading file and triggering AI pipeline..."):
                result = upload_file(uploaded_file)

            if "error" in result:
                st.error(f"❌ Upload failed: {result['error']}")
            else:
                # Save to session state
                st.session_state.file_id = result.get("file_id")
                st.session_state.filename = result.get("filename")
                st.session_state.file_info = result

                st.success(f"✅ File uploaded successfully!")

                # Show upload results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("File ID", result.get("file_id"))
                with col2:
                    st.metric("Rows Processed", result.get("rows"))
                with col3:
                    st.metric("Columns Found", len(result.get("columns", [])))

                st.info("⚙️ AI pipeline is processing your data in the background. This takes 15-30 seconds for large files. You can start querying shortly!")

                # Show columns
                with st.expander("📋 Detected Columns"):
                    cols = result.get("columns", [])
                    col_grid = st.columns(4)
                    for i, col in enumerate(cols):
                        with col_grid[i % 4]:
                            st.markdown(f"• `{col}`")

    else:
        # Empty state
        st.markdown("""
    <div style="text-align: center; padding: 3rem; color: #aaa;">
        <h3>👆 Upload a file to get started</h3>
        <p>Supported formats: CSV, Excel (.xlsx)</p>
        <p>The AI will automatically index your data</p>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB 2: QUERY
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.header("💬 Ask Your Data Anything")

    # Check if file is selected
    if st.session_state.file_id:
        st.success(f"📁 Active file: **{st.session_state.filename}** (ID: {st.session_state.file_id})")
    else:
        st.warning("⚠️ No file selected. Upload a file first or select one from the sidebar.")

    # ── Initialize session state keys ──────────────────────────
    if "current_question" not in st.session_state:
        st.session_state.current_question = ""
    if "trigger_query" not in st.session_state:
        st.session_state.trigger_query = False

    # ── Example questions ──────────────────────────────────────
    with st.expander("💡 Example Questions", expanded=True):
        examples = [
            "How many employees have attrition Yes?",
            "What is the average monthly income by department?",
            "Which employees work overtime?",
            "What is the attrition rate by gender?",
            "Which job roles have the highest monthly income?",
            "How many employees travel frequently for business?",
        ]
        cols = st.columns(2)
        for i, example in enumerate(examples):
            with cols[i % 2]:
                if st.button(
                    f"📝 {example[:45]}",
                    key=f"example_btn_{i}",
                    use_container_width=True
                ):
                    st.session_state.current_question = example
                    st.session_state.trigger_query = True
                    st.rerun()

    # ── Question input ─────────────────────────────────────────
    question = st.text_area(
        "Your Question",
        value=st.session_state.current_question,
        placeholder="Type your question here or click an example above...",
        height=100,
        key="question_box"
    )

    # ── Buttons ────────────────────────────────────────────────
    col1, col2 = st.columns([3, 1])
    with col1:
        submit_clicked = st.button(
            "🤖 Ask Question",
            use_container_width=True,
            type="primary"
        )
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.query_history = []
            st.session_state.current_question = ""
            st.session_state.trigger_query = False
            st.rerun()

    # ── Trigger query (manual OR example click) ────────────────
    should_query = submit_clicked or st.session_state.trigger_query
    active_question = question or st.session_state.current_question

    if should_query and active_question.strip():
        # Reset trigger immediately
        st.session_state.trigger_query = False
        st.session_state.current_question = ""

        with st.spinner("🧠 AI is thinking..."):
            result = query_data(
                question=active_question,
                use_agent=use_agent,
                file_id=st.session_state.file_id
            )

        if "error" in result:
            st.error(f"❌ Error: {result['error']}")
        else:
            st.session_state.query_history.insert(0, {
                "question": active_question,
                "answer": (
                    result.get("answer") or
                    result.get("text") or
                    "No answer returned"
                ),
                "mode": (
                    result.get("mode") or
                    result.get("status") or
                    "unknown"
                ),
                "latency": (
                    result.get("latency_seconds") or
                    result.get("latency") or
                    0.0
                ),
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            st.rerun()

    # ── Conversation history ───────────────────────────────────
    if st.session_state.query_history:
        st.divider()
        st.subheader("💬 Conversation History")

        for i, item in enumerate(st.session_state.query_history):
            # Question bubble
            st.markdown(f"""
            <div style="background:#1e3a5f; padding:0.75rem 1rem;
                        border-radius:8px; margin:0.5rem 0;
                        border-left:3px solid #2196F3; color:#e8f4fd;">
                <strong>🧑 You:</strong> {item['question']}
            </div>
            """, unsafe_allow_html=True)

            # Answer bubble
            st.markdown(f"""
            <div style="background:#1a3a2a; padding:0.75rem 1rem;
                        border-radius:8px; margin:0.5rem 0;
                        border-left:3px solid #4CAF50; color:#e8f5e9;">
                <strong>🤖 AI:</strong> {item['answer']}
            </div>
            """, unsafe_allow_html=True)

            # Metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"⏱️ {item['latency']:.2f}s")
            with col2:
                st.caption(f"🔧 {item['mode']}")
            with col3:
                st.caption(f"🕐 {item['timestamp']}")

            if i < len(st.session_state.query_history) - 1:
                st.divider()
    else:
        st.markdown("""
        <div style="text-align:center; padding:2rem; color:#aaa;">
            <h4>No questions yet</h4>
            <p>Click an example above or type your own question!</p>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 3: ANALYTICS
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.header("📊 System Analytics")
    st.write("Real-time metrics from MLflow tracking")

    # Refresh button
    if st.button("🔄 Refresh Metrics"):
        st.rerun()

    # Fetch stats
    with st.spinner("Loading analytics..."):
        stats = get_stats()

    if "error" in stats:
        st.error(f"Could not load stats: {stats['error']}")
    elif stats.get("total_queries", 0) == 0:
        st.info("No queries logged yet. Ask some questions first!")
    else:
        # ── TOP METRICS ROW ───────────────────────────────────
        st.subheader("📈 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Queries",
                stats.get("total_queries", 0),
                help="Total number of questions asked"
            )
        with col2:
            st.metric(
                "Avg Latency",
                f"{stats.get('avg_latency_seconds', 0):.2f}s",
                help="Average response time"
            )
        with col3:
            st.metric(
                "Success Rate",
                f"{stats.get('success_rate', 0):.1f}%",
                help="Percentage of successful queries"
            )
        with col4:
            st.metric(
                "Avg Similarity",
                f"{stats.get('avg_similarity_score', 0):.3f}",
                help="Average Qdrant similarity score (higher = more relevant)"
            )

        st.divider()

        # ── CHARTS ROW ────────────────────────────────────────
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏷️ Query Categories")
            category_data = stats.get("category_breakdown", {})
            if category_data:
                fig = px.pie(
                    values=list(category_data.values()),
                    names=list(category_data.keys()),
                    color_discrete_sequence=px.colors.sequential.Purples_r,
                    hole=0.4
                )
                fig.update_layout(
                    margin=dict(t=0, b=0, l=0, r=0),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🔧 Query Modes")
            mode_data = stats.get("mode_breakdown", {})
            if mode_data:
                fig = px.bar(
                    x=list(mode_data.keys()),
                    y=list(mode_data.values()),
                    color=list(mode_data.keys()),
                    color_discrete_sequence=["#667eea", "#764ba2", "#f093fb"],
                    labels={"x": "Mode", "y": "Count"}
                )
                fig.update_layout(
                    margin=dict(t=0, b=0, l=0, r=0),
                    height=300,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # ── RECENT QUERIES ────────────────────────────────────
        st.subheader("🕐 Recent Queries")
        recent = stats.get("recent_queries", [])
        if recent:
            for i, q in enumerate(recent, 1):
                st.markdown(f"""
                <div style="background:#1e1e2e; padding:0.6rem 1rem;
                            border-radius:6px; margin:0.3rem 0;
                            border-left:3px solid #667eea;
                            color:#e0e0e0;">        
                    <strong>{i}.</strong> {q}
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # ── RAW STATS ─────────────────────────────────────────
        with st.expander("🔍 Raw Stats JSON"):
            st.json(stats)