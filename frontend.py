import streamlit as st
import requests
import json
import time
import textwrap

# Page Configuration
st.set_page_config(
    page_title="GitHub Issue Analyzer",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Styles
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        color: white;
        background-color: #4CAF50;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("GitHub Issue Analyzer 🔍")
st.markdown("Automated classification and summarization of GitHub issues using **Gemini AI**.")

# Sidebar for Instructions
with st.sidebar:
    st.header("How to use")
    st.markdown("""
    1. **Paste** a public GitHub repository link.
    2. **Enter** the issue number.
    3. **Click** 'Analyze Issue'.
    
    The AI will provide:
    - Summary
    - Type (Bug, Feature, etc.)
    - Priority Score
    - Suggested Labels
    """)
    st.info("API Key must be set")

# ---------- Input Fields ----------
col1, col2 = st.columns([3, 1])
with col1:
    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/fastapi/fastapi"
    )
with col2:
    issue_number = st.number_input(
        "Issue #",
        min_value=1,
        step=1,
        value=1
    )

# ---------- Helper: Cache Results ----------
# We use st.cache_data to avoid re-calling the API if params haven't changed.
@st.cache_data(show_spinner=False, ttl=300)
def get_analysis(url, issue):
    """Call backend API and return response."""
    response = requests.post(
        "http://localhost:8000/analyze",
        json={"repo_url": url, "issue_number": issue},
        timeout=45
    )
    return response

# ---------- Analyze Button ----------
if st.button("Analyze Issue", use_container_width=True):
    if not repo_url:
        st.warning("⚠️ Please enter a GitHub Repository URL.")
    else:
        with st.spinner("🤖 Fetching & Analyzing... This may take a few seconds."):
            try:
                # Call the caching wrapper
                start_time = time.time()
                response = get_analysis(repo_url, int(issue_number))
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success(f"Analysis Complete ({duration:.2f}s)")
                    

                    st.divider()

                    # Custom CSS for Cards
                    st.markdown("""
                    <style>
                    .card {
                        background-color: white;
                        padding: 25px;
                        border-radius: 12px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                        margin-bottom: 25px;
                        font-family: 'Source Sans Pro', sans-serif;
                    }
                    .row-flex {
                        display: flex;
                        justify-content: space-between;
                        margin-bottom: 20px;
                        flex-wrap: wrap;
                        gap: 15px;
                    }
                    .column-flex {
                        flex: 1;
                        min-width: 140px;
                    }
                    .h-label {
                        font-weight: 600;
                        color: #6c757d;
                        font-size: 0.85rem;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                        margin-bottom: 4px;
                    }
                    .h-value {
                        font-size: 1.15rem;
                        font-weight: 700;
                        color: #2c3e50;
                    }
                    .section-header {
                        margin-top: 15px;
                        margin-bottom: 8px;
                        font-size: 0.95rem;
                        font-weight: 700;
                        color: #343a40;
                        border-bottom: 1px solid #eee;
                        padding-bottom: 5px;
                    }
                    .content-text {
                        color: #495057;
                        line-height: 1.6;
                        font-size: 1rem;
                    }
                    .info-box {
                        background-color: #e8f4fd;
                        border-left: 4px solid #2196f3;
                        padding: 12px;
                        border-radius: 4px;
                        color: #0c5460;
                        margin-top: 5px;
                        font-size: 0.95rem;
                    }
                    .badge {
                        display: inline-block;
                        padding: 5px 12px;
                        margin-right: 6px;
                        margin-bottom: 6px;
                        font-size: 0.85rem;
                        font-weight: 600;
                        border-radius: 20px;
                        background-color: #f1f3f5;
                        color: #495057;
                        border: 1px solid #dee2e6;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    # Prepare Data for HTML
                    issue_type = data.get("type", "Unknown").title()
                    p_score = data.get('priority_score', 'N/A')
                    display_score = p_score.split(' ')[0] if p_score[0].isdigit() else p_score[:3]
                    summary = data.get('summary', 'No summary available.')
                    impact = data.get('potential_impact', 'N/A')
                    labels = data.get('suggested_labels', [])
                    labels_html = "".join([f'<span class="badge">{l}</span>' for l in labels]) if labels else "<i>None</i>"

                    # Render Single Card HTML
                    # accessing variables directly in the list to avoid indentation issues
                    html_lines = [
                        '<div class="card">',
                        '  <div class="row-flex">',
                        '    <div class="column-flex">',
                        '      <div class="h-label">Issue Type</div>',
                        f'      <div class="h-value">{issue_type}</div>',
                        '    </div>',
                        '    <div class="column-flex">',
                        '      <div class="h-label">Priority Score</div>',
                        f'      <div class="h-value">{display_score}/5 <span style="font-size:0.8rem; font-weight:normal; color:#888">({p_score})</span></div>',
                        '    </div>',
                        '  </div>',
                        '',
                        '  <div class="h-label" style="margin-top:10px;">Summary</div>',
                        f'  <div class="content-text">{summary}</div>',
                        '',
                        '  <br>',
                        '',
                        '  <div class="h-label">Potential Impact</div>',
                        '  <div class="info-box">',
                        f'    {impact}',
                        '  </div>',
                        '',
                        '  <br>',
                        '',
                        '  <div class="h-label">Suggested Labels</div>',
                        '  <div style="margin-top:5px;">',
                        f'    {labels_html}',
                        '  </div>',
                        '</div>'
                    ]
                    card_html = "\n".join(html_lines)
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    # --- Raw JSON Display (Always Visible) ---
                    st.subheader("📦 Raw JSON Response")
                    st.code(json.dumps(data, indent=2), language='json')
                    
                    st.download_button(
                        label="📥 Download Analysis as JSON",
                        data=json.dumps(data, indent=2),
                        file_name=f"issue_analysis_{issue_number}.json",
                        mime="application/json"
                    )
                        
                elif response.status_code == 400:
                    st.error(f"❌ Input Error: {response.json().get('detail')}")
                elif response.status_code == 404:
                    st.error("❌ Issue not found. Please check the URL and Issue #.")
                else:
                    st.error(f"❌ Server Error ({response.status_code}): {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to backend. Is `uvicorn app.main:app` running?")
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")
