# -*- coding: utf-8 -*-
"""app.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1X85a4bgcXZ8Qz7_4JP4KMubIY8rkiKz6
"""
import os
import subprocess

# Clone the MeloTTS repository
subprocess.run(["git", "clone", "https://github.com/myshell-ai/MeloTTS.git"])


# %cd MeloTTS

# !pip install transformers torch --upgrade
# !pip install gradio elevenlabs groq streamlit

# !pip install cn2an pypinyin num2words pykakasi mecab-python3 unidic-lite fugashi g2p_en

# !pip install anyascii jamo gruut cached_path
# !python -m unidic download

import streamlit as st
import re
import os
from groq import Groq
from melo.api import TTS

# Initialize MeloTTS model
import torch
from melo.api import TTS
from melo.app import speaker_ids
device = 'auto'

model = TTS(language='EN', device=device)
speaker_ids = model.hps.data.spk2id

# Directory to save audio files
AUDIO_DIR = 'static'
os.makedirs(AUDIO_DIR, exist_ok=True)

# Initialize Groq API settings
# Access the Groq API key from Streamlit secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
groq_client = Groq(api_key=GROQ_API_KEY)

def clean_text_for_tts(text):
    # Replace or remove unwanted characters
    clean_text = re.sub(r'\*\*', '', text)  # Remove double asterisks
    clean_text = re.sub(r'\*', '', clean_text)  # Remove single asterisks
    clean_text = re.sub(r'•', '', clean_text)  # Remove bullet points
    clean_text = re.sub(r'(\d+\.)', '', clean_text)  # Remove numbers followed by a period (like "1.")
    clean_text = re.sub(r'\n', ' ', clean_text)  # Replace newlines with spaces

    # Additional replacements can be done here as needed
    return clean_text

def generate_podcast_content(prompt):
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192"
        )
        content = response.choices[0].message.content
        # Truncate content to 10000 characters
        if len(content) > 9000:
            content = content[:9000]
        return content
    except Exception as e:
        print(f"Error in generate_podcast_content: {e}")
        return "Error generating content."

def text_to_speech(text):
    try:
        # Clean the text
        cleaned_text = clean_text_for_tts(text)

        # Initialize MeloTTS model
        model = TTS(language='EN', device='auto')  # Set language to English

        # Get speaker IDs
        speaker_ids = model.speaker_ids

        # Convert text to speech
        output_path = 'podcast.wav'
        model.tts_to_file(cleaned_text, speaker_ids['EN-US'], output_path, speed=1.0)

        # Return the audio file path
        return output_path
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        return None

# Create Streamlit app
import streamlit as st

st.title("Podcast Creator")
prompt_input = st.text_input("Enter Podcast Prompt", placeholder="Type your podcast prompt here...")
create_button = st.button("Create Podcast")

if create_button:
    content = generate_podcast_content(prompt_input)
    audio_file_path = text_to_speech(content)
    st.write("Generated Content:")
    st.write(content)
    st.audio(audio_file_path)

# !streamlit run app.py