import utils.utils as utils
import numpy as np

obj = {
    'power': [100, 200, 300],
    'time': [1, 2, 3],
    'distance': [10, 20, 30]
}

utils.write_json(np.array([100, 200, 300]), np.array([1, 2, 3]), np.array([10, 20, 30]))