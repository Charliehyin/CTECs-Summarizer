from flask import Blueprint, request, jsonify
import os
from typing import List, Tuple
import re
import json

ner_bp = Blueprint('ner', __name__)

@ner_bp.route('/ner', methods=['GET'])
def ner():
    query = request.json.get('message')
    if not query:
        return jsonify({"error": "Missing message in request"}), 400

    try: 
        with open("course_keywords/course_keywords.json", "r") as f:
            course_data = json.load(f)

        # File paths (adjust if needed)
        COURSE_NUMBERS_FILE   = 'course_keywords/course_numbers.txt'
        PROFESSOR_NAMES_FILE  = 'course_keywords/professor_names.txt'

        # Load lists
        course_numbers   = set(load_list(COURSE_NUMBERS_FILE))
        professor_names  = set(load_list(PROFESSOR_NAMES_FILE))

        def course_matching(paragraph: str) -> Tuple[List[str], List[str], List[str]]:
            """
            Highlight exact course numbers and professor names, and fuzzy-match course names.

            Args:
                paragraph: The input text to search.

            Returns:
                Tuple of three lists:
                - matched course numbers
                - matched course names
                - matched professor names
            """
            # --- Exact matches for course numbers & professors
            matched_numbers = [num for num in course_numbers if num in paragraph]
            matched_profs   = [prof for prof in professor_names if contains_word(paragraph, prof)]
            matched_courses = match_courses_by_keywords(paragraph, course_data)

            return matched_numbers, sorted(matched_courses), matched_profs
        
        matched_numbers, matched_courses, matched_profs = course_matching(query)

        return jsonify({
            "numbers": matched_numbers,
            "courses": matched_courses,
            "professors": matched_profs
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def match_courses_by_keywords(text, json_data):
    text_lower = text.lower()
    course_scores = []

    # Build a list of (course_name, abbreviation_matched, keyword_match_count)
    for course_name, info in json_data.items():
        abbreviations = info.get("abbreviations", [])
        keywords = info.get("keywords", [])

        # Check if any abbreviation matches as a whole word
        abbreviation_matched = any(
            re.search(r'\b{}\b'.format(re.escape(abbrev)), text_lower)
            for abbrev in abbreviations
        )

        # Count keyword matches (whole word)
        keyword_matches = sum(
            1 for kw in keywords
            if re.search(r'\b{}\b'.format(re.escape(kw)), text_lower)
        )

        course_scores.append((course_name, abbreviation_matched, keyword_matches))

    # Try increasing keyword threshold until <= 10 matches
    for keyword_threshold in range(1, 4):
        if 'filtered' in locals():
            old = filtered
        filtered = [
            (name, keyword_matches)
            for name, abbrev_match, keyword_matches in course_scores
            if abbrev_match or keyword_matches >= keyword_threshold
        ]
        if len(filtered) == 0 and 'old' in locals():
            filtered = old
            break
        if len(filtered) <= 6:
            break

    # Sort matches by keyword count, descending
    filtered.sort(key=lambda x: x[1], reverse=True)

    # Return only course names, limited to 10
    return [name for name, _ in filtered[:6]]

def contains_word(text, word):
    pattern = r'\b{}\b'.format(re.escape(word))
    return re.search(pattern, text) is not None

def load_list(file_path: str) -> List[str]:
    """
    Load line-separated items from a text file, stripping whitespace.
    """
    if not os.path.isfile(file_path):
        print(f"Warning: file not found: {file_path}")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]
    

