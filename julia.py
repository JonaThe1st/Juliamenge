import time
import numpy as np

STANDARD_BOUNDS = (-1.5, 1.5, -1.5, 1.5)

def julia(user_input, resolution, bounds=STANDARD_BOUNDS):
    c, max_it, radius = user_input

    xmin, xmax, ymin, ymax = bounds
    width = xmax - xmin
    height = ymax - ymin
    ratio = width/height
    if width > height:
        res_x = resolution
        res_y = int(ratio**-1 * res_x)
    else:
        res_y = resolution
        res_x = int(ratio * res_y)

    x = np.linspace(xmin, xmax, res_x).reshape(1, res_x)
    y = np.linspace(ymin, ymax, res_y).reshape(res_y, 1)
    z = x + 1j * y

    m = np.full(z.shape, True, dtype=bool)

    start = time.time()

    for _ in range(max_it):
        zm = z[m]
        for _ in range(10):
            zm = zm ** 2 + c

        z[m] = zm
        m[np.abs(z) > radius] = False

    res = np.where(m, 0, 1)
    print(time.time() - start)

    return np.flip(res, 0)
