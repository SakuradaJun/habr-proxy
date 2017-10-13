import os
import re

import requests_mock
from flask_testing import TestCase

from common import filter_html
from habr_proxy import create_app


class AppTestCase(TestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        self.data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
        return app

    def test_full(self):
        with open(os.path.join(self.data_dir, 'page_mock.html')) as fp:
            page_mock = fp.read()

        with open(os.path.join(self.data_dir, 'page_except.html')) as fp:
            page_except = fp.read()

        with requests_mock.mock() as m:
            m.get(requests_mock.ANY, text=page_mock, headers={
                'Content-Type': 'text/html; charset=UTF-8'
            })
            r = self.client.get('/')
            self.assert200(r)
            self.assertEqual(r.data.decode('utf-8'), page_except)

    @staticmethod
    def transform_request(body):
        result = filter_html('<html><body>%s</body></html>' % body, 'http://127.0.0.1:8232')
        return re.match(r'.*<body>\s*(.+)\s*</body>.*', result, flags=re.DOTALL).group(1).strip()

    def test_parser(self):
        r = self.transform_request('''Сейчас на фоне уязвимости Logjam все в индустрии в очередной раз обсуждают
  проблемы и особенности TLS. Я хочу воспользоваться этой возможностью, чтобы
  поговорить об одной из них, а именно — о настройке ciphersiutes.''')
        self.assertEqual('''Сейчас™ на фоне уязвимости Logjam™ все в индустрии в очередной раз обсуждают
  проблемы и особенности TLS. Я хочу воспользоваться этой возможностью, чтобы
  поговорить об одной из них, а именно™ — о настройке ciphersiutes.''', r)

        self.assertIn('ёрзать™', self.transform_request('<p>ёрзать</p>'))

        # skip replace in entities
        self.assertNotIn('™', self.transform_request('<p>&amp;spades;</p>'))
        self.assertNotIn('™', self.transform_request('<p>&spades;</p>'))
        self.assertIn('♠ — &amp;#9824; или &amp;spades;',
                      self.transform_request('<p>♠ — &amp;#9824; или &amp;spades;</p>'))
        self.assertIn('™', self.transform_request('<p>spades;</p>'))

        self.assertIn('Yandex™', self.transform_request('<div>looooong mini Yandex</div>'))
        self.assertIn('+8', self.transform_request('<span class="post-info__meta-counter">+8</span>'))

        before = '<a href="http://habrahabr.ru/company/itinvest/blog/339548/"></a>'
        '<a href="http://127.0.0.1:8232/post/338068/">' in self.transform_request(before)

        self.assertEqual('<b>\n   &lt;b&gt;\n  </b>', self.transform_request('<b>&lt;b&gt;</b>'))


