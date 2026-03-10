# Run the app using:
# streamlit run app.py


# ================================
# Import Required Libraries
# ================================

from langchain_groq import ChatGroq      # Groq LLM integration
from dotenv import load_dotenv           # Load environment variables
import streamlit as st                   # Streamlit UI framework

# Voice input libraries
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import tempfile

# Clipboard library for copy button
import pyperclip


# ================================
# Load Environment Variables
# ================================
load_dotenv()

# Initialize Groq LLM model
model = ChatGroq(model="llama-3.1-8b-instant")


# ================================
# App Title
# ================================

st.title("🌐 Indian Language Translator")
st.caption("Translate between 22+ Indian languages using Llama 3")


# ================================
# Initialize Session State
# ================================
# Session state is used to preserve values across reruns

if "lang1" not in st.session_state:
    st.session_state.lang1 = "English"

if "lang2" not in st.session_state:
    st.session_state.lang2 = "Hindi"


# ================================
# Function to Swap Languages
# ================================

def swap_languages():
    st.session_state.lang1, st.session_state.lang2 = (
        st.session_state.lang2,
        st.session_state.lang1,
    )


# ================================
# Language Options (22+ Indian Languages)
# ================================

languages = [
    "Assamese","Bengali","Bodo","Dogri","Gujarati","Hindi",
    "Kannada","Kashmiri","Konkani","Maithili","Malayalam",
    "Manipuri","Marathi","Nepali","Odia","Punjabi","Sanskrit",
    "Santali","Sindhi","Tamil","Telugu","Urdu","English"
]


# ================================
# Language Selection Layout
# ================================

col1, col2, col3 = st.columns([4,1,4])

# Source language
with col1:
    language1 = st.selectbox(
        "From",
        languages,
        key="lang1"
    )

# Swap button
with col2:
    st.write("")
    st.write("")
    st.button("🔄", on_click=swap_languages)

# Target language
with col3:
    language2 = st.selectbox(
        "To",
        languages,
        key="lang2"
    )


# ================================
# Voice Input Section
# ================================

st.subheader("🎤 Voice Input")

# Store user input in session state
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Text input box
user_input = st.text_area("Enter text", key="user_input")

st.write("OR")

# Record audio using microphone
audio = mic_recorder(
    start_prompt="Start Recording",
    stop_prompt="Stop Recording",
    key="recorder"
)


# ================================
# Convert Voice → Text
# ================================

if audio:
    recognizer = sr.Recognizer()

    # Save recorded audio to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio["bytes"])
        audio_path = tmp_file.name

    # Load audio for speech recognition
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)

    try:
        # Convert speech to text using Google Speech Recognition
        text = recognizer.recognize_google(audio_data)

        st.success(f"Recognized Text: {text}")

        # Automatically fill input text area
        st.session_state.user_input = text

    except Exception as e:
        st.error("Could not recognize speech")


# ================================
# Translation Section
# ================================

if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

# Translate button
if st.button("🔁 Convert"):

    # Input validation
    if user_input.strip() == "":
        st.warning("Please enter some text")

    elif language1 == language2:
        st.warning("Please select different languages")

    else:

        # Prompt for LLM translation
        prompt = f"""You are an expert translator for Indian languages.

        Translate the following text from {language1} to {language2}.

        Rules:
        - Return ONLY the translated text
        - Do not explain anything
        - Preserve the meaning exactly

        Text:
        {user_input}
        """

        # Show loading spinner during translation
        with st.spinner("Translating..."):
            response = model.invoke(prompt)

        # Store translation in session state
        st.session_state.translated_text = response.content


# ================================
# Display Translation Output
# ================================

if st.session_state.translated_text:

    st.subheader("Translation")

    col1, col2 = st.columns([10,1])

    # Show translated text
    with col1:
        st.text_area(
            "Translated Text",
            st.session_state.translated_text,
            height=150
        )

    # Copy to clipboard button
    with col2:
        if st.button("📋", help="Copy to clipboard"):
            pyperclip.copy(st.session_state.translated_text)
            st.toast("Copied!")