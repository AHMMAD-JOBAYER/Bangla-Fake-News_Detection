import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# Set the maximum number of news articles to scrape
MAX_NEWS_ARTICLES = 1000

# Set the delay between requests (in seconds)
DELAY_BETWEEN_REQUESTS = 2

# Set the URL of the news webpage
base_url = "https://www.earki.co/news/article/"
articleID = 10179

# Create a list to store the news data
news_data = []

while len(news_data) < MAX_NEWS_ARTICLES:
    try:
        # Send request to the webpage
        article_link = base_url + str(articleID)
        response = requests.get(article_link)

        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract Title of Article
        title = soup.find('span', {'class': 'title'}).text
        author = soup.find('span', {'class': 'author_name'}).text

        # Extract article
        article_div = soup.find('div', {'itemprop': 'articleBody'})
        paragraphs = article_div.find_all('p')
        article = ' '.join([p.get_text() for p in paragraphs])

        #Extract date
        date_span = soup.find('span', {'class': 'time'})
        date_str = date_span['data-modified']

        # Append to the news data list
        news_data.append({
            'domain': base_url,
            'articleID': articleID,
            'author': author,
            'date': date_str,
            'headline': title,
            'content': article,
            'label': 0
        })
        print(f"news added: {len(news_data)}")

    except Exception:
      print(f"article no {articleID} does not exists")

    articleID -= 1
    # Delay for a random time between 2-5 seconds
    time.sleep(random.uniform(DELAY_BETWEEN_REQUESTS, DELAY_BETWEEN_REQUESTS + 3))

# Create a pandas DataFrame from the news data list
df = pd.DataFrame(news_data)

# Write the DataFrame to a CSV file
df.to_csv('fake_news_data.csv', index=False)

print("News data saved to news_data.csv")
