import numpy as np
from sentence_transformers import SentenceTransformer, util
import pickle
import re
# Load SBERT Model (Only Once)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Change chunk_size by changing the input argument
def split_into_corpus(text, chunk_size=512):
    # Use regular expression to Replace multiple spaces, newlines, and tabs with a single space
    cleaned_text = re.sub(r"\s+", " ", text).strip()
    # Split into chunks of exactly `chunk_size`
    return [cleaned_text[i:i+chunk_size] for i in range(0, len(cleaned_text), chunk_size)]

def split_by_newline(text):
    return text.split("\n")

def compute_corpus_embeddings(corpus):
    """
    Computes embeddings for the corpus.
    No file-saving logic, just returns the embeddings.
    """
    corpus_embeddings = embedding_model.encode(corpus, convert_to_tensor=True)
    return corpus_embeddings

def retrieve_sbert(query, corpus, corpus_embeddings, top_k=5):
    """care
    Retrieves the most relevant course review chunks using SBERT embeddings only.
    :param query: User's search query
    :param corpus: The list of text chunks to search in.
    :param corpus_embeddings: Precomputed embeddings for corpus.
    :param top_k: Number of results to return.
    :return: List of (chunk_index, score, text)
    """
    # Compute Query Embedding
    query_embedding = embedding_model.encode(query, convert_to_tensor=True)

    # Compute Cosine Similarity Between Query & Corpus
    similarity_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0].cpu().numpy()

    # Get Top-k Indices Sorted by Similarity Score
    top_k_indices = np.argsort(-similarity_scores)[:top_k]

    # Return Top-k Results as Tuples
    return [(int(top_k_indices[i]), float(similarity_scores[top_k_indices[i]]), corpus[top_k_indices[i]]) for i in range(top_k)]

if __name__ == "__main__":
    # Read corpus from file
    with open("course_essays.txt", "r", encoding="utf-8") as file:
        essay_corpus = split_by_newline(file.read())
    with open("course_summary.txt", "r", encoding="utf-8") as file:
        summary_corpus = split_by_newline(file.read())

    corpus = essay_corpus + summary_corpus
    print("Created corpus:", len(corpus))

    with open("corpus.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(corpus))

    # Compute corpus embeddings
    corpus_embeddings = compute_corpus_embeddings(corpus)
    print("Computed corpus embeddings:", len(corpus_embeddings))

    # Save corpus embeddings to file
    with open("corpus_embeddings.pkl", "wb") as file:
        pickle.dump(corpus_embeddings, file)
