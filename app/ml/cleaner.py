# import re
# import nltk
# from nltk.corpus import stopwords


# import nltk

# try:
#     nltk.data.find("corpora/stopwords")
# except:
#     nltk.download("stopwords")


# # Make sure stopwords are downloaded at startup
# nltk.download('stopwords', quiet=True)
# STOP_WORDS = set(stopwords.words("english"))

# def clean_email_text(text: str) -> str:
#     text = str(text).lower()
#     text = re.sub(r'\S+@\S+', ' ', text)       # remove emails
#     text = re.sub(r'http\S+', ' ', text)       # remove URLs
#     text = re.sub(r'\d+', ' ', text)           # remove numbers
#     text = re.sub(r'[^a-z\s]', ' ', text)      # remove punctuation
#     text = re.sub(r'\s+', ' ', text).strip()

#     tokens = [w for w in text.split() if w not in STOP_WORDS]
#     return " ".join(tokens)


# import re
# import nltk
# from nltk.corpus import stopwords

# # Lazy load stopwords (safe for deployment)
# def get_stopwords():
#     try:
#         return set(stopwords.words("english"))
#     except LookupError:
#         nltk.download("stopwords")
#         return set(stopwords.words("english"))

# STOP_WORDS = get_stopwords()

# def clean_email_text(text: str) -> str:
#     text = str(text).lower()
#     text = re.sub(r'\S+@\S+', ' ', text)
#     text = re.sub(r'http\S+', ' ', text)
#     text = re.sub(r'\d+', ' ', text)
#     text = re.sub(r'[^a-z\s]', ' ', text)
#     text = re.sub(r'\s+', ' ', text).strip()

#     tokens = [w for w in text.split() if w not in STOP_WORDS]
#     return " ".join(tokens)


import re
from nltk.corpus import stopwords
import nltk

STOP_WORDS = None  # do not load at startup

def get_stopwords():
    global STOP_WORDS
    if STOP_WORDS is None:
        try:
            STOP_WORDS = set(stopwords.words("english"))
        except LookupError:
            nltk.download("stopwords")
            STOP_WORDS = set(stopwords.words("english"))
    return STOP_WORDS


def clean_email_text(text: str) -> str:
    stop_words = get_stopwords()  # load only when needed

    text = str(text).lower()
    text = re.sub(r'\S+@\S+', ' ', text)
    text = re.sub(r'http\S+', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    tokens = [w for w in text.split() if w not in stop_words]
    return " ".join(tokens)