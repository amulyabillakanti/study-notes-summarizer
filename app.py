import os
import streamlit as st
from google import genai
from pypdf import PdfReader


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Smart Study Notes Summarizer",
    page_icon="📚",
    layout="centered"
)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("📚 Smart Study Notes Summarizer")

st.write(
    "Upload lecture slides, notes (PDF), or paste text to generate "
    "instant revision summaries, key definitions, and flashcards."
)


# --------------------------------------------------
# GEMINI API KEY FROM ENVIRONMENT
# --------------------------------------------------

api_key = os.getenv("GOOGLE_API_KEY")


# --------------------------------------------------
# USER INPUTS
# --------------------------------------------------

input_type = st.radio(
    "Choose input method:",
    ["Paste Text", "Upload PDF"],
    horizontal=True
)

notes_text = ""

if input_type == "Paste Text":
    notes_text = st.text_area(
        "Paste your study material here:",
        height=200,
        placeholder="Paste lecture transcripts, textbook excerpts, or revision topics..."
    )
else:
    uploaded_file = st.file_uploader(
        "Upload your study material (PDF):",
        type=["pdf"]
    )
    if uploaded_file is not None:
        reader = PdfReader(uploaded_file)
        extracted_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
        notes_text = "\n".join(extracted_pages)
        st.success(f"Loaded {len(reader.pages)} pages successfully!")

summary_style = st.selectbox(
    "Select summary format:",
    [
        "Quick Revision Bullet Points",
        "Comprehensive Study Guide with Key Terms & Formulas",
        "Exam-Style Q&A and Flashcards"
    ]
)

generate_btn = st.button("Generate Summary", type="primary")


# --------------------------------------------------
# GENERATE ANSWER
# --------------------------------------------------

if generate_btn:

    if not api_key:
        st.error(
            "GOOGLE_API_KEY environment variable is missing. "
            "Please add it in your Render Service Dashboard under Environment Variables."
        )

    elif not notes_text.strip():
        st.warning("Please provide study text or upload a PDF first.")

    else:
        try:
            with st.spinner("Analyzing material and generating revision notes..."):

                # Create Gemini client
                client = genai.Client(api_key=api_key)

                # Prompt structure
                prompt = f"""
You are an expert academic tutor and exam preparation coach.

Summarize the following study material using this format: {summary_style}.

Ensure the summary:
1. Highlights key definitions, core concepts, and formulas clearly.
2. Uses structured Markdown headings, bold keywords, and bullet points.
3. Keeps explanations concise, student-friendly, and exam-focused.

STUDY MATERIAL:
{notes_text[:12000]}
"""

                # Gemini Model Fallback
                models_to_try = [
                    "gemini-2.5-flash",
                    "gemini-1.5-flash",
                    "gemini-2.0-flash"
                ]

                response = None
                last_error = None
                successful_model = None

                for model_name in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )
                        if response.text:
                            successful_model = model_name
                            break
                    except Exception as e:
                        last_error = e
                        continue

                # If all models fail
                if response is None or not response.text:
                    raise Exception(
                        "All Gemini models are temporarily unavailable. "
                        f"Please try again later. Last error: {last_error}"
                    )

                # Display Output
                st.subheader("📝 Generated Summary:")
                st.markdown(response.text)

                st.caption(f"Generated using: {successful_model}")

        except Exception as e:
            st.error(f"Error processing notes: {e}")
