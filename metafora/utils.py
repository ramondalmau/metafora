#!/usr/bin/env python
# coding: utf-8
"""
metafora utilities
"""
from typing import Union

Number = Union[float, int]


def convert_speed(speed: Number, unit: str) -> float:
    """
    Convets speed to meters per second

    :param speed: speed in the original units
    :param unit: units in KT, KPH or MPS
    :return: speed in meters per second
    """
    if unit == "KT":
        return round(0.514444 * speed, 2)
    elif unit == "KPH":
        return round(0.277778 * speed, 2)
    elif unit == "MPS":
        return round(speed, 2)
    else:
        raise ValueError("Unknown speed unit {}. Speed unit must be KT, KPH or MPS".format(unit))


def convert_distance(distance: Number, unit: str) -> float:
    """
    Converts distance to meters

    :param distance: distance in the original units
    :param unit: units in FT, SM or M
    :return: distance in meters
    """
    if unit == "FT":
        return round(0.3048 * distance)
    elif unit == "SM":
        return round(1609.34 * distance)
    elif unit == "M":
        return round(distance)
    else:
        raise ValueError("Unknown distance unit {}. Distance unit must be FT, SM or M".format(unit))


def convert_pressure(pressure: Number, unit: str) -> float:
    """
    Converts pressure to hPa

    :param pressure: pressure in the original units
    :param unit: units in A or Q
    :return: pressure in hPa
    """
    if unit == "A":
        return round(pressure / 0.02953)
    elif unit == "Q":
        return round(pressure)
    else:
        raise ValueError("Unknown pressure unit {}. Pressure unit must be A or Q".format(unit))


def convert_direction(direction: Number) -> str:
    """
    Returns the compass of a wind direction in degrees

    :param direction: direction in degrees
    :return: compass
    """
    if 0 <= direction <= 360:
        return [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ][round(direction / 22.5) % 16]
    else:
        raise ValueError(
            "Wind direction must be in degrees. Thus, its value must be higher than 0 and lower than 360, "
            "while the provided value is {}".format(direction)
        )
