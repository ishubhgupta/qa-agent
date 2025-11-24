import streamlit as st
import requests
import json
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Autonomous QA Agent",
    page_icon="🤖",
    layout="wide"
)

# Backend API URL
API_URL = "http://localhost:8000"

# Initialize session state
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []
if "uploaded_html" not in st.session_state:
    st.session_state.uploaded_html = None
if "kb_built" not in st.session_state:
    st.session_state.kb_built = False
if "test_cases" not in st.session_state:
    st.session_state.test_cases = []
if "selected_test_case" not in st.session_state:
    st.session_state.selected_test_case = None
if "generated_script" not in st.session_state:
    st.session_state.generated_script = None


def call_api(endpoint: str, method: str = "GET", files=None, data=None, json_data=None):
    """Call backend API"""
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=60)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, timeout=60)
            elif json_data:
                response = requests.post(url, json=json_data, timeout=60)
            elif data:
                response = requests.post(url, data=data, timeout=60)
            else:
                response = requests.post(url, timeout=60)
        elif method == "DELETE":
            response = requests.delete(url, timeout=60)
        else:
            return None
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        st.info("Make sure the FastAPI backend is running on http://localhost:8000")
        return None


# Title and description
st.title("🤖 Autonomous QA Agent")
st.markdown("""
Generate grounded test cases and Selenium scripts from your checkout page and documentation.
All test cases are strictly based on your provided documents - no hallucinations!
""")

# Check backend health
with st.sidebar:
    st.header("Backend Status")
    if st.button("Check Connection"):
        health = call_api("/health", "GET")
        if health:
            st.success(f"✅ Backend: {health['status']}")
            st.info(f"ChromaDB: {health['chroma_status']}")
        else:
            st.error("❌ Backend not reachable")
    
    st.markdown("---")
    st.markdown("### Instructions")
    st.markdown("""
    1. Upload support documents (MD, TXT, PDF, JSON)
    2. Upload checkout HTML file
    3. Build knowledge base
    4. Generate test cases for a feature
    5. Select a test case and generate Selenium script
    """)

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📁 Upload Documents",
    "🧠 Build Knowledge Base",
    "📝 Generate Test Cases",
    "🔧 Generate Scripts"
])

# Tab 1: Upload Documents
with tab1:
    st.header("Upload Documents")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Support Documents")
        st.markdown("Upload 1-5 support documents (MD, TXT, PDF, JSON)")
        
        doc_files = st.file_uploader(
            "Choose files",
            type=["md", "txt", "pdf", "json"],
            accept_multiple_files=True,
            key="doc_uploader"
        )
        
        if st.button("Upload Documents", type="primary"):
            if doc_files:
                if len(doc_files) > 5:
                    st.error("Maximum 5 documents allowed")
                else:
                    with st.spinner("Uploading documents..."):
                        files = [("files", (f.name, f, f.type)) for f in doc_files]
                        result = call_api("/upload_docs", "POST", files=files)
                        
                        if result and result.get("success"):
                            st.session_state.uploaded_docs = result.get("files", [])
                            st.success(result.get("message"))
                            st.session_state.kb_built = False
            else:
                st.warning("Please select files to upload")
        
        if st.session_state.uploaded_docs:
            st.info(f"Uploaded: {', '.join(st.session_state.uploaded_docs)}")
    
    with col2:
        st.subheader("Checkout HTML")
        st.markdown("Upload your checkout page HTML file")
        
        html_file = st.file_uploader(
            "Choose HTML file",
            type=["html", "htm"],
            key="html_uploader"
        )
        
        if st.button("Upload HTML", type="primary"):
            if html_file:
                with st.spinner("Uploading HTML..."):
                    files = [("file", (html_file.name, html_file, html_file.type))]
                    result = call_api("/upload_html", "POST", files=files)
                    
                    if result and result.get("success"):
                        st.session_state.uploaded_html = html_file.name
                        st.success(result.get("message"))
                        st.session_state.kb_built = False
            else:
                st.warning("Please select an HTML file")
        
        if st.session_state.uploaded_html:
            st.info(f"Uploaded: {st.session_state.uploaded_html}")

# Tab 2: Build Knowledge Base
with tab2:
    st.header("Build Knowledge Base")
    
    st.markdown("""
    Build the vector database from your uploaded documents. 
    This processes all documents, extracts text and HTML selectors, and creates embeddings.
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        clear_existing = st.checkbox("Clear existing KB", value=False)
        
        if st.button("🔨 Build Knowledge Base", type="primary", use_container_width=True):
            if not st.session_state.uploaded_docs and not st.session_state.uploaded_html:
                st.error("Please upload documents first")
            else:
                with st.spinner("Building knowledge base... This may take a moment."):
                    result = call_api(
                        f"/build_kb?clear_existing={clear_existing}",
                        "POST"
                    )
                    
                    if result and result.get("success"):
                        st.success(result.get("message"))
                        st.session_state.kb_built = True
                        
                        # Show stats
                        st.metric("Total Chunks", result.get("num_chunks", 0))
                        st.metric("Documents Processed", result.get("num_documents", 0))
    
    with col2:
        if st.button("📊 View KB Statistics"):
            with st.spinner("Fetching statistics..."):
                stats = call_api("/kb_stats", "GET")
                
                if stats:
                    st.subheader("Knowledge Base Statistics")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Total Chunks", stats.get("total_chunks", 0))
                    with col_b:
                        st.metric("Unique Sources", stats.get("unique_sources", 0))
                    
                    if stats.get("sources"):
                        st.markdown("**Source Documents:**")
                        for source in stats["sources"]:
                            st.markdown(f"- {source}")

# Tab 3: Generate Test Cases
with tab3:
    st.header("Generate Test Cases")
    
    if not st.session_state.kb_built:
        st.warning("⚠️ Please build the knowledge base first")
    
    st.markdown("Enter a feature or functionality to generate test cases for:")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        feature_query = st.text_input(
            "Feature Query",
            placeholder="e.g., discount code validation, payment processing, form validation",
            key="feature_query"
        )
    
    with col2:
        num_test_cases = st.number_input(
            "Number of test cases",
            min_value=1,
            max_value=10,
            value=5,
            key="num_test_cases"
        )
    
    if st.button("🎯 Generate Test Cases", type="primary"):
        if not feature_query:
            st.error("Please enter a feature query")
        else:
            with st.spinner("Generating test cases... This may take 10-20 seconds."):
                result = call_api(
                    "/generate_test_cases",
                    "POST",
                    json_data={
                        "feature_query": feature_query,
                        "num_test_cases": num_test_cases
                    }
                )
                
                if result:
                    st.session_state.test_cases = result.get("test_cases", [])
                    st.success(f"✅ Generated {len(st.session_state.test_cases)} test cases in {result.get('generation_time', 0):.2f}s")
                    
                    # Show context sources
                    if result.get("context_sources"):
                        st.info(f"📚 Grounded in: {', '.join(result['context_sources'])}")
    
    # Display test cases
    if st.session_state.test_cases:
        st.markdown("---")
        st.subheader("Generated Test Cases")
        
        for idx, tc in enumerate(st.session_state.test_cases):
            with st.expander(f"**{tc['test_id']}** - {tc['feature']} ({tc['test_type']})", expanded=(idx == 0)):
                st.markdown(f"**Scenario:** {tc['test_scenario']}")
                
                if tc.get('preconditions'):
                    st.markdown(f"**Preconditions:** {tc['preconditions']}")
                
                st.markdown("**Steps:**")
                for step_idx, step in enumerate(tc['steps'], 1):
                    st.markdown(f"{step_idx}. {step}")
                
                st.markdown(f"**Expected Result:** {tc['expected_result']}")
                
                st.markdown(f"**Test Type:** {tc['test_type'].upper()}")
                
                st.markdown(f"**Grounded In:** {', '.join(tc['grounded_in'])}")
                
                if st.button(f"Generate Script for {tc['test_id']}", key=f"gen_script_{idx}"):
                    st.session_state.selected_test_case = tc
                    st.success(f"Selected {tc['test_id']}. Go to 'Generate Scripts' tab.")

# Tab 4: Generate Scripts
with tab4:
    st.header("Generate Selenium Scripts")
    
    if st.session_state.selected_test_case:
        tc = st.session_state.selected_test_case
        
        st.info(f"Selected Test Case: **{tc['test_id']}** - {tc['feature']}")
        
        if st.button("🔧 Generate Selenium Script", type="primary"):
            with st.spinner("Generating Selenium script... This may take 10-20 seconds."):
                result = call_api(
                    "/generate_script",
                    "POST",
                    json_data={"test_case": tc}
                )
                
                if result:
                    st.session_state.generated_script = result
                    st.success(f"✅ Script generated in {result.get('generation_time', 0):.2f}s")
        
        # Display generated script
        if st.session_state.generated_script:
            st.markdown("---")
            st.subheader("Generated Selenium Script")
            
            script = st.session_state.generated_script.get("script", "")
            filename = st.session_state.generated_script.get("filename", "test_script.py")
            
            st.code(script, language="python")
            
            # Download button
            st.download_button(
                label="📥 Download Script",
                data=script,
                file_name=filename,
                mime="text/x-python"
            )
    else:
        st.info("Please select a test case from the 'Generate Test Cases' tab first")
        
        # Allow manual test case selection
        if st.session_state.test_cases:
            st.markdown("---")
            st.subheader("Or select a test case manually:")
            
            test_case_options = [
                f"{tc['test_id']} - {tc['feature']}"
                for tc in st.session_state.test_cases
            ]
            
            selected = st.selectbox("Select Test Case", test_case_options)
            
            if st.button("Use This Test Case"):
                idx = test_case_options.index(selected)
                st.session_state.selected_test_case = st.session_state.test_cases[idx]
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Autonomous QA Agent v1.0 | Powered by FastAPI, Streamlit, ChromaDB, and Gemini</p>
</div>
""", unsafe_allow_html=True)
