from elements._elementBase import ElementBase, docDB


class Distributor(ElementBase):
    _attrdef = dict(
        name=ElementBase.addAttr(unique=True, notnone=True),
        desc=ElementBase.addAttr(default='', notnone=True),
        url=ElementBase.addAttr(default='', notnone=True)
    )

    def delete_pre(self):
        from elements import PartDistributor
        for pd in docDB.search_many('PartDistributor', {'distributor_id': self['_id']}):
            pd = PartDistributor(pd)
            pd.delete()
