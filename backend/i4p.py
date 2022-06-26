import cherrypy
import cherrypy_cors
from helpers.docdb import docDB
from helpers.config import get_config
from helpers.elementendpoint import ElementEndpointBase
from elements import MountingStyle, Footprint, Category


class Inventory4Parts():
    def __init__(self):
        self.mountingstyle = MountingStyleEndpoint()
        self.footprint = FootprintEndpoint()
        self.category = CategoryEndpoint()


class MountingStyleEndpoint(ElementEndpointBase):
    _element = MountingStyle


class FootprintEndpoint(ElementEndpointBase):
    _element = Footprint


class CategoryEndpoint(ElementEndpointBase):
    _element = Category


if __name__ == '__main__':
    conf = {
    }
    config = get_config('server')
    cherrypy_cors.install()
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': config['port'], 'cors.expose.on': True})

    docDB.wait_for_connection()
    cherrypy.quickstart(Inventory4Parts(), '/', conf)
