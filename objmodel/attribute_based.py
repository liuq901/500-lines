MISSING = object()

class Base(object):
    def __init__(self, cls, fileds):
        self.cls = cls
        self._fields = fileds

    def read_attr(self, filedname):
        result = self._read_dict(filedname)
        if result is not MISSING:
            return result
        result = self.cls._read_from_class(filedname)
        if _is_bindable(result):
            return _make_boundmethod(result, self)
        if result is not MISSING:
            return result
        raise AttributeError(filedname)

    def write_attr(self, filedname, value):
        self._write_dict(filedname, value)

    def isinstance(self, cls):
        return self.cls.issubclass(cls)

    def callmethod(self, methname, *args):
        meth = self.read_attr(methname)
        return meth(*args)

    def _read_dict(self, filedname):
        return self._fields.get(filedname, MISSING)

    def _write_dict(self, filedname, value):
        self._fields[filedname] = value

def _is_bindable(meth):
    return callable(meth)

def _make_boundmethod(meth, self):
    def bound(*args):
        return meth(self, *args)

    return bound

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
