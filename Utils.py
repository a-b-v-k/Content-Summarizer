import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
import nltk
import re
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import spacy

@st.cache
def fetch_article_text(url: str):

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    results = soup.find_all(["h1", "p"])
    text = [result.text for result in results]
    ARTICLE = " ".join(text)
    return re.sub(r'\[\d+\]', '', ARTICLE)

def count_tokens(text: str):
    return len(text.split(" "))

@st.cache
def get_text_from_youtube_url(url: str):

    id = url.split("=")[1]
    try:
        transcript = YouTubeTranscriptApi.get_transcript(id)
    except:
        transcript = YouTubeTranscriptApi.find_transcript(["en"])
    script = ""

    for text in transcript:
        t = text["text"]
        if t != '[Music]':
            script += t.lower() + " "
        
    return add_punctuation(script)

def add_punctuation(text: str):

    # try:
    nlp = spacy.load("en_core_web_sm")
    # except:
    #     import spacy.cli
    #     spacy.cli.download("en_core_web_sm")
    #     nlp = spacy.load("en_core_web_sm")
        
    doc = nlp(text)
    punctuation = [".", ",", ";", ":", "?", "!"]

    sentences = []
    for sentence in doc.sents:

        last_token = sentence[-1]
        if last_token.text in punctuation:
            sentence = sentence[:-1]
        
        last_word = sentence[-1]
        if last_word.pos_ == "NOUN":
            sentence = sentence.text + "."
        elif last_word.pos_ == "VERB":
            sentence = sentence.text + "?"
        else:
            sentence = sentence.text + "."

        sentence = sentence[0].upper() + sentence[1:]
        sentences.append(sentence)
        
    text_with_punctuation = " ".join(sentences)

    return text_with_punctuation


def get_input_chunks(text: str, max_length: int = 500):

    text = re.sub(r'\[\d+\]', '', text)

    try:
        nltk.download('punkt_tab')
        sentences = sent_tokenize(text)
    except:
        nltk.download('punkt') 
        sentences = sent_tokenize(text)

    sentences = [sentence for sentence in sentences if len(sentence.strip()) > 0 and count_tokens(sentence) > 4]

    input_chunks = []
    temp_sentences = ""
    tokens = 0

    for sentence in sentences:
        if tokens + count_tokens(sentence) < max_length:
            temp_sentences += sentence
            tokens += count_tokens(sentence)
        else:
            input_chunks.append(temp_sentences)
            tokens = count_tokens(sentence)
            temp_sentences = sentence
        
    if len(temp_sentences) > 0:
        input_chunks.append(temp_sentences)

    return input_chunks
