import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from deep_translator import GoogleTranslator
import torch

@st.cache_resource
def load_summarizer():
    model_name = "t5-small"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

summarize_tokenizer, summarize_model = load_summarizer()

def generate_summary(text, length="Medium"):
    # Refined length mapping for independent generation
    length_map = {
        "Extra Short": {"max": 20, "min": 5},
        "Short": {"max": 45, "min": 20},
        "Medium": {"max": 90, "min": 45},
        "Detailed": {"max": 200, "min": 90}
    }
    
    settings = length_map.get(length, length_map["Medium"])
    
    # Prefix for T5
    input_text = "summarize: " + text
    
    # Tokenize
    inputs = summarize_tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    
    # Generate with high repetition penalty for unique, independent summaries
    summary_ids = summarize_model.generate(
        inputs["input_ids"],
        max_length=settings["max"],
        min_length=settings["min"],
        length_penalty=2.0,
        num_beams=4,
        repetition_penalty=2.5,
        no_repeat_ngram_size=3,
        early_stopping=True
    )
    
    return summarize_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

import trafilatura

def extract_text_from_url(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        result = trafilatura.extract(downloaded)
        return result
    return None

def translate_text(text, target_lang):
    if target_lang == "English":
        return text
    
    lang_codes = {
        "Hindi": "hi",
        "Tamil": "ta"
    }
    
    if target_lang not in lang_codes:
        return text

    try:
        # Use deep-translator for instant and high-quality translation
        translated = GoogleTranslator(source='auto', target=lang_codes[target_lang]).translate(text)
        return translated
    except Exception as e:
        st.error(f"Translation Error: {e}")
        return text
