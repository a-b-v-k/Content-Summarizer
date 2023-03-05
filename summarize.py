from datetime import datetime
from transformers import BartTokenizer, TFBartForConditionalGeneration, pipeline
from Utils import fetch_article_text, count_tokens
import re
from nltk.tokenize import sent_tokenize
import nltk

tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
model = TFBartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

def bart_summarize(text: str):

    max_length = model.config.max_position_embeddings

    try:
        sentences = sent_tokenize(text)
    except:
        nltk.download('punkt') 
        sentences = sent_tokenize(text)
    sentences = [sentence for sentence in sentences if len(sentence.strip()) > 0 and len(sentence.split(" ")) > 4]

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

    # summarize each input chunk separately
    summaries = []
    print(datetime.now().strftime("%H:%M:%S"))
    for chunk in input_chunks:
        # encode the input chunk

        encoded_input = tokenizer.encode(chunk, max_length=max_length, return_tensors='tf')
        
        # generate summary for the input chunk
        summary_ids = model.generate(encoded_input, max_length=300, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        # add the summary to the list of summaries
        summaries.append(summary)

        print(summary)
        
    # # combine the summaries to get the final summary for the entire input
    final_summary = " ".join(summaries)

    print(datetime.now().strftime("%H:%M:%S"))

    return final_summary