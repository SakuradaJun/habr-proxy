import re
from bs4 import BeautifulSoup as bs
from bs4 import Comment


def filter_html(content, app_url):
    def filter_text(text):
        return re.sub(r'\b(?<!&amp;)(?<!&)([а-яёa-z-]{6})\b', r'\1™', text, flags=re.IGNORECASE)

    soup = bs(content, 'html5lib')
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

    return soup.prettify()
