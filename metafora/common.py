#!/usr/bin/env python
# coding: utf-8
"""
metafora - common dataclasses
"""
import re
from dataclasses import field, dataclass
from dataclasses_json import dataclass_json, config
from typing import Optional, List, Union

from metafora.utils import (
    convert_distance,
    convert_speed,
    convert_direction,
    Number,
)
from metafora.enums import *

WEATHER_DESCRIPTOR = "|".join(WeatherDescriptor.set())
WEATHER_PHENOMENA = "|".join(WeatherPrecipitation.set().union(WeatherObscuration.set()).union(OtherWeather.set()))

TIME_FORMAT = "(0[0-9]|1[0-9]|2[0-9]|3[0-1])(0[0-9]|1[0-9]|2[0-4])([0-5][0-9])"
DIRECTION_FMT = "0[0-9][0-9]|1[0-9][0-9]|2[0-9][0-9]|3[0-5][0-9]|360"


class Station(str):
    """
    Station class
    """

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the station from a token

        :param token: token
        :return: station instance or None if not successful
        """
        found = re.search("^([A-Z]{4})$", token)

        if not found:
            return None

        return str(found[0])


@dataclass_json
@dataclass
class Timestamp:
    """
    Time information
    """

    day: Number
    hour: Number
    minute: Number

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the time information from a token

        :param token: token
        :return: time instance or None if not successful
        """
        found = re.search("^" + TIME_FORMAT + "Z$", token)

        if not found:
            return None

        day = int(found[1])
        hour = int(found[2])
        minute = int(found[3])

        return cls(day=day, hour=hour, minute=minute)


@dataclass_json
@dataclass
class Wind:
    """
    Wind conditions
    Speed and gust are expressed in meters per second
    """

    speed: Number
    compass: str
    gust: Optional[Number] = field(default=0)

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the wind conditions from a token

        :param token: token
        :return: wind conditions instance or None if not successful
        """
        found = re.search(
            "^("
            + DIRECTION_FMT
            + "|VRB|///)P?([0-9]{2,3}|//)(GP?([0-9]{2,3}))?(KT|MPS|KPH)$",
            token,
        )

        if not found:
            return None

        # get unit
        unit = found[5]

        # get speed
        if found[2] == "//":
            # unknown speed
            speed = None
        else:
            speed = found[2].replace("/", "")
            speed = convert_speed(int(speed), unit)

        # get compass
        if found[1] == "VRB":
            # variable driection
            compass = "VRB"
        elif found[1] == "///":
            # unknown direction
            compass = None
        else:
            direction = int(found[1])
            compass = convert_direction(direction)

        # get gust
        if found[4]:
            gust = convert_speed(int(found[4]), unit)
        else:
            gust = 0

        return cls(speed=speed, compass=compass, gust=gust)


@dataclass_json
@dataclass
class VariableDirection:
    """
    Variable wind direction
    """

    direction_min: str
    direction_max: str

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the wind from a token

        :param token: token
        :return: wind instance or None if not successful
        """
        found = re.search("^(" + DIRECTION_FMT + ")V(" + DIRECTION_FMT + ")$", token)

        if not found:
            return None

        direction_min = int(found[1])
        direction_max = int(found[2])

        direction_min = convert_direction(direction_min)
        direction_max = convert_direction(direction_max)

        return VariableDirection(
            direction_min=direction_min, direction_max=direction_max
        )


@dataclass_json
@dataclass
class Visibility:
    """
    Visibility conditions
    Distance is expressed in meters
    """

    distance: Number
    cavok: Optional[bool]

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the visibility conditions from a token

        :param token: token
        :return: visibility conditions instance or None if not successful
        """
        found = re.search(
            "^(CAVOK|([0-9]{4})|([PM])?([0-9]{0,2})?(([1357])/(2|4|8|16))?SM|////)$",
            token,
        )

        if not found:
            return None

        cavok = False

        # get visibility and cavok flag
        if found[1] == "CAVOK":
            cavok = True
            distance = 9999
        elif found[1] == "////":
            distance = None
        else:
            if found[2]:
                distance = int(found[2])
            else:
                distance = 0 if not found[4] else int(found[4])

                if found[7]:
                    distance += int(found[6]) / int(found[7])

                distance = convert_distance(distance, "SM")

            distance = min(distance, 9999)

        return cls(distance=distance, cavok=cavok)


@dataclass_json
@dataclass
class Weather:
    """
    Weather conditions
    """

    intensity: Optional[str] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    descriptor: Optional[str] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    phenomena: Optional[str] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the weather conditions from a token

        :param token: token
        :return: weather conditions instance or None if not successful
        """
        expression = (
                "^([-+]|VC)?("
                + WEATHER_DESCRIPTOR
                + ")?("
                + WEATHER_PHENOMENA
                + ")?("
                + WEATHER_PHENOMENA
                + ")?("
                + WEATHER_PHENOMENA
                + ")?(NSW)?$"
        )
        found = re.search(expression, token)

        if not found:
            return None

        intensity = None
        descriptor = None
        phenomena = None

        # intensity
        if found[1]:
            intensity = found[1]

        # descriptor
        if found[2]:
            descriptor = found[2]

        # for all codes after intensity ...
        if found[3]:
            phenomena = ""
            for code in found.groups()[2:]:
                if code:
                    phenomena += code

        return cls(
            intensity=intensity,
            descriptor=descriptor,
            phenomena=phenomena,
        )


@dataclass_json
@dataclass
class Clouds:
    """
    Cloud conditions
    Height expressed in meters
    """

    amount: Optional[Union[str, int]] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    height: Optional[Number] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    cloud: Optional[str] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the cloud conditions from a token

        :param token: token
        :return: cloud conditions instance or None if not successful
        """
        found = re.search(
            "^((NSC|NCD|CLR|SKC|NOBS)|((VV|FEW|SCT|BKN|OVC|///)([0-9]{3}|///)(CB|TCU|///)?))$",
            token,
        )

        if not found:
            return None

        amount = None
        height = None
        cloud = None

        # get cloud height and amount
        if found[2] and found[2] in CloudCover.set():
            amount = found[2]
        elif found[5]:
            if found[5] != "///":
                height = convert_distance(int(found[5]) * 100, "FT")
            else:
                # unknown height
                height = None

            if found[4] in CloudCover.set():
                amount = found[4]

        # get cloud type
        if found[6] in CloudType.set():
            cloud = found[6]

        return cls(amount=amount, height=height, cloud=cloud)


def clouds_height(clouds: Union[List[Clouds], None]) -> Union[Number, None]:
    """
    Computes the ceiling based on cloud layers
    A cloud ceiling is the height of the first cloud layer that constitutes at least a broken (BKN) layer

    :param clouds: layers of clouds
    :return: the ceiling in meters
    """
    ceiling = 3048

    if clouds is None:
        return ceiling

    for c in clouds:
        if c.amount in ["BKN", "OVC", "VV"]:
            if c.height is not None:
                ceiling = min(ceiling, c.height)
            else:
                # ceiling could not be determined (///)
                # but there is a layer of clouds that constitutes at least a broken (BKN) layer
                ceiling = None
                break

    return ceiling


def clouds_cloud(clouds: Union[List[Clouds], None]) -> Union[str, None]:
    """
    Computes the most dangerous cloud based on cloud layers

    :param clouds: layers of clouds
    :return: the most dangerous cloud (if any)
    """
    if clouds is None:
        return None

    members = CloudType.list()
    idx = None
    for c in clouds:
        if c.cloud is not None:
            idx = max(members.index(c.cloud), 0 if idx is None else idx)

    if idx is not None:
        return members[idx]
    else:
        return None


def clouds_amount(clouds: Union[List[Clouds], None]) -> Union[str, None]:
    """
    Computes the largest layer cover in oktas
    , VV is considered 10 oktas (the maximum)

    :param clouds: layers of clouds
    :return: the most dangerous cloud (if any)
    """
    if clouds is None:
        return None

    members = CloudCover.list()
    idx = None
    
    for c in clouds:
        if c.amount is not None:
            idx = max(members.index(c.amount), 0 if idx is None else idx)

    if idx is not None:
        return (idx + 1) * 2
    else:
        return None


def simplify_clouds(clouds: List[Clouds]) -> Clouds:
    """
    Simplifies list of clouds

    :param clouds: layers of clouds
    :return: simplified clouds
    """
    return Clouds(
        height=clouds_height(clouds),
        cloud=clouds_cloud(clouds),
        amount=clouds_amount(clouds),
    )
