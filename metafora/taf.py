#!/usr/bin/env python
# coding: utf-8
"""
metafora - taf
Ramon Dalmau-Codina
October 2022
"""
from dataclasses import field, dataclass
from dataclasses_json import dataclass_json, config
from typing import List, Optional
import re

import warnings

warnings.filterwarnings(action="ignore", category=UserWarning)

from metafora.common import (
    Station,
    Context,
    Timestamp,
    Wind,
    Clouds,
    Weather,
    Visibility,
    TIME_FORMAT,
    Number
)
from metafora.parser import ParserMixIn, sanitise_string
from metafora.enums import ChangeEu

HOUR_FORMAT = "(0[0-9]|1[0-9]|2[0-9]|3[0-1])(0[0-9]|1[0-9]|2[0-3])"


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


class Probability(int):
    """
    Probability of change
    """

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the pressure from a token

        :param token: token
        :return: probability of change instance or None if not successful
        """
        found = re.search("^(PROB[0-9]{2})$", token)

        if not found:
            return None

        return int(found[0].replace("PROB", ""))


class Indicator(str):
    """
    Change indicator
    """

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the pressure from a token

        :param token: token
        :return: change indicator instance or None if not successful
        """
        found = re.search("^(" + "|".join(ChangeEu.members()) + ")$", token)

        if not found:
            return None

        return found[0]


# NOT USED
@dataclass_json
@dataclass
class MaximimTemperature:
    """
    Maximum Temperature
    Maximum Temperature is expressed in degrees celcius
    """

    value: Number
    time: Timestamp

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the temperature from a token

        :param token: token
        :return: visibility conditions instance or None if not successful
        """
        found = re.search("^TX(M?[0-9]{2})/(" + HOUR_FORMAT + ")Z$", token)

        if not found:
            return None

        value = int(found[1].replace("M", "-"))
        time = Timestamp.from_text(str(found[2]) + "00Z")

        return cls(value=value, time=time)


# NOT USED
@dataclass_json
@dataclass
class MinimumTemperature:
    """
    Minimum Temperature
    Minimum Temperature is expressed in degrees celcius
    """

    value: Number
    time: Timestamp

    @classmethod
    def from_text(cls, token: str):
        """
        Attempts to parse the temperature from a token

        :param token: token
        :return: visibility conditions instance or None if not successful
        """
        found = re.search("^TN(M?[0-9]{2})/(" + HOUR_FORMAT + ")Z$", token)

        if not found:
            return None

        value = int(found[1].replace("M", "-"))
        time = Timestamp.from_text(str(found[2]) + "00Z")

        return cls(value=value, time=time)


@dataclass_json
@dataclass
class Forecast(ParserMixIn):
    """
    Weather forecast dataclass
    """

    probability: Optional[Probability] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    indicator: Optional[Indicator] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    # only to ensure compatibility ... should not be default. This will be fixed in Python 3.10
    validity: Optional[Validity] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
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

    def __post_init__(self):
        if self.validity is None:
            raise ValueError("Validity is mandatory in forecasts")

        if self.indicator is None:
            if self.validity.start_time is None and self.validity.end_time is not None:
                self.indicator = Indicator("TL")
            elif self.validity.end_time is None and self.validity.start_time is not None:
                self.indicator = Indicator("FM")
            elif self.validity.start_time == self.validity.end_time:
                self.indicator = Indicator("AT")


@dataclass_json
@dataclass
class Taf(Context):
    """
    TAF dataclass
    """

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
            return None

        # extract context
        station = Station.from_text(found[3])
        time = Timestamp.from_text(found[4])

        # process peridos
        lines = re.sub(
            r"(PROB[0-9]{2}\sTEMPO|TEMPO|INTER|BECMG"
            + "|FM"
            + HOUR_FORMAT
            + "|AT"
            + HOUR_FORMAT
            + "|TL"
            + HOUR_FORMAT
            + ")",
            "\n\\g<1>",
            token.replace(found[0], ""),
        ).splitlines()

        # forecasts
        forecasts = [Forecast.from_text(line) for line in lines]

        # create taf instance
        return cls(station=station, time=time, forecasts=forecasts)


def propagate_forecasts(taf: Taf) -> Taf:
    """
    Propagates times in taf

    :param taf:
    :return:
    """
    forecasts = [forecast.to_dict() for forecast in taf.forecasts]

    # prevailing weather conditions
    prevailing = forecasts[0]
    propagated_forecasts = [prevailing]

    for change in forecasts[1:]:
        # current is the prevailing conditions
        current = prevailing.copy()

        # get indicator
        indicator = change.get("indicator", None)

        # update fields of prevailing weather
        current.update(change)

        if indicator in ('BECMG', 'FM'):
            current['validity']['end_time'] = prevailing['validity']['end_time'].copy()
            prevailing['validity']['end_time'] = current['validity']['start_time'].copy()
            prevailing = current

        propagated_forecasts.append(current)

    taf.forecasts = [Forecast.from_dict(forecast) for forecast in propagated_forecasts]
    return taf


if __name__ == "__main__":
    from pprint import pprint

    text = (
        "TAF LEGE 050500Z 0506/0606 02008KT CAVOK TX17/0513Z TN02/0606Z BECMG 0514/0516 VRB04KT BECMG 0602/0604 02012KT"
    )
    taf = Taf.from_text(text)
    pprint(propagate_forecasts(taf))
    #test = Taf.schema().dump([taf, taf], many=True)


