import cherrypy
import cherrypy_cors
from helpers.docdb import docDB
from helpers.config import get_config
from helpers.elementendpoint import ElementEndpointBase
from elements import MountingStyle, Footprint, Category, Unit, Part, Distributor, PartDistributor, StorageGroup, StorageLocation
from elements import Order, PartLocation, StockChange


class Inventory4Parts():
    def __init__(self):
        self.mountingstyle = MountingStyleEndpoint()
        self.footprint = FootprintEndpoint()
        self.category = CategoryEndpoint()
        self.unit = UnitEndpoint()
        self.part = PartEndpoint()
        self.distributor = DistributorEndpoint()
        self.partdistributor = PartDistributorEndpoint()
        self.storagegroup = StorageGroupEndpoint()
        self.storagelocation = StorageLocationEndpoint()
        self.order = OrderEndpoint()
        self.partlocation = PartLocationEndpoint()
        self.stockchange = StockChangeEndpoint()


class MountingStyleEndpoint(ElementEndpointBase):
    _element = MountingStyle


class FootprintEndpoint(ElementEndpointBase):
    _element = Footprint


class CategoryEndpoint(ElementEndpointBase):
    _element = Category


class UnitEndpoint(ElementEndpointBase):
    _element = Unit


class PartEndpoint(ElementEndpointBase):
    _element = Part


class DistributorEndpoint(ElementEndpointBase):
    _element = Distributor


class PartDistributorEndpoint(ElementEndpointBase):
    _element = PartDistributor


class StorageGroupEndpoint(ElementEndpointBase):
    _element = StorageGroup


class StorageLocationEndpoint(ElementEndpointBase):
    _element = StorageLocation


class OrderEndpoint(ElementEndpointBase):
    _element = Order


class PartLocationEndpoint(ElementEndpointBase):
    _element = PartLocation


class StockChangeEndpoint(ElementEndpointBase):
    _element = StockChange


if __name__ == '__main__':
    conf = {
    }
    config = get_config('server')
    cherrypy_cors.install()
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': config['port'], 'cors.expose.on': True})

    docDB.wait_for_connection()
    cherrypy.quickstart(Inventory4Parts(), '/', conf)
