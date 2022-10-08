# import os  # We need this to retrieve credentials from environment variables
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# import datanews  # This is the official Datanews library for Python
# import lang
# assert 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ, 'Google Cloud credentials are not specified'
# assert 'DATANEWS_API_KEY' in os.environ, 'Datanews API key is not specified'

# datanews.api_key = os.environ['DATANEWS_API_KEY']
# """https://datanews.io/blog/sentiment-analysis-with-news-api"""
# """https://towardsdatascience.com/sentiment-analysis-concept-analysis-and-applications-6c94d6f58c17"""
# sources = [
#     'wsj.com',
#     'apnews.com',
#     'nytimes.com',
#     'cnn.com'
# ]

# articles = {}

# for source in sources:
#     most_recent = datanews.headlines(source=source, page=0, size=100, sortBy='date')
#     articles[source] = [article['content'] for article in most_recent['hits']]

# analyzer = SentimentIntensityAnalyzer()

# for source, news in articles.items():
#     magnitude, score = 0, 0

#     # TODO: this is adapted from google-based
#     for article in news:
#         document = lang.Document(content=article, type_=lang.Document.Type.PLAIN_TEXT)
#         sentiment = client.analyze_sentiment(request={'document': document})
#         magnitude += sentiment.document_sentiment.magnitude
#         score += sentiment.document_sentiment.score

#     avg_magnitude = magnitude / len(news)
#     avg_score = score / len(news)
#     print(source)
#     print(f'\taverage magnitude: {avg_magnitude}')
#     print(f'\taverage score: {avg_score}')