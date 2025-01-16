import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import download
import os

download('punkt')
download('stopwords')
download('punkt_tab')

russian_stopwords = list(stopwords.words('russian'))


def preprocess_text(text):
    """
    Clears the text: removes punctuation, lowercase, removes stop words
    """

    text = re.sub(r'[^\w\s]', '', text.lower())

    # Tokenization
    words = word_tokenize(text)

    # Deleting stop words
    custom_stop_words = [
        'это', 'всё', 'тебе', 'просто', 'очень', 'ладно', 'ещё',
        'давай', 'ага', 'так', 'как', 'мне', 'ты', 'он', 'она',
        'мы', 'вы', 'кто', 'где', 'что'
    ]
    return ' '.join([word for word in words if word not in russian_stopwords and word not in custom_stop_words and len(word) >= 3])


def extract_style_keywords(messages, top_n=200):
    """
    Highlights keywords specific to a particular person's style.
    """
    preprocessed_messages = [preprocess_text(msg) for msg in messages]

    # We use TF-IDF for frequency and uniqueness analysis.
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),    # Phrases from N to M words are highlighted (for example, all phrases with from 1 to 3 words)
        max_features=3000,      # Maximum of N phrases
        min_df=10,            # Minimum of N data words from the document
        max_df=0.3,           # Maximum of N% of documents
        stop_words=russian_stopwords  # Removing safe words
    )
    tfidf_matrix = vectorizer.fit_transform(preprocessed_messages)

    # We get the words and their weights
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.mean(axis=0).A1  # Average weight for each word
    keywords = list(zip(feature_names, tfidf_scores))

    keywords = sorted(keywords, key=lambda x: x[1], reverse=True)

    return keywords[:top_n]


def analyze_style(file_path, top_n=10):
    """
    Analyzes the style of a particular person based on a JSON file with messages
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # We extract the messages of a specific person
    messages = []
    for entry in data:
        if len(entry['output']) <= 300:
            messages.append(entry['output'])

    if not messages:
        print(f"Нет сообщений для пользователя")
        return []

    keywords = extract_style_keywords(messages, top_n=top_n)
    return keywords

def load_dataset(user_id):
    """
    Uploads and processes user data
    """
    user_folder = os.path.join("results", str(user_id))
    print(user_folder)
    file_path = os.path.join(user_folder, "filtered_messages.json")
    print(file_path)

    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    style_keywords = analyze_style(file_path, top_n=200)

    if style_keywords:
        keywords_file = os.path.join(user_folder, "style_keywords.json")
        with open(keywords_file, "w", encoding="utf-8") as f:
            json.dump(style_keywords, f, ensure_ascii=False, indent=4)
        print(f"Ключевые слова сохранены в '{keywords_file}'")

    return style_keywords