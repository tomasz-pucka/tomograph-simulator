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


params = Params("examples/Kropka.jpg", 2, 50, 180)
image_original = imread(params.image_path, as_gray=True)
sinogram = tomograph.radon(image_original, params.theta, params.detector_quantity, params.span)

fig, (ax1, ax2) = plt.subplots(1, 2)
ax1.set_title("Original image")
ax2.set_title("Sinogram")
ax2.set_xlabel("Detector Index")
ax2.set_ylabel("Projection step")
ax1.imshow(image_original, cmap="gray")
ax2.imshow(sinogram, cmap="gray", aspect='auto')
plt.tight_layout()
plt.show()
