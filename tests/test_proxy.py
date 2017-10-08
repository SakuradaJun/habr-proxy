import os
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
    def transform_request(html):
        return filter_html(html, 'http://127.0.0.1:8232')

    def test_parser(self):
        before = '<html><body><div>looooong mini Yandex</div></body></html>'
        result = self.transform_request(before)
        assert 'Yandex&trade;' in result

        before = '<html><body><a href="http://habrahabr.ru/company/itinvest/blog/339548/"></a></body></html>'
        '<a href="http://127.0.0.1:8232/post/338068/">' in self.transform_request(before)
