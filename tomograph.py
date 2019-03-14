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


def radon(image, theta, detector_quantity, span):
    emitter_angles = generate_angles(theta)
    sinogram = []
    h, w = image.shape
    detector_step = span / detector_quantity
    center = Point(w // 2, h // 2)
    base = Point(w // 2, 1)
    halfspan = span / 2.0
    for emitter_angle in emitter_angles:
        source = base.get_coords(center, emitter_angle)
        detectors_angles = [emitter_angle + np.pi - halfspan + k * detector_step for k in range(detector_quantity)]
        detectors_positions = [base.get_coords(center, angle) for angle in detectors_angles]
        rays = []
        for detector in detectors_positions:
            path = bresenham.bresenham_indexes(source, detector)
            path_x_coords = path[:, 0]
            path_y_coords = path[:, 1]
            rays.append(image[path_x_coords, path_y_coords].sum())
        sinogram.append(rays)
    sinogram = sinogram / np.amax(sinogram)
    return sinogram


def inverse_radon(sinogram, size, theta, detector_quantity, span):
    emitter_angles = generate_angles(theta)
    height = width = size
    img = np.zeros((height, width))
    detector_step = span / detector_quantity
    w, h = height - 5, width - 5
    center = Point(int(w / 2), int(h / 2))
    base = Point(int(w / 2), 0)
    halfspan = span / 2.0
    for sinogram_projection, emitter_angle in zip(sinogram, emitter_angles):
        source = base.get_coords(center, emitter_angle)
        detectors_angles = [emitter_angle + np.pi - halfspan + k * detector_step for k in range(detector_quantity)]
        detectors_positions = [base.get_coords(center, angle) for angle in detectors_angles]
        for i, detector in enumerate(detectors_positions):
            path = bresenham.bresenham_indexes(source, detector)
            img[path[:, 0], path[:, 1]] += sinogram_projection[i]
    return np.array(img)
