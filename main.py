import numpy as np
import matplotlib.pyplot as plt
import tomograph
import filter
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


params = Params("examples/sl100.jpg", 1, 100, 180)
image_original = imread(params.image_path, as_gray=True)
image_padded = make_image_square(image_original)
sinogram = tomograph.radon(image_padded, params.theta, params.detector_quantity, params.span)
sinogram_filtered = filter.ramp_filter(sinogram, "ramp")
image_reconstructed_filtered = tomograph.inverse_radon(sinogram_filtered, image_padded.shape[0], params.theta,
                                                       params.detector_quantity, params.span)
image_reconstructed = tomograph.inverse_radon(sinogram, image_padded.shape[0], params.theta, params.detector_quantity,
                                              params.span)

fig, ax = plt.subplots(2, 2)
ax[0, 0].set_title("Original image")
ax[0, 1].set_title("Sinogram")
ax[1, 0].set_title("Reconstructed image")
ax[1, 1].set_title("Filtered and reconstructed image")
ax[0, 1].set_xlabel("Detector Index")
ax[0, 1].set_ylabel("Projection step")
ax[0, 0].imshow(image_padded, cmap="gray")
ax[0, 1].imshow(sinogram, cmap="gray")
ax[1, 0].imshow(image_reconstructed, cmap="gray")
ax[1, 1].imshow(image_reconstructed_filtered, cmap="gray")
plt.tight_layout(0, -0.8, 0)
plt.show()
