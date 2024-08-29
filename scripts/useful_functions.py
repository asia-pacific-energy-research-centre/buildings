# Useful functions
import numpy as np
from scipy.interpolate import interp1d

def generate_smooth_curve(num_points, shape, start_value, end_value, apex_point = None, apex_position = None):
    """
    Generates a smooth curve based on the specified shape.

    Args:
        num_points (int): The number of points to generate in the smooth curve.
        shape (str): The shape of the smooth curve ('increase', 'decrease',
                     'constant', 'peak', or 'bottom').
        start_value (float): The starting value of the curve.
        end_value (float): The ending value of the curve.
        apex_point (float): y-value of series where it peaks or bottoms.
                                     Only applicable for 'peak' or 'bottom' shapes.
        apex_position (int): where the peak or bottom occurs along the x-axis

    Returns:
        numpy.ndarray: The smooth curve values.
    """
    if shape == 'constant':
        return np.full(num_points, start_value)

    x = np.linspace(start_value, end_value, num_points)
    y = np.zeros(num_points)

    if shape == 'increase':
        y = start_value + (end_value - start_value) * ((x - start_value) / (end_value - start_value)) ** 2

    elif shape == 'decrease':
        y = end_value - (end_value - start_value) * ((end_value - x) / (end_value - start_value)) ** 2

    elif shape == 'peak' or shape == 'bottom':
        if apex_point is None:
            raise ValueError("Apex point must be specified for 'peak' or 'bottom' shapes.")
        if apex_position is None:
            raise ValueError("Apex position must specify where the peak or trough occurs as in integer.")

        x_left = np.linspace(start_value, apex_point, num_points - (num_points - apex_position))
        x_right = np.linspace(apex_point, end_value, num_points - apex_position)
        y_left = apex_point - (apex_point - start_value) * ((apex_point - x_left) / (apex_point - start_value)) ** 2
        y_right = apex_point + (end_value - apex_point) * ((x_right - apex_point) / (end_value - apex_point)) ** 2
        y[:num_points - (num_points - apex_position)] = y_left
        y[num_points - (num_points - apex_position):] = y_right

    else:
        raise ValueError("Invalid shape. Supported shapes are 'increase', 'decrease', 'constant', 'peak', or 'bottom'.")

    f = interp1d(x, y, kind = 'quadratic')
    interpolated_curve = f(np.linspace(start_value, end_value, num_points))

    return interpolated_curve
