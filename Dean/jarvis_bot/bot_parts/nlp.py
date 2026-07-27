"""
NLP Module for JARVIS - Handles text processing and analysis
"""
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')


class NLPTask:
    """Handles Natural Language Processing tasks"""
    
    def __init__(self, text=''):
        self.text = text
        self.stop_words = set(stopwords.words('english'))

    def set_text(self, text):
        """Update the text to process"""
        self.text = text

    def tokenize(self):
        """Tokenize text into words"""
        if not self.text:
            return []
        return word_tokenize(self.text.lower())

    def remove_stopwords(self):
        """Remove common stopwords from tokens"""
        tokens = self.tokenize()
        filtered_tokens = [token for token in tokens if token not in self.stop_words and token.isalnum()]
        return filtered_tokens

    def extract_keywords(self):
        """Extract meaningful keywords from text"""
        return self.remove_stopwords()

    def sentiment_analysis(self):
        """Analyze sentiment of text using VADER"""
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer()
        scores = sia.polarity_scores(self.text)
        return scores['compound']
