import numpy as np
import bresenham
import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_coords(self, center, angle):
        s = math.sin(angle)
        c = math.cos(angle)
        x = self.x - center.x
        y = self.y - center.y
        nx = x * c - y * s
        ny = x * s + y * c
        x = nx + center.x
        y = ny + center.y
        return Point(round(x), round(y))


def generate_angles(theta):
    full_angle = np.pi * 2
    return [theta * i for i in range(int(np.ceil(full_angle / theta)))]


def radon(image_original, theta, detectors_quantity, span):
    angles = generate_angles(theta)
    sinogram = []
    h, w = image_original.shape
    detector_step = span / detectors_quantity
    center = Point(w // 2, h // 2)
    zero = Point(w // 2, 1)
    for angle in angles:
        source = zero.get_coords(center, angle)
        detectors = [angle + np.pi - (span / 2.0) + (k * detector_step) for k in range(detectors_quantity)]
        detectors = [zero.get_coords(center, detector) for detector in detectors]
        measurements = []
        for detector in detectors:
            path = bresenham.bresenham_indexes(source, detector)
            p1 = path[:, 0]
            p2 = path[:, 1]
            measurements.append(image_original[p1, p2].sum())
        sinogram.append(measurements)
    sinogram = sinogram / np.amax(sinogram)
    return sinogram
