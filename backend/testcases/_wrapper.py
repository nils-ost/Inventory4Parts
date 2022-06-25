import io
import unittest
import json
import cherrypy
from cherrypy.lib import httputil
from i4p import Inventory4Parts


def setUpModule():
    cherrypy.config.update({'environment': 'test_suite'})

    # prevent the HTTP server from ever starting
    cherrypy.server.unsubscribe()

    cherrypy.tree.mount(Inventory4Parts(), '/')
    cherrypy.engine.start()


def tearDownModule():
    cherrypy.engine.exit()


class ApiTestBase(unittest.TestCase):
    def webapp_request(self, path='/', method='POST', data=None, **kwargs):
        headers = [('Host', '127.0.0.1')]
        local = httputil.Host('127.0.0.1', 50000, '')
        remote = httputil.Host('127.0.0.1', 50001, '')

        # Get our application and run the request against it
        app = cherrypy.tree.apps['']
        # Let's fake the local and remote addresses
        # Let's also use a non-secure scheme: 'http'
        request, response = app.get_serving(local, remote, 'http', 'HTTP/1.1')

        if data:
            qs = json.dumps(data)
        elif kwargs:
            qs = json.dumps(kwargs)
        else:
            qs = '{}'
        headers.append(('content-type', 'application/json'))
        headers.append(('content-length', f'{len(qs)}'))
        fd = io.BytesIO(qs.encode())
        qs = None

        try:
            response = request.run(method.upper(), path, qs, 'HTTP/1.1', headers, fd)
        finally:
            if fd:
                fd.close()
                fd = None

        if response.output_status.startswith(b'500'):
            print(response.body)
            raise AssertionError('Unexpected error')

        # collapse the response into a bytestring
        response.collapse_body()
        try:
            response.json = json.loads(response.body[0])
        except Exception:
            response.json = {}

        return response
