#!/usr/bin/env python
# coding: utf-8
"""
metafora - metar
"""
import re
from dataclasses import field, dataclass
from dataclasses_json import dataclass_json, config
from typing import List, Optional
import warnings

warnings.filterwarnings(action="ignore", category=UserWarning)

from metafora.common import (
    Station,
    Timestamp,
    Wind,
    Visibility,
    Clouds,
    Weather,
    Number,
)
from metafora.parser import ParserMixIn
from metafora.utils import convert_distance, convert_pressure, convert_direction


@dataclass_json
@dataclass
class RunwayVisualRange:
    """
    Runway visual range (RVR)
    distances are expressed in meters
    """

    runway: Optional[str] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    distance: Optional[Number] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    distance_prefix: Optional[str] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    distance_min: Optional[Number] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    distance_max: Optional[Number] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    tendency: Optional[str] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the RVR from a token

        :param token: token
        :return: RVR instance or None if not successful
        """
        found = re.search(
            "^R([0-9]{2}[LCR]?)/(([PM])?([0-9]{4})V)?([PM])?([0-9]{4})(FT)?/?([UDN]?)$",
            token,
        )

        if not found:
            return None

        runway = None
        distance = None
        distance_prefix = None
        distance_min = None
        distance_max = None
        tendency = None

        if found[1]:
            runway = found[1]

        unit = "M"
        if found[7]:
            unit = found[7]

        if found[6]:
            if found[4]:
                distance_min = convert_distance(int(found[4]), unit)
                distance_max = convert_distance(int(found[6]), unit)
            else:
                distance = convert_distance(int(found[6]), unit)

            if found[5]:
                distance_prefix = found[5]
        else:
            # if distance is not give, return none
            return None

        if found[8]:
            tendency = found[8]

        return cls(
            runway=runway,
            distance=distance,
            distance_prefix=distance_prefix,
            distance_min=distance_min,
            distance_max=distance_max,
            tendency=tendency,
        )


@dataclass_json
@dataclass
class Temperature:
    """
    Temperature
    Temperature is expressed in degrees celcius
    """

    temperature: Number
    dewpoint: Optional[Number] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the temperature from a token

        :param token: token
        :return: visibility conditions instance or None if not successful
        """
        found = re.search("^(M?[0-9]{2})/(M?[0-9]{2}|X{2})?$", token)

        if not found:
            return None

        temperature = int(found[1].replace("M", "-"))

        if found[2] and len(found[2]) != 0 and found[2] != "XX":
            dewpoint = int(found[2].replace("M", "-"))
        else:
            # unknown dew point
            dewpoint = None

        return cls(temperature=temperature, dewpoint=dewpoint)


class Pressure(int):
    """
    Pressure conditions
    Pressure is expressed in hPa
    """

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the pressure from a token

        :param token: token
        :return: pressure conditions instance or None if not successful
        """
        found = re.search("^([QA])(////|[0-9]{4})$", token)

        if not found:
            return None

        if found[2] and found[2] != "////":
            unit = found[1]

            if unit == "A":
                pressure = int(found[2]) / 100
            else:
                pressure = int(found[2])

            pressure = int(convert_pressure(pressure, unit))
        else:
            pressure = None

        return pressure


@dataclass_json
@dataclass
class Metar(ParserMixIn):
    """
    METAR dataclass
    """

    station: Station
    time: Optional[Timestamp] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    wind: Optional[Wind] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    visibility: Optional[Visibility] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    runway_info: Optional[List[RunwayVisualRange]] = field(
        default_factory=list, metadata=config(exclude=lambda x: len(x) == 0)
    )
    weather: Optional[List[Weather]] = field(
        default_factory=list, metadata=config(exclude=lambda x: len(x) == 0)
    )
    clouds: Optional[List[Clouds]] = field(
        default_factory=list, metadata=config(exclude=lambda x: len(x) == 0)
    )
    temperature: Optional[Temperature] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    pressure: Optional[Pressure] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )


def runway_info_distance_min(runway_info: List[RunwayVisualRange]) -> RunwayVisualRange:
    """
    Gets compass of the runway with minimum distance

    :param clouds: list of RVR
    :return: compass and distance
    """    
    distance = None
    compass = None

    if runway_info is not None:
        for r in runway_info:
            if r.distance is not None:
                if distance is None or r.distance < distance:
                    distance = r.distance
                    compass = convert_direction(int(r.runway[:2]))
            elif r.distance_min is not None:
                if distance is None or r.distance_min < distance:
                    distance = r.distance_min
                    compass = convert_direction(int(r.runway[:2]))

    return RunwayVisualRange(runway=compass, distance=distance)


def runway_info_distance_max(runway_info: List[RunwayVisualRange]) -> RunwayVisualRange:
    """
    Gets compass of the runway with maximum distance

    :param clouds: list of RVR
    :return: compass and distance
    """    
    distance = None
    compass = None

    if runway_info is not None:
        for r in runway_info:
            if r.distance is not None:
                if distance is None or r.distance > distance:
                    distance = r.distance
                    compass = convert_direction(int(r.runway[:2]))
            elif r.distance_max is not None:
                if distance is None or r.distance_max > distance:
                    distance = r.distance_max
                    compass = convert_direction(int(r.runway[:2]))
                
    return RunwayVisualRange(runway=compass, distance=distance)
