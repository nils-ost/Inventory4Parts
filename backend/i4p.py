import cherrypy
import cherrypy_cors
from helpers.docdb import docDB
from helpers.config import get_config
from elements import MountingStyle


class Inventory4Parts():
    def __init__(self):
        self.mountingstyle = MountingStyleEndpoint()


@cherrypy.popargs('mountingstyle_id')
class MountingStyleEndpoint():
    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self, mountingstyle_id=None):
        if cherrypy.request.method == 'OPTIONS':
            if mountingstyle_id is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST'
                cherrypy_cors.preflight(allowed_methods=['GET', 'POST'])
                return
            else:
                ms = MountingStyle.get(mountingstyle_id)
                if ms['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {mountingstyle_id} not found'}
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, PATCH, DELETE'
                cherrypy_cors.preflight(allowed_methods=['GET', 'PATCH', 'DELETE'])
                return
        elif cherrypy.request.method == 'GET':
            if mountingstyle_id is not None:
                ms = MountingStyle.get(mountingstyle_id)
                if ms['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {mountingstyle_id} not found'}
                return ms.json()
            else:
                result = list()
                for ms in MountingStyle.all():
                    result.append(ms.json())
                return result
        elif cherrypy.request.method == 'POST':
            if mountingstyle_id is None:
                attr = cherrypy.request.json
                if not isinstance(attr, dict):
                    cherrypy.response.status = 400
                    return {'error': 'Submitted data need to be of type dict'}
                attr.pop('_id', None)
                ms = MountingStyle(attr)
                result = ms.save()
                if 'errors' in result:
                    cherrypy.response.status = 400
                else:
                    cherrypy.response.status = 201
                return result
            else:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, PATCH, DELETE'
                cherrypy.response.status = 405
                return {'error': 'POST not allowed on existing objects'}
        elif cherrypy.request.method == 'PATCH':
            if mountingstyle_id is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST'
                cherrypy.response.status = 405
                return {'error': 'PATCH not allowed on indexes'}
            else:
                ms = MountingStyle.get(mountingstyle_id)
                if ms['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {mountingstyle_id} not found'}
                attr = cherrypy.request.json
                if not isinstance(attr, dict):
                    cherrypy.response.status = 400
                    return {'error': 'Submitted data need to be of type dict'}
                attr.pop('_id', None)
                for k, v in attr.items():
                    ms[k] = v
                result = ms.save()
                if 'errors' in result:
                    cherrypy.response.status = 400
                else:
                    cherrypy.response.status = 201
                return result
        elif cherrypy.request.method == 'DELETE':
            if mountingstyle_id is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST'
                cherrypy.response.status = 405
                return {'error': 'DELETE not allowed on indexes'}
            else:
                ms = MountingStyle.get(mountingstyle_id)
                if ms['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {mountingstyle_id} not found'}
                ms.delete()
                return
        else:
            if mountingstyle_id is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST'
            else:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, PATCH, DELETE'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}


if __name__ == '__main__':
    conf = {
    }
    config = get_config('server')
    cherrypy_cors.install()
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': config['port'], 'cors.expose.on': True})

    docDB.wait_for_connection()
    cherrypy.quickstart(Inventory4Parts(), '/', conf)
