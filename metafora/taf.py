#!/usr/bin/env python
# coding: utf-8
"""
metafora - taf
"""
from dataclasses import field, dataclass
from dataclasses_json import dataclass_json, config
from typing import List, Optional
import re

import warnings

warnings.filterwarnings(action="ignore", category=UserWarning)

from metafora.common import (
    Station,
    Timestamp,
    Wind,
    Clouds,
    Weather,
    Visibility,
    TIME_FORMAT,
    Number,
)
from metafora.parser import ParserMixIn, sanitise_string

HOUR_FORMAT = "(0[0-9]|1[0-9]|2[0-9]|3[0-1])(0[0-9]|1[0-9]|2[0-3])"
CHANGE_SEARCH = (
    r"^(PROB[0-9]{2}\sTEMPO)|(TEMPO)|(INTER)|(BECMG)|(FM"
    + HOUR_FORMAT
    + ")|(AT"
    + HOUR_FORMAT
    + ")|(TL"
    + HOUR_FORMAT
    + ")"
)
CHANGE_SUB = (
    r"(PROB[0-9]{2}\sTEMPO|TEMPO|INTER|BECMG|FM"
    + HOUR_FORMAT
    + "|AT"
    + HOUR_FORMAT
    + "|TL"
    + HOUR_FORMAT
    + ")"
)


@dataclass_json
@dataclass
class Validity:
    """
    Valdity period
    """

    start_time: Optional[Timestamp] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    end_time: Optional[Timestamp] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the validity period information from a token

        :param token: token
        :return: validity instance or None if not successful
        """
        found = re.search(
            "^((AT|FM|TL)"
            + TIME_FORMAT
            + ")|("
            + HOUR_FORMAT
            + "/"
            + HOUR_FORMAT
            + ")$",
            token,
        )

        if not found:
            return None

        start_time = None
        end_time = None

        if found[1]:
            time = Timestamp.from_text(
                str(found[3]) + str(found[4]) + str(found[5]) + "Z"
            )
            if found[2] == "FM":
                start_time = time
                end_time = None
            elif found[2] == "TL":
                start_time = None
                end_time = time
            elif found[2] == "AT":
                start_time = time
                end_time = time
        else:
            start_time = Timestamp.from_text(str(found[7]) + str(found[8]) + "00Z")
            end_time = Timestamp.from_text(str(found[9]) + str(found[10]) + "00Z")

        return cls(start_time=start_time, end_time=end_time)


@dataclass_json
@dataclass
class Forecast(ParserMixIn):
    """
    Weather forecast dataclass
    """

    validity: Validity

    wind: Optional[Wind] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    visibility: Optional[Visibility] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    weather: Optional[List[Weather]] = field(
        default_factory=list, metadata=config(exclude=lambda x: len(x) == 0)
    )
    clouds: Optional[List[Clouds]] = field(
        default_factory=list, metadata=config(exclude=lambda x: len(x) == 0)
    )
    probability: Optional[Number] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    indicator: Optional[str] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )


@dataclass_json
@dataclass
class Taf:
    """
    TAF dataclass
    """

    station: Station
    time: Timestamp
    forecasts: List[Forecast]

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the TAF from a token

        :param token: token
        :return: TAF instance or False if not successful
        """
        # check if it follows a TAF format
        found = re.search(
            "^(PROV\\s)?TAF\\s(AMD\\s|COR\\s)?([A-Z]{4})\\s(" + TIME_FORMAT + "Z)",
            sanitise_string(token),
        )

        if not found:
            raise ValueError("The report '{}' does not look like a TAF".format(token))

        # extract context
        station = Station.from_text(found[3])
        time = Timestamp.from_text(found[4])

        # process peridos
        lines = re.sub(CHANGE_SUB, "\n\\g<1>", token.replace(found[0], "")).splitlines()

        # forecasts
        forecasts = []
        for line in lines:
            probability = None
            found = re.search(CHANGE_SEARCH, line)
            if found:
                indicator = found[0]
                if indicator.startswith(("FM", "AT", "TL")):
                    indicator = indicator[:2]
                elif indicator.startswith("PROB"):
                    probability = int(indicator[4:6])
                    indicator = "TEMPO"
            else:
                indicator = None

            forecast = Forecast.from_text(line)
            forecast.indicator = indicator
            forecast.probability = probability
            forecasts.append(forecast)

        # create taf instance
        return cls(station=station, time=time, forecasts=forecasts)


def propagate_forecasts(taf: Taf) -> Taf:
    """
    Propagates times in taf

    :param taf:
    :return:
    """
    # prevailing weather conditions
    forecasts = [forecast.to_dict() for forecast in taf.forecasts]
    prevailing = forecasts[0]
    propagated = [prevailing]

    for forecast in forecasts[1:]:
        # current is the prevailing conditions
        current = prevailing.copy()

        # get indicator
        indicator = forecast.get("indicator", None)

        # update fields of prevailing weather
        current.update(forecast)

        if indicator in ("BECMG", "FM"):
            current["validity"]["end_time"] = prevailing["validity"]["end_time"].copy()
            prevailing["validity"]["end_time"] = current["validity"][
                "start_time"
            ].copy()
            prevailing = current

        propagated.append(current)

    forecasts = [Forecast.from_dict(forecast) for forecast in propagated]
    return Taf(station=taf.station, time=taf.time, forecasts=forecasts)
