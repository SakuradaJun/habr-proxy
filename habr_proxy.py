#!/usr/bin/env python3
import argparse

import requests
from flask import Flask, Response, request, current_app

from common import filter_html


def create_app():
    app = Flask(__name__)
    REQUESTS_SESSION = requests.Session()

    @app.route('/', defaults={'uri_path': ''}, methods=['GET'])
    @app.route('/<path:uri_path>', methods=['GET'])
    def default(uri_path):
        if not uri_path.startswith('/'):
            uri_path = '/' + uri_path
        else:
            uri_path = '/'
        url = '{}{}'.format('https://habrahabr.ru', uri_path)
        headers = dict(request.headers.items())
        headers.pop('Host', None)

        req = REQUESTS_SESSION.get(url, headers=headers)
        current_app.logger.info('%s %s - %s', url, req, req.elapsed.total_seconds())
        response_headers = dict(req.headers.items())
        exclude_headers = (
            'Content-Encoding', 'Transfer-Encoding', 'Content-Length', 'P3P', 'Public-Key-Pins',
            'Connection', 'Keep-Alive'
        )
        [response_headers.pop(h, None) for h in exclude_headers]
        content = req.content

        if req.headers.get('Content-Type', '').startswith('text/html'):
            content = filter_html(content, request.host_url.strip('/'))

        return Response(content, content_type=req.headers['Content-Type'], headers=response_headers)
    return app

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0', type=str, help='default: 0.0.0.0')
    parser.add_argument('--port', default='8232', type=int, help='default: 8232')
    parser.add_argument('-d', '--debug', action='store_true', help='Run the app in debug mode')

    args = parser.parse_args()
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)
