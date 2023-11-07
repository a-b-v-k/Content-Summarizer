import io
from process_media import MediaProcessor
import streamlit as st
from summarizer import BARTSummarizer
from  Utils import fetch_article_text, get_text_from_youtube_url
from pytube import YouTube

def generate_summary(overall_summary, auto_chapters_summarize, text_to_summarize, show_text = False):
    if overall_summary:
        with st.spinner("Generating overall summary..."):
            summarizer = BARTSummarizer()
            summary = summarizer.chunk_summarize(text_to_summarize)
    elif auto_chapters_summarize:
        with st.spinner("Generating auto chapters summary..."):
            summarizer = BARTSummarizer()
            summary = summarizer.auto_chapters_summarize(text_to_summarize)
    if show_text:
        st.markdown("#### Text before summarization:")
        st.markdown('<div style="height: 500px; overflow: auto; margin-bottom: 20px;">' + text_to_summarize + '</div>', unsafe_allow_html=True)
    st.markdown("#### Summary:")
    st.write(summary)

def show_buttons(type, data = None):
    text_to_summarize = None
    overall_summary = st.button("Overall summary")
    auto_chapters_summary = st.button("Auto Chapters summary...")

    if type == "raw_text" or type == "url" and data:
        if overall_summary or auto_chapters_summary:
            if type == "raw_text":
                text_to_summarize = data
                generate_summary(overall_summary, auto_chapters_summary, text_to_summarize)
            elif type == "url":
                text_to_summarize = fetch_article_text(data)
                generate_summary(overall_summary, auto_chapters_summary, text_to_summarize, show_text = True)

    elif type == "audio_file" and data:
        if overall_summary or auto_chapters_summary:
            with st.spinner("Fetching text from audio..."):
                text_to_summarize = process_audio_file(data)
            generate_summary(overall_summary, auto_chapters_summary, text_to_summarize, show_text = True)

    elif type == "video_file" and data:
        if overall_summary or auto_chapters_summary:
            with st.spinner("Fetching text from video..."):
                text_to_summarize = process_video_file(data)
            generate_summary(overall_summary, auto_chapters_summary, text_to_summarize, show_text = True)

    elif type == "youtube_url" and data:
        if overall_summary or auto_chapters_summary:
            try:
                try:
                    with st.spinner("Fetching text from video..."):
                        text_to_summarize = get_text_from_youtube_url(data)
                except:
                    with st.spinner("Captions not available. Downloading video..."):
                        text_to_summarize = get_yt_video(data)
            except:
                st.error("Unable to fetch text from video. Please try a different video.")
                text_to_summarize = None
            if text_to_summarize:
                generate_summary(overall_summary, auto_chapters_summary, text_to_summarize, show_text = True)
    elif type == 'document':
        # TODO: Add document summary
        pass


def process_video_file(video_file):
    media_processor = MediaProcessor()
    text = media_processor.process_video(video_file.read())
    return text

def process_audio_file(audio_file):
    media_processor = MediaProcessor()
    if audio_file.type == "audio/mpeg":
        wav_bytes = media_processor.get_wav_from_audio(audio_file.read())
    else:
        wav_bytes = audio_file.read()
    text = media_processor.process_audio(wav_bytes)
    return text

def get_yt_video(youtube_url):
    yt = YouTube(youtube_url)
    video_stream = yt.streams.first()
    video_buffer = io.BytesIO()
    video_stream.stream_to_buffer(video_buffer)
    media_processor = MediaProcessor()
    text = media_processor.process_video(video_buffer.getvalue())
    return text

st.markdown(
"""
<style>
section[data-testid="stSidebar"]  div[role="radiogroup"] label {
    padding: 0px 0px 20px 20px;
}
section[data-testid="stSidebar"] h2 {
    margin: 10px;
}
section.main div[role="radiogroup"] label {
    padding: 10px 10px 10px 0px;
}
</style>
""",
unsafe_allow_html=True,
)

with st.sidebar:
    st.header("CHOOSE INPUT TYPE")
    input_type = st.radio("", ["Text", "Media"], label_visibility = "hidden")

if input_type == "Text":

    st.header("Summarize from text or URL")

    text_type = st.radio("", ["Raw Text", "URL", "Document"], key="text_type", horizontal=True, label_visibility = "hidden")

    if text_type == "Raw Text":
        text = st.text_area("Enter raw text here", height=240, max_chars=10000, placeholder="Enter a paragraph to summarize")
        if text:
            show_buttons("raw_text", text)
        
    elif text_type == "URL":
        url = st.text_input("Enter URL here", placeholder="Enter URL to an article, blog post, etc.")
        if url:
            show_buttons("url", url)
    else:
        ## TODO: Add file upload option
        pass

elif input_type == "Media":

    st.header("Summarize from file or YouTube URL")

    media_type = st.radio("", ["Audio file", "Video file", "Youtube video link"], key="media_type", horizontal=True, label_visibility = "hidden")

    if media_type == "Audio file":
        audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav"], label_visibility="visible")
        if audio_file is not None:
            show_buttons("audio_file", audio_file)

    elif media_type == "Video file":
        video_file = st.file_uploader("Upload a video file", type=["mp4"], label_visibility="visible")
        if video_file is not None:
            show_buttons("video_file", video_file)

    else:
        youtube_url = st.text_input("Enter YouTube URL here", placeholder="Enter URL to an YouTube video", label_visibility="visible")
        if youtube_url:
            show_buttons("youtube_url", youtube_url)
            
            