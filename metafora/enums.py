#!/usr/bin/env python
# coding: utf-8
"""
metafora - enumerators
"""
from enum import Enum


class CustomEnum(str, Enum):
    """
    Custom enum with additional functionalities
    """
    @classmethod
    def members(cls):
        """
        Returns the members of this enumerator

        :return: members
        """
        return set(k for k in cls.__members__.keys())


class CloudCover(CustomEnum):
    """
    Enumerator of cloud covers
    """
    NSC = "no significant clouds are observed"
    NCD = "nil cloud detected"
    SKC = "no significant changes expected"
    CLR = "clear skies"
    NOBS = "no observation"
    FEW = "a few"
    SCT = "scattered"
    BKN = "broken sky"
    OVC = "overcast sky"
    VV = "vertical visibility"


class CloudType(CustomEnum):
    """
    Enumerator of cloud types
    """
    CB = "cumulonimbus"
    TCU = "towering cumulus"


class WeatherDescriptor(CustomEnum):
    """
    Enumerator of weather descriptors
    """
    NSW = "no significant weather are observed"
    MI = "shallow"
    PR = "partial"
    BC = "patches of"
    DR = "low drifting"
    BL = "blowing"
    SH = "showers of"
    TS = "thunderstorms"
    FZ = "freezing"


class WeatherPrecipitation(CustomEnum):
    """
    Enumerator of weather precipitation
    """
    DZ = "drizzle"
    RA = "rain"
    SN = "snow"
    SG = "snow grains"
    IC = "ice crystals"
    PL = "ice pellets"
    GR = "hail"
    GS = "small hail"
    UP = "unknown"


class WeatherObscuration(CustomEnum):
    """
    Enumerator of weather obscuration
    """
    BR = "mist"
    FG = "fog"
    FU = "smoke"
    DU = "widespread dust"
    SA = "sand"
    HZ = "haze"


class OtherWeather(CustomEnum):
    """
    Enumerator of other weather phenomena
    """
    PY = "spray"
    VA = "volcanic ash"
    PO = "well-developed dust/sand whirls"
    SQ = "squalls"
    FC = "funnel cloud, tornado, or waterspout"
    SS = "sandstorm"
    DS = "duststorm"


class RunwayVisualRangeTrend(CustomEnum):
    """
    Enumerator of event tendencies
    """
    D = "decreasing"
    U = "increasing"
    N = "no tendency"


class ChangeEu(CustomEnum):
    """
    Enumerator of change indicators
    """
    BECMG = "expected to arise soon"
    TEMPO = "expected to arise temporarily"
    INTER = "expected to arise intermittent"


class ChangeUS(CustomEnum):
    """
    Enumerator of time indicators
    """
    FM = "from"
    AT = "at"
    TL = "until"
