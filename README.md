---
title: Content Summarizer
emoji: 🔥
colorFrom: purple
colorTo: green
sdk: streamlit
sdk_version: 1.20.0
app_file: app.py
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

### Content Summarizer

The Content Summarizer is a project that can generate summaries for various types of content including text, URLs, audio, video, and YouTube. It utilizes the transformers library and leverages the BART-large-CNN, T5-small and Whisper-tiny.en models to provide effective summarization.

It contains two options for summarization:
 - Overall summary
 - Auto-Chapters summary

#### Overall summary 
The overall summary is generated using BART-large-CNN with chunk split algorithm.

#### Auto Chapters summary
In this type, the text content is split using clustering techniques and chunk split algorithm and uses BART-large-CNN and T5-small for summarization which gives blocks of summary with headings for each.

To run the app, install the packages from requirements.txt and execute the command `streamlit run app.py` from the root of this project.

This repository has also been added as a space in huggingface: https://huggingface.co/spaces/KevlarVK/content_summarizer
