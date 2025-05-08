from flask import Blueprint, request, jsonify
from config.config import load_config
from scripts.compute_embeddings import split_by_newline, retrieve_sbert
import pickle
import json
import numpy as np
from utils.connect_db import get_db_connection

rag_bp = Blueprint('rag', __name__)
config = load_config()

# Get course_ids based on metadata values
def get_course_ids_from_metadata(metadata_list, conn):
    cursor = conn.cursor()

    format_strings = ','.join(['%s'] * len(metadata_list))
    query = f"SELECT DISTINCT course_id FROM course_metadata WHERE metadata_value IN ({format_strings})"
    cursor.execute(query, metadata_list)
    course_ids = [row[0] for row in cursor.fetchall()]

    cursor.close()
    return course_ids

# Get essays and embeddings based on course_ids
def get_filtered_essays(course_ids, conn):
    cursor = conn.cursor()

    format_strings = ','.join(['%s'] * len(course_ids))
    query = f"SELECT essay_id, response, embedding FROM Course_Essays_With_Embeddings WHERE course_id IN ({format_strings})"
    cursor.execute(query, course_ids)
    rows = cursor.fetchall()

    cursor.close()

    return rows

@rag_bp.route('/rag', methods=['POST'])
def rag():
    query = request.json.get('message')
    top_k = request.json.get('top_k', 10)
    metadata_filters = request.json.get('metadata', [])  # Changed parameter name to match chat.py

    conn = get_db_connection()

    if not query:
        return jsonify({"error": "Missing message in request"}), 400

    try:
        essay_texts = []
        filtered_embeddings = []

        # Get course_ids from metadata filters and fetch essays
        if metadata_filters:
            course_ids = get_course_ids_from_metadata(metadata_filters, conn)
            if course_ids:
                filtered_essays = get_filtered_essays(course_ids, conn)
                for essay_id, response, embedding_json in filtered_essays:
                    essay_texts.append(response)
                    embedding_vector = np.array(json.loads(embedding_json), dtype=np.float32)  # Explicitly convert to float32
                    filtered_embeddings.append(embedding_vector)

        if not essay_texts:
            # Fallback to full corpus
            with open("summary_corpus.txt", "r", encoding="utf-8") as file:
                summary_corpus = split_by_newline(file.read())
            summary_corpus_embeddings = pickle.load(open("summary_corpus_embeddings.pkl", "rb"))
            with open("essay_corpus.txt", "r", encoding="utf-8") as file:
                essay_texts = split_by_newline(file.read())
            filtered_embeddings = pickle.load(open("essay_corpus_embeddings.pkl", "rb"))

        # Convert filtered_embeddings to the correct dtype if it's a numpy array
        if isinstance(filtered_embeddings, np.ndarray):
            filtered_embeddings = filtered_embeddings.astype(np.float32)
            
        # Retrieve results
        top_chunks_essay = retrieve_sbert(query, essay_texts, filtered_embeddings, top_k=top_k)
        # top_chunks_summary = retrieve_sbert(query, summary_corpus, summary_corpus_embeddings, top_k=3) # TODO: Course table needs a new column for embedded version 
        top_chunks_summary = []

        top_chunks = top_chunks_essay + top_chunks_summary

        combined_text = ""
        for _, _, text in top_chunks:
            combined_text += text + "\n\n"

        top_chunks_string = combined_text.strip()

        return jsonify({"response": top_chunks_string}), 200

    except Exception as e:
        print(f"Detailed RAG error: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full stack trace
        return jsonify({"error": f"RAG error: {str(e)}"}), 500
    
    finally:
        conn.close()