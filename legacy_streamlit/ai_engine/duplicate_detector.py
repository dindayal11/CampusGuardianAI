from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def find_similar_complaints(new_title, new_description, existing_complaints):

    # Combine new complaint text
    new_text = f"{new_title} {new_description}".lower()

    # If database has no complaints
    if not existing_complaints:

        return {
            "is_duplicate": False,
            "similarity_score": 0.0,
            "similar_complaints": [],
            "similar_count": 0,
            "impact_level": "Low"
        }

    complaint_texts = []
    complaint_data = []

    # Prepare existing complaint texts
    for complaint in existing_complaints:

        title = complaint[2]
        description = complaint[3]

        text = f"{title} {description}".lower()

        complaint_texts.append(text)

        complaint_data.append({
            "complaint_id": complaint[1],
            "title": title,
            "description": description
        })

    # Add new complaint to comparison list
    all_texts = complaint_texts + [new_text]

    # Convert text to TF-IDF vectors
    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Compare new complaint with existing complaints
    new_vector = tfidf_matrix[-1]
    existing_vectors = tfidf_matrix[:-1]

    similarities = cosine_similarity(
        new_vector,
        existing_vectors
    )[0]

    similar_complaints = []

    for index, score in enumerate(similarities):

        percentage = float(round(score * 100, 2))

        if percentage >= 40:

            similar_complaints.append({
                "complaint_id": complaint_data[index]["complaint_id"],
                "title": complaint_data[index]["title"],
                "similarity": percentage
            })

    # Sort highest similarity first
    similar_complaints.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    # Highest similarity
    highest_similarity = float(max(similarities) * 100)

    # Duplicate if similarity is 70% or more
    is_duplicate = bool(highest_similarity >= 70)

    # Number of similar complaints
    similar_count = len(similar_complaints)

    # Determine impact level
    if similar_count >= 10:
        impact_level = "Critical"

    elif similar_count >= 5:
        impact_level = "High"

    elif similar_count >= 2:
        impact_level = "Medium"

    else:
        impact_level = "Low"

    return {
        "is_duplicate": is_duplicate,
        "similarity_score": round(highest_similarity, 2),
        "similar_complaints": similar_complaints,
        "similar_count": similar_count,
        "impact_level": impact_level
    }