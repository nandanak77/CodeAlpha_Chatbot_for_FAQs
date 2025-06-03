from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download required NLTK data (only first time)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')
app = Flask(__name__)

# Load FAQ data
df = pd.read_csv("faq_questions.csv")
qa_pairs = []
for row in df['question']:
    try:
        items = json.loads(row)
        for item in items:
            qa_pairs.append({
                "question": item.get("question", "").strip(),
                "answer": item.get("answer", "").strip()
            })
    except json.JSONDecodeError:
        continue

faq_df = pd.DataFrame(qa_pairs).dropna()

# NLP preprocessing
stop_words = set(stopwords.words('english'))
def preprocess(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

faq_df['clean_question'] = faq_df['question'].apply(preprocess)

# TF-IDF vectorizer
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(faq_df['clean_question'])

def get_response(user_input):
    user_input_clean = preprocess(user_input)
    user_vec = vectorizer.transform([user_input_clean])
    similarity = cosine_similarity(user_vec, tfidf_matrix)
    idx = similarity.argmax()
    score = similarity[0, idx]
    if score > 0.2:
        return faq_df.iloc[idx]['answer']
    else:
        return "Sorry, I couldn't understand your question."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("message")
    response = get_response(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
