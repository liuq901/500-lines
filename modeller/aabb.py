import math

import numpy

EPSILON = 0.000001

class AABB(object):
    def __init__(self, center, size):
        self.center = numpy.array(center)
        self.size = numpy.array(size)

    def ray_hit(self, origin, direction, modelmatrix):
        aabb_min = self.center - self.size
        aabb_max = self.center + self.size
        tmin = 0.0
        tmax = 100000.0

        obb_pos_worldspace = numpy.array([modelmatrix[0, 3], modelmatrix[1, 3], modelmatrix[2, 3]])
        delta = obb_pos_worldspace - origin

        xaxis = numpy.array([modelmatrix[0, 0], modelmatrix[0, 1], modelmatrix[0, 2]])
        e = numpy.dot(xaxis, delta)
        f = numpy.dot(direction, xaxis)
        if math.fabs(f) > 0.0 + EPSILON:
            t1 = (e + aabb_min[0]) / f
            t2 = (e + aabb_max[0]) / f
            if t1 > t2:
                t1, t2 = t2, t1
            if t2 < tmax:
                tmax = t2
            if t1 > tmin:
                tmin = t1
            if tmax < tmin:
                return False, 0
        else:
            if -e + aabb_min[0] > 0.0 + EPSILON or -e + aabb_max[0] < 0.0 - EPSILON:
                return False, 0

        yaxis = numpy.array([modelmatrix[1, 0], modelmatrix[1, 1], modelmatrix[1, 2]])
        e = numpy.dot(yaxis, delta)
        f = numpy.dot(direction, yaxis)
        if math.fabs(f) > 0.0 + EPSILON:
            t1 = (e + aabb_min[1]) / f
            t2 = (e + aabb_max[1]) / f
            if t1 > t2:
                t1, t2 = t2, t1
            if t2 < tmax:
                tmax = t2
            if t1 > tmin:
                tmin = t1
            if tmax < tmin:
                return False, 0
        else:
            if -e + aabb_min[1] > 0.0 + EPSILON or -e + aabb_max[1] < 0.0 - EPSILON:
                return False, 0

        zaxis = numpy.array([modelmatrix[2, 0], modelmatrix[2, 1], modelmatrix[2, 2]])
        e = numpy.dot(zaxis, delta)
        f = numpy.dot(direction, zaxis)
        if math.fabs(f) > 0.0 + EPSILON:
            t1 = (e + aabb_min[2]) / f
            t2 = (e + aabb_max[2]) / f
            if t1 > t2:
                t1, t2 = t2, t1
            if t2 < tmax:
                tmax = t2
            if t1 > tmin:
                tmin = t1
            if tmax < tmin:
                return False, 0
        else:
            if -e + aabb_min[2] > 0.0 + EPSILON or -e + aabb_max[2] < 0.0 - EPSILON:
                return False, 0

        return True, tmin
