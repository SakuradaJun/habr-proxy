import re
import html
from bs4 import BeautifulSoup as bs
from bs4 import Comment


def filter_html(content, app_url):
    def filter_text(text):
        return re.sub(r'\b([а-яa-z]{6})\b', r'\1&trade;', text, flags=re.I)

    soup = bs(content, 'lxml')
    exclude_tags = ['script', 'style', 'noscript', 'meta', 'link', 'code']

    for a in soup.findAll('a', href=True):
        a['href'] = a['href'].replace('https://habrahabr.ru', app_url)\
            .replace('http://habrahabr.ru', app_url)

    for element in soup.find_all(text=True):
        if isinstance(element, Comment):
            continue
        text = element.string
        if text and False not in [element.find_parent(x) is None for x in exclude_tags] and text != 'html':
            element.replace_with(filter_text(text))

    return html.unescape(soup.prettify(formatter='html'))
