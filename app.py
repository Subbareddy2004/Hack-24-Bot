import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import PyPDF2
import io

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Custom CSS with improved styling
def local_css():
    st.markdown("""
        <style>
        /* Global Styles */
        .main {
            background: linear-gradient(135deg, #f0f4fd 0%, #e2eafc 100%);
            padding: 1.5rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* Header Styles */
        .header-container {
            background: linear-gradient(120deg, #1a73e8 0%, #4285f4 50%, #34a5ff 100%);
            padding: 2.5rem;
            border-radius: 25px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 20px rgba(26, 115, 232, 0.15);
            text-align: center;
        }
        
        .header-title {
            color: white;
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            letter-spacing: -0.5px;
        }
        
        .header-subtitle {
            color: rgba(255,255,255,0.95);
            font-size: 1.3rem;
            font-weight: 400;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.5;
        }
        
        /* Card Styles */
        .card {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
            border: 1px solid rgba(226, 232, 240, 0.8);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.08);
        }
        
        /* Button Styles */
        .stButton>button {
            background: linear-gradient(120deg, #1a73e8 0%, #4285f4 100%);
            color: white;
            border-radius: 12px;
            padding: 0.8rem 1.5rem;
            border: none;
            font-weight: 600;
            letter-spacing: 0.3px;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 1rem;
            text-transform: uppercase;
            font-size: 0.9rem;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(26, 115, 232, 0.2);
            background: linear-gradient(120deg, #1557b0 0%, #2b6cd4 100%);
        }
        
        /* Input Field Styles */
        .stTextInput>div>div>input {
            border-radius: 12px;
            border: 2px solid #e2e8f0;
            padding: 1rem 1.2rem;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: #f8fafc;
        }
        
        .stTextInput>div>div>input:focus {
            border-color: #4285f4;
            box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.15);
            background: white;
        }
        
        /* File Uploader Styles */
        .upload-container {
            border: 2px dashed #4285f4;
            border-radius: 20px;
            padding: 2.5rem;
            text-align: center;
            background: rgba(66, 133, 244, 0.03);
            transition: all 0.3s ease;
        }
        
        .upload-container:hover {
            background: rgba(66, 133, 244, 0.06);
            border-color: #1a73e8;
        }
        
        /* Response Styles */
        .response-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            margin: 1.5rem 0;
            border-left: 5px solid #4285f4;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            animation: slideIn 0.5s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Intelligence Level Styles */
        .intelligence-container {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(226, 232, 240, 0.8);
        }
        
        .intelligence-title {
            color: #1a73e8;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        /* Slider Styles */
        .stSlider {
            padding: 1rem 0;
        }
        
        .stSlider > div > div > div > div {
            background-color: #4285f4 !important;
        }
        
        /* Success Message */
        .success-message {
            background: linear-gradient(120deg, #34a853 0%, #4caf50 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            text-align: center;
            animation: fadeIn 0.5s ease-out;
            margin: 1rem 0;
            font-weight: 500;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Section Titles */
        .section-title {
            color: #1a73e8;
            font-size: 1.5rem;
            font-weight: 600;
            margin: 1.5rem 0 1rem 0;
            letter-spacing: -0.3px;
        }
        
        /* Help Text */
        .help-text {
            color: #64748b;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        
        /* Spinner */
        .stSpinner {
            text-align: center;
            color: #4285f4;
        }
        </style>
    """, unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    with st.spinner("📄 Processing your document..."):
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_gemini_response(input_text, prompt, difficulty):
    difficulty_prompts = {
        "Easy": "Explain this in simple, easy-to-understand terms, suitable for beginners: ",
        "Medium": "Provide a balanced explanation with moderate technical detail: ",
        "Professional": "Give an in-depth, technical analysis with professional terminology and advanced concepts: "
    }
    full_prompt = f"{difficulty_prompts[difficulty]}\n{prompt}"
    response = model.generate_content([input_text, full_prompt])
    return response.text

def main():
    st.set_page_config(
        page_title="SmartDoc AI",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    local_css()

    # Header Section
    st.markdown("""
        <div class="header-container">
            <h1 class="header-title">SmartDoc AI</h1>
            <p class="header-subtitle">Transform your documents into intelligent insights</p>
        </div>
    """, unsafe_allow_html=True)

    # Main content columns
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "📄 Upload your document",
            type=['pdf'],
            help="Maximum file size: 200MB • Supported format: PDF"
        )
        
        if uploaded_file is not None:
            document_text = extract_text_from_pdf(uploaded_file)
            st.session_state.document_text = document_text
            st.markdown(
                '<div class="success-message">✨ Document processed successfully!</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="intelligence-title">🎯 Intelligence Level</p>', unsafe_allow_html=True)
        difficulty = st.select_slider(
            "Select response complexity",
            options=["Easy", "Medium", "Professional"],
            value="Medium",
            help="Adjust the depth and complexity of AI responses"
        )
        st.markdown('<p class="help-text">Slide to adjust the complexity of responses</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if 'document_text' in st.session_state and st.session_state.document_text:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        if st.button("📊 Generate Smart Summary", use_container_width=True):
            with st.spinner("Analyzing your document..."):
                summary_prompt = "Please provide a comprehensive summary of the following text:"
                summary = get_gemini_response(st.session_state.document_text, summary_prompt, difficulty)
                st.markdown('<p class="section-title">📑 Document Summary</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="response-card">{summary}</div>', unsafe_allow_html=True)

        st.markdown('<p class="section-title">💡 Ask Questions</p>', unsafe_allow_html=True)
        user_question = st.text_input(
            "What would you like to know?",
            placeholder="Enter your question here...",
            help="Ask any question about your document content"
        )
        
        if user_question and st.button("🔍 Get Answer", use_container_width=True):
            with st.spinner("Finding insights..."):
                qa_prompt = f"Based on the following document, please answer this question: {user_question}\n\nDocument content:"
                answer = get_gemini_response(st.session_state.document_text, qa_prompt, difficulty)
                st.markdown(f'<div class="response-card">{answer}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()