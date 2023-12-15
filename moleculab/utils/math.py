from typing import Tuple
from math import hypot, sqrt, acos, radians, degrees, dist
import numpy as np


def clamp(value: float or int, min_value: float or int = 0.0, max_value: float or int = 1.0) -> float or int:
    return min(max(value, min_value), max_value)


def map_value(val: float, src: Tuple[float, float], dst: Tuple[float, float] = (0.0, 1.0)):
    """
    Scale the given value from the scale of src to the scale of dst.
    """
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]
