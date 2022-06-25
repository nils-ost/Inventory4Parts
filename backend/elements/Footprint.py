from elements._elementBase import ElementBase, docDB


class Footprint(ElementBase):
    _attrdef = dict(
        name=ElementBase.addAttr(unique=True, notnone=True),
        mounting_style_id=ElementBase.addAttr()
    )

    def validate(self):
        errors = dict()
        if self['mounting_style_id'] is not None and not docDB.exists('MountingStyle', self['mounting_style_id']):
            errors['mounting_style_id'] = f"There is no MountingStyle with id '{self['mounting_style_id']}'"
        return errors
