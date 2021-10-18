import math

from OpenGL.GL import GL_VIEWPORT
from OpenGL.GL import GLfloat
from OpenGL.GL import glGetIntegerv

M_SQRT1_2 = math.sqrt(0.5)
M_SQRT2 = math.sqrt(2.0)

def v_add(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]]

def v_sub(v1, v2):
    return [v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]]

def v_mul(v, s):
    return [v[0] * s, v[1] * s, v[2] * s]

def v_dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

def v_cross(v1, v2):
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0],
    ]

def v_length(v):
    return math.sqrt(v_dot(v, v))

def v_normalize(v):
    try:
        return v_mul(v, 1.0 / v_length(v))
    except ZeroDivisionError:
        return v

def q_add(q1, q2):
    t1 = v_mul(q1, q2[3])
    t2 = v_mul(q2, q1[3])
    t3 = v_cross(q2, q1)
    tf = v_add(t1, t2)
    tf = v_add(t3, tf)
    tf.append(q1[3] * q2[3] - v_dot(q1, q2))
    return tf

def q_mul(q, s):
    return [q[0] * s, q[1] * s, q[2] * s, q[3] * s]

def q_dot(q1, q2):
    return q1[0] * q2[0] + q1[1] * q2[1] + q1[2] * q2[2] + q1[3] * q2[3]

def q_length(q):
    return math.sqrt(q_dot(q, q))

def q_normalize(q):
    try:
        return q_mul(q, 1.0/q_length(q))
    except ZeroDivisionError:
        return q

def q_from_axis_angle(v, phi):
    q = v_mul(v_normalize(v), math.sin(phi / 2.0))
    q.append(math.cos(phi / 2.0))
    return q

def q_rotmatrix(q):
    m = [0.0] * 16
    m[0 * 4 + 0] = 1.0 - 2.0 * (q[1] * q[1] + q[2] * q[2])
    m[0 * 4 + 1] = 2.0 * (q[0] * q[1] - q[2] * q[3])
    m[0 * 4 + 2] = 2.0 * (q[2] * q[0] + q[1] * q[3])
    m[1 * 4 + 0] = 2.0 * (q[0] * q[1] + q[2] * q[3])
    m[1 * 4 + 1] = 1.0 - 2.0 * (q[2] * q[2] + q[0] * q[0])
    m[1 * 4 + 2] = 2.0 * (q[1] * q[2] - q[0] * q[3])
    m[2 * 4 + 0] = 2.0 * (q[2] * q[0] - q[1] * q[3])
    m[2 * 4 + 1] = 2.0 * (q[1] * q[2] + q[0] * q[3])
    m[2 * 4 + 2] = 1.0 - 2.0 * (q[1] * q[1] + q[0] * q[0])
    m[3 * 4 + 3] = 1.0
    return m

class Trackball(object):
    def __init__(self, theta=0, phi=0, zoom=1, distance=3):
        self.rotation = [0, 0, 0, 1]
        self.zoom = zoom
        self.distance = distance
        self.count = 0
        self.matrix = None
        self.RENORMCOUNT = 97
        self.TRACKBALLSIZE = 0.8
        self.set_orientation(theta, phi)
        self.x = 0.0
        self.y = 0.0

    def drag_to(self, x, y, dx, dy):
        viewport = glGetIntegerv(GL_VIEWPORT)
        width, height = float(viewport[2]), float(viewport[3])
        x = (x * 2.0 - width) / width
        dx = (2.0 * dx) / width
        y = (y * 2.0 - height) / height
        dy = (2.0 * dy) / height
        q = self.rotate(x, y, dx, dy)
        self.rotation = q_add(q, self.rotation)
        self.count += 1
        if self.count > self.RENORMCOUNT:
            self.rotation = q_normalize(self.rotation)
            self.count = 0
        m = q_rotmatrix(self.rotation)
        self.matrix = (GLfloat * len(m))(*m)

    def set_orientation(self, theta, phi):
        self.theta = theta
        self.phi = phi
        angle = self.theta * (math.pi / 180.0)
        sine = math.sin(0.5 * angle)
        xrot = [sine, 0.0, 0.0, math.cos(0.5 * angle)]
        angle = self.phi * (math.pi / 180.0)
        sine = math.sin(0.5 * angle)
        zrot = [0.0, 0.0, sine, math.cos(0.5 * angle)]
        self.rotation = q_add(xrot, zrot)
        m = q_rotmatrix(self.rotation)
        self.matrix = (GLfloat * len(m))(*m)

    def project(self, r, x, y):
        d = math.sqrt(x * x + y * y)
        if d < r * M_SQRT1_2:
            z = math.sqrt(r * r - d * d)
        else:
            t = r / M_SQRT2
            z = t * t / d
        return z

    def rotate(self, x, y, dx, dy):
        if not dx and not dy:
            return [0.0, 0.0, 0.0, 1.0]
        last = [x, y, self.project(self.TRACKBALLSIZE, x, y)]
        new = [x + dx, y + dx, self.project(self.TRACKBALLSIZE, x + dx, y + dy)]
        a = v_cross(new, last)
        d = v_sub(last, new)
        t = v_length(d) / (2.0 * self.TRACKBALLSIZE)
        if t > 1.0:
            t = 1.0
        if t < -1.0:
            t = -1.0
        phi = 2.0 * math.asin(t)
        return q_from_axis_angle(a, phi)
