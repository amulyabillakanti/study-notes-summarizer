import streamlit as st
from pypdf import PdfReader
from google import genai
import os

# Page Configuration
st.set_page_config(page_title="Smart Study Notes Summarizer", page_icon="📚", layout="centered")

st.title("Smart Study Notes Summarizer")
st.write("Upload lecture slides, notes (PDF), or paste text to generate instant revision summaries and key concepts.")

# Sidebar for API Key (or loaded from environment)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter your Gemini API Key:", type="password")

# Content Input Options
input_type = st.radio("Choose input method:", ["Paste Text", "Upload PDF"], horizontal=True)
notes_text = ""

if input_type == "Paste Text":
    notes_text = st.text_area("Paste your study material here:", height=220)
else:
    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
    if uploaded_file is not None:
        reader = PdfReader(uploaded_file)
        extracted_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
        notes_text = "\n".join(extracted_pages)
        st.success(f"Loaded {len(reader.pages)} pages successfully!")

# Action Options
summary_style = st.selectbox(
    "Select summary format:",
    [
        "Quick Revision Bullet Points",
        "Comprehensive Study Guide with Key Terms",
        "Exam-Style Q&A and Flashcards"
    ]
)

if st.button("Generate Summary", type="primary"):
    if not api_key:
        st.error("Please provide a Gemini API Key to continue.")
    elif not notes_text.strip():
        st.warning("Please paste text or upload a document first.")
    else:
        with st.spinner("Analyzing and summarizing your notes..."):
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""
                You are an expert academic tutor. Summarize the following study material using this style: {summary_style}.
                Make sure the output is structured, clear, and highlights essential definitions, formulas, or concepts.

                Study Notes:
                {notes_text[:12000]}
                """
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                st.markdown("### 📝 Generated Summary")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error processing notes: {e}")
