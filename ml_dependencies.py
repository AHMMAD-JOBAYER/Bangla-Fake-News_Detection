import re
import pickle
from bnlp import CleanText
from bnlp import BengaliCorpus as corpus

clean_text = CleanText(
   fix_unicode=True,
   unicode_norm=True,
   unicode_norm_form="NFKC",
   remove_url=True,
   remove_email=True,
   remove_emoji=True,
   remove_number=True,
   remove_digits=True,
   remove_punct=True,
   replace_with_url="",
   replace_with_email="",
   replace_with_number="",
   replace_with_digit="",
   replace_with_punct = ""
)

stopword = set(corpus.stopwords)
stopword.update({
    "এ",
    "এক",
    "একটা",
    "একটু",
    "এরপর",
    "সাথে",
    "একজন",
    "সবাই",
    "দেয়া",
})

def preprocess_text(text):
  text = clean_text(text)
  text = re.sub(r'[a-zA-Z0-9]', '', text)
  text = ' '.join([word for word in text.split() if word not in (stopword)])
  # text = stemmer(text)
  return text

with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

def predict_text_from_user(user_input):
  user_input_vectorized = preprocess_text(user_input)
  user_input_vectorized = vectorizer.transform([user_input_vectorized])
  prediction = model.predict(user_input_vectorized)
  return prediction[0]
