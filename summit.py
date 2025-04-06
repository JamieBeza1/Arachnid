# summarizer model for mass content found from hacker news

from transformers import pipeline
import math

class Summary:
    def __init__(self):
        self.summariser = pipeline("summarization", model="facebook/bart-large-cnn")
        
    def chunker(self, text, chunk_size=500):
        words = text.split()
        num_chunks = math.ceil(len(words) / chunk_size)
        chunks = [words[i * chunk_size:(i + 1) * chunk_size] for i in range(num_chunks)]
        return [" ".join(chunk) for chunk in chunks]
        
    def summarise_text(self, text):
        if not text or len(text.split()) < 10:
            #print(text)
            return "Text too short to summarise."
        
        try:
            chunks = self.chunker(text, chunk_size=500)
            summaries = []
            
            for chunk in chunks:
                summary = self. summariser(chunk, max_length=400, min_length=100, do_sample=False)
                if summary and "summary_text" in summary[0]:
                    summaries.append(summary[0]['summary_text'])
                else:
                    print(f"Summarisation failed for chunk: {chunk}")
                    
            final_sum = " ".join(summaries)
            return final_sum
        except Exception as e:
            print(f"Error during summarisation: {e}")
            return "Error - No summary available."
            
            