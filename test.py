import requests
from bs4 import BeautifulSoup

with requests.Session() as session:
    s = session.get("www.nytimes.com")
    soup = BeautifulSoup(s.text, 'html.parser')
    print(soup.title.string)
