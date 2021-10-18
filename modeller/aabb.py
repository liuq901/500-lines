import numpy

EPSILON = 0.000001

class AABB(object):
    def __init__(self, center, size):
        self.center = numpy.array(center)
        self.size = numpy.array(size)
