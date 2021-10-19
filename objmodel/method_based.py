MISSING = object()

class Base(object):
    def __init__(self, cls, fileds):
        self.cls = cls
        self._fields = fileds

    def read_attr(self, fieldname):
        return self._read_dict(fieldname)

    def write_attr(self, fieldname, value):
        self._write_dict(fieldname, value)

    def isinstance(self, cls):
        return self.cls.issubclass(cls)

    def callmethod(self, methname, *args):
        meth = self.cls._read_from_class(methname)
        return meth(self, *args)

    def _read_dict(self, fieldname):
        return self._fields.get(fieldname, MISSING)

    def _write_dict(self, fieldname, value):
        self._fields[fieldname] = value

class Instance(Base):
    def __init__(self, cls):
        assert isinstance(cls, Class)
        super().__init__(cls, {})

class Class(Base):
    def __init__(self, name, base_class, fields, metaclass):
        super().__init__(metaclass, fields)
        self.name = name
        self.base_class = base_class

    def method_resolution_order(self):
        if self.base_class is None:
            return [self]
        else:
            return [self] + self.base_class.method_resolution_order()

    def issubclass(self, cls):
        return cls in self.method_resolution_order()

    def _read_from_class(self, methname):
        for cls in self.method_resolution_order():
            if methname in cls._fields:
                return cls._fields[methname]
        return MISSING

OBJECT = Class(name='object', base_class=None, fields={}, metaclass=None)
TYPE = Class(name='type', base_class=OBJECT, fields={}, metaclass=None)
TYPE.cls = TYPE
OBJECT.cls = TYPE
