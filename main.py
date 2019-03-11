import numpy as np
import matplotlib.pyplot as plt
import tomograph
from skimage.io import imread


class Params:
    def __init__(self, image_path, theta, detector_quantity, span):
        self.image_path = image_path
        self.theta = np.deg2rad(float(theta))
        self.detector_quantity = int(detector_quantity)
        self.span = np.deg2rad(span)


def make_image_square(image_original):
    diagonal = np.sqrt(2) * max(image_original.shape)
    pad = [int(np.ceil(diagonal - s)) for s in image_original.shape]
    new_center = [(s + p) // 2 for s, p in zip(image_original.shape, pad)]
    old_center = [s // 2 for s in image_original.shape]
    pad_before = [nc - oc for oc, nc in zip(old_center, new_center)]
    pad_width = [(pb, p - pb) for pb, p in zip(pad_before, pad)]
    return np.pad(image_original, pad_width, mode='constant', constant_values=0)


params = Params("examples/CT_ScoutView.jpg", 2, 200, 180)
image_original = imread(params.image_path, as_gray=True)
image_padded = make_image_square(image_original)
sinogram = tomograph.radon(image_padded, params.theta, params.detector_quantity, params.span)

fig, (ax1, ax2) = plt.subplots(1, 2)
ax1.set_title("Original image")
ax2.set_title("Sinogram")
ax2.set_xlabel("Detector Index")
ax2.set_ylabel("Projection step")
ax1.imshow(image_padded, cmap="gray")
ax2.imshow(sinogram, cmap="gray")
plt.show()
