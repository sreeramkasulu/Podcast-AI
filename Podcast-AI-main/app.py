import requests
from flask import Flask, render_template, request, jsonify
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
from datetime import datetime, timedelta
import nltk

nltk.download('punkt')

app = Flask(__name__)

API_KEY = "e18dd9325d33409b83d8a6571e28ac4f"

STOP_WORDS = set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
    'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
    'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
    'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
    'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
    'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
    'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
    'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
    'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
    'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
])

def fetch_news(query='latest news', language='en'):
    today = datetime.now()
    last_week = today - timedelta(days=7)
    from_date = last_week.strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    url = f'https://newsapi.org/v2/everything?q={query}&from={from_date}&to={to_date}&sortBy=publishedAt&language={language}&apiKey={API_KEY}'
    response = requests.get(url)

    articles = []
    if response.json().get('status') == 'ok':
        articles = response.json().get('articles', [])
    
    return {'status': 'ok', 'articles': articles}

def analyze_news(articles):
    content = []
    summaries = []
    additional_insights = []
    key_insights = []

    for article in articles:
        if 'content' in article and article['content']:
            content.append(article['content'])
            summaries.append(f"{article['title']}: {article['description']}")
            additional_insights.append(article['content'])
            key_insights.append(article['title'])

    text = ' '.join(content)
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())

    filtered_words = [word for word in words if word.isalpha() and word not in STOP_WORDS]
    word_freq = Counter(filtered_words)
    most_common_words = word_freq.most_common(10)

    return {
        'sentences': sentences,
        'most_common_words': most_common_words,
        'total_articles': len(articles),
        'summaries': summaries,
        'additional_insights': additional_insights,
        'key_insights': key_insights
    }

def generate_podcast_outline(analysis):
    outline = f"Today's Podcast Topics:\n- Overview of {analysis['total_articles']} articles\n\n"

    outline += "Detailed Topics:\nRecent Developments:\n"
    for i, summary in enumerate(analysis['summaries'], 1):
        outline += f"{i}. {summary}\n"

    outline += "\nKey Insights:\n"
    for i, insight in enumerate(analysis['key_insights'], 1):
        outline += f"{i}. {insight}\n"

    return outline

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        query = request.json.get('query')
        language = request.json.get('language', 'en')

        if not query:
            return jsonify({'error': 'Query is required.'}), 400

        news_data = fetch_news(query, language)

        if news_data.get('status') == 'ok':
            articles = news_data.get('articles', [])
            if articles:
                analysis = analyze_news(articles)
                podcast_outline = generate_podcast_outline(analysis)
                return jsonify({
                    'outline': podcast_outline,
                    'total_articles': analysis['total_articles']
                })
            else:
                return jsonify({'error': 'No articles found for the given query.'}), 404
        else:
            return jsonify({'error': news_data.get('message', 'Error fetching news')}), 500

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    app.run(debug=True)
