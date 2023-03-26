from datetime import datetime
from transformers import BartTokenizer, TFBartForConditionalGeneration
from Utils import get_input_chunks
import networkx as nx
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import community


class BARTSummarizer:

    def __init__(self, model_name: str = 'facebook/bart-large-cnn'):
        self.model_name = model_name
        self.tokenizer = BartTokenizer.from_pretrained(model_name)
        self.model = TFBartForConditionalGeneration.from_pretrained(model_name)
        self.max_length = self.model.config.max_position_embeddings

    def summarize(self, text: str):
        encoded_input = self.tokenizer.encode(text, max_length=self.max_length, return_tensors='tf', truncation=True)
        summary_ids = self.model.generate(encoded_input, max_length=300, num_beams=4, early_stopping=True, min_length=70)
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary
    
    def chunk_summarize(self, text: str):

        # split the input into chunks
        summaries = []
        input_chunks = get_input_chunks(text, self.max_length)

        # summarize each input chunk separately
        print(datetime.now().strftime("%H:%M:%S"))
        for chunk in input_chunks:
            summaries.append(self.summarize(chunk))
            
        # # combine the summaries to get the final summary for the entire input
        final_summary = " ".join(summaries)

        print(datetime.now().strftime("%H:%M:%S"))

        return final_summary
    
    def preprocess_for_auto_chapters(self, text: str):
       
        # Tokenize the text into sentences
        sentences = sent_tokenize(text)

        # Filter out empty sentences and sentences with less than 5 words
        sentences = [sentence for sentence in sentences if len(sentence.strip()) > 0 and len(sentence.split(" ")) > 4]

        # Combine every 5 sentences into a single sentence
        sentences = [' '.join(sentences[i:i + 5]) for i in range(0, len(sentences), 5)]

        return sentences
    
    def auto_chapters_summarize(self, text: str):

        sentences = self.preprocess_for_auto_chapters(text)

        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(sentences)

        # Compute the similarity matrix using cosine similarity
        similarity_matrix = X * X.T

        # Convert the similarity matrix to a graph
        graph = nx.from_scipy_sparse_array(similarity_matrix)

        # Apply the Louvain algorithm to identify communities
        partition = community.best_partition(graph, resolution=0.7, random_state=42)

        # Cluster the sentences
        clustered_sentences = []
        for cluster in set(partition.values()):
            sentences_to_print = []
            for i, sentence in enumerate(sentences):
                if partition[i] == cluster:
                    sentences_to_print.append(sentence)
            if len(sentences_to_print) > 1:
                clustered_sentences.append(" ".join(sentences_to_print))
        
        # Summarize each cluster
        summaries = []
        for cluster in clustered_sentences:
            summaries.append(self.chunk_summarize(cluster))

        # Combine the summaries to get the final summary for the entire input
        final_summary = "\n\n".join(summaries)
    
