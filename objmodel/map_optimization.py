MISSING = object()

class Base(object):
    def __init__(self, cls, fileds):
        self.cls = cls
        self._fields = fileds

    def read_attr(self, fieldname):
        result = self._read_dict(fieldname)
        if result is not MISSING:
            return result
        result = self.cls._read_from_class(fieldname)
        if _is_bindable(result):
            return _make_boundmethod(result, self)
        if result is not MISSING:
            return result
        meth = self.cls._read_from_class('__getattr__')
        if meth is not MISSING:
            return meth(self, fieldname)
        raise AttributeError(fieldname)

    def write_attr(self, fieldname, value):
        meth = self.cls._read_from_class('__setattr__')
        return meth(self, fieldname, value)

    def isinstance(self, cls):
        return self.cls.issubclass(cls)

    def callmethod(self, methname, *args):
        meth = self.read_attr(methname)
        return meth(*args)

    def _read_dict(self, fieldname):
        return self._fields.get(fieldname, MISSING)

    def _write_dict(self, fieldname, value):
        self._fields[fieldname] = value

def _is_bindable(meth):
    return hasattr(meth, '__get__')

def _make_boundmethod(meth, self):
    return meth.__get__(self, None)

def OBJECT__setattr__(self, fieldname, value):
    self._write_dict(fieldname, value)

class Map(object):
    def __init__(self, attrs):
        self.attrs = attrs
        self.next_maps = {}

    def get_index(self, fieldname):
        return self.attrs.get(fieldname, -1)

    def next_map(self, fieldname):
        assert fieldname not in self.attrs
        if fieldname in self.next_maps:
            return self.next_maps[fieldname]
        attrs = self.attrs.copy()
        attrs[fieldname] = len(attrs)
        result = self.next_maps[fieldname] = Map(attrs)
        return result

EMPTY_MAP = Map({})

class Instance(Base):
    def __init__(self, cls):
        assert isinstance(cls, Class)
        super().__init__(cls, None)
        self.map = EMPTY_MAP
        self.storage = []

    def _read_dict(self, fieldname):
        index = self.map.get_index(fieldname)
        if index == -1:
            return MISSING
        return self.storage[index]

    def _write_dict(self, fieldname, value):
        index = self.map.get_index(fieldname)
        if index != -1:
            self.storage[index] = value
        else:
            new_map = self.map.next_map(fieldname)
            self.storage.append(value)
            self.map = new_map

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

OBJECT = Class(name='object', base_class=None, fields={'__setattr__': OBJECT__setattr__}, metaclass=None)
TYPE = Class(name='type', base_class=OBJECT, fields={}, metaclass=None)
TYPE.cls = TYPE
OBJECT.cls = TYPE
