import streamlit as st
from summarize import bart_summarize

# Create a text field
text = st.text_input("Enter text here")

# Create a button
button = st.button("Click here")

# get text from text field and print it
if button:
    summary = bart_summarize(text)
    st.write(summary)