#!/usr/bin/env python
# coding: utf-8
"""
metafora - some helping functions for engineering
"""
from metafora.taf import Forecast, Taf, propagate_forecasts
from metafora.metar import Metar, runway_info_distance_max, runway_info_distance_min
from metafora.common import simplify_clouds
from metafora.enums import WeatherPrecipitation, WeatherObscuration, OtherWeather
from typing import Union, Dict, List, Optional
from pandas import DataFrame, json_normalize, to_datetime, Timestamp, NaT, isnull
from datetime import datetime, timedelta
import re

PRECIPITATION_MEMBERS = frozenset(WeatherPrecipitation._member_names_)
OBSCURATION_MEMBERS = frozenset(WeatherObscuration._member_names_)
OTHER_MEMBERS = frozenset(OtherWeather._member_names_)

BASIC_COLS = [
    "station",
    "visibility_cavok",
    "visibility_distance",
    "clouds_height",
    "clouds_amount",
    "clouds_vertical_visibility",
    "wind_speed",
    "wind_gust",
    "wind_compass",
    "wind_shear",
]

BOOLEAN_COLS = [
    "precipitation",
    "obscuration",
    "other",
    "thunderstorms",
    "freezing",
    "showers",
    "snow",
    "ice",
    "hail",
    "fog",
    "clouds",
]

METAR_SPECIFIC_COLS = [
    "temperature_temperature",
    "temperature_dewpoint",
    "pressure",
]

TAF_SPECIFIC_COLS = [
    "indicator",
    "probability",
    "maxtemperature_value",
    "mintemperature_value",
]


def simplify_report(report: Union[Metar, Forecast]) -> Dict:
    """
    Simplifies a report (TAF or METAR) and converts the result into a basic dictionary

    :param report: a raw METAR or TAF report
    :return: simplified dictionary representation of the report
    """
    features = report.to_dict()

    # simplify clouds
    features["clouds"] = simplify_clouds(report.clouds).to_dict()

    # simplify runway visual range
    if features.pop("runway_info", None):
        features["runway_info_min"] = runway_info_distance_min(
            report.runway_info
        ).to_dict()
        features["runway_info_max"] = runway_info_distance_max(
            report.runway_info
        ).to_dict()

    # flatten weather
    for i, w in enumerate(features.pop("weather", [])):
        features["weather_{}".format(i)] = w

    return features


def time_from_reference(time: Timestamp, reference: datetime) -> datetime:
    """Determines the datetime of a metafora Timestamp from a reference datetime

    Args:
        time (Timestamp): metafora Timestamp
        reference (datetime): reference datetime

    Returns:
        datetime: datetime associated to the timestamp
    """
    # correct minute
    if time.minute == 60:
        time.minute = 0
        time.hour = min(time.hour + 1, 24)

    # correct hour
    if time.hour == 24:
        time.hour = 0
        increased_day = True
    else:
        increased_day = False

    result = reference.replace(hour=time.hour, minute=time.minute)

    # move to next day until they match
    while time.day != result.day:
        result = result + timedelta(days=1)

    # if increased day
    if increased_day:
        result = result + timedelta(days=1)

    return result


def process_tafs(tafs: List[Dict], errors: Optional[str] = "ignore") -> List[Dict]:
    """Processes list of TAFs with metafora
       Each element of the list must be a dictionary with the following keys
       - report: the raw TAF
       - time: the release time

    Args:
        tafs (List[Dict]): list of raw TAFs

    Returns:
        List[Dict]: processed TAFs
    """
    reports = []

    for t in tafs:
        # get release time
        time = t["time"]

        # convert to isoformat
        time_iso = datetime.fromisoformat(time)
        try:
            # parse TAF from raw text
            report = Taf.from_text(t["report"])

            # get station
            station = report.station

            # unify forecasts
            forecasts = propagate_forecasts(report.forecasts)

            for f in forecasts:
                # get validity period
                start_time = time_from_reference(f.validity.start_time, time_iso)
                end_time = time_from_reference(f.validity.end_time, time_iso)

                # extract ml features
                report = simplify_report(f)

                # set station as well as release time and validity times in isoformat
                report["time"] = time
                report["station"] = station
                report["validity"]["start_time"] = start_time.isoformat()
                report["validity"]["end_time"] = end_time.isoformat()

                # min and max temperatures are special cases ...
                if f.mintemperature is not None and f.mintemperature.time is not None:
                    report["mintemperature"]["time"] = time_from_reference(
                        f.mintemperature.time, time_iso
                    ).isoformat()

                if f.maxtemperature is not None and f.maxtemperature.time is not None:
                    report["maxtemperature"]["time"] = time_from_reference(
                        f.maxtemperature.time, time_iso
                    ).isoformat()

                # append the report
                reports.append(report)
        except Exception:
            if errors == "raise":
                raise ValueError("{} is not a valid TAF".format(t["report"]))

    return reports


def process_metars(metars: List[Dict], errors: Optional[str] = "ignore") -> List[Dict]:
    """Processes list of METARs with metafora
       Each element of the list must be a dictionary with the following keys
       - report: the raw METAR
       - time: the release time

    Args:
        metars (List[Dict]): list of raw METARs

    Returns:
        List[Dict]: processed METARs
    """
    reports = []

    for m in metars:
        try:
            # parse METAR from raw text
            metar = Metar.from_text(m["report"])

            # extract ml features
            report = simplify_report(metar)

            # set release time in isoformat
            report["time"] = m["time"]
            reports.append(report)
        except Exception:
            if errors == "raise":
                raise ValueError("{} is not a valid METAR".format(m["report"]))

    return reports


def machine_learning_features(df: DataFrame) -> DataFrame:
    """Simplifies the weather dataframe
       extracting only the most relevant information for aviation

    Args:
        weather (DataFrame): original weather dataframe

    Returns:
        DataFrame: simplified weather dataframe
    """
    # boolean columns to False by default
    df[BOOLEAN_COLS] = False

    for c in df.columns:
        if c.endswith("phenomena"):
            # precipitation phenomena
            phenomena = df[c].apply(
                lambda x: frozenset() if isnull(x) else frozenset(re.findall("..", x))
            )
            precipitation = phenomena.apply(
                lambda x: x.intersection(PRECIPITATION_MEMBERS)
            )

            # note that different types of precipitation occurring at the time of observation
            # are to be reported as one single group
            # with the dominant type of precipitation reported first
            df["precipitation"] = df["precipitation"] | precipitation.apply(any)

            # snow
            snow = precipitation.apply(
                lambda x: any(frozenset(["SN", "SG"]).intersection(x))
            )
            df["snow"] = df["snow"] | snow

            # hail
            hail = precipitation.apply(
                lambda x: any(frozenset(["GR", "GS"]).intersection(x))
            )
            df["hail"] = df["hail"] | hail

            # ice
            ice = precipitation.apply(
                lambda x: any(frozenset(["IC", "PL"]).intersection(x))
            )
            df["ice"] = df["ice"] | ice

            # obscuration phenomena
            obscuration = phenomena.apply(lambda x: x.intersection(OBSCURATION_MEMBERS))

            df["obscuration"] = df["obscuration"] | obscuration.apply(any)

            fog = obscuration.apply(lambda x: "FG" in x)
            df["fog"] = df["fog"] | fog

            # other phenomena
            other = phenomena.apply(lambda x: x.intersection(OTHER_MEMBERS))
            df["other"] = df["other"] | other.apply(any)

        elif c.endswith("descriptor"):
            # only one descriptor per weather level
            # thunderstorms
            status = (df[c] == "TS").fillna(False)
            df["thunderstorms"] = df["thunderstorms"] | status

            # showers
            status = (df[c] == "SH").fillna(False)
            df["showers"] = df["showers"] | status

            # freezing
            status = (df[c] == "FZ").fillna(False)
            df["freezing"] = df["freezing"] | status

    # general clouds (TCU or CB)
    if "clouds_cloud" in df.columns:
        df["clouds"] = df["clouds_cloud"].notnull()

    return df


def reports_to_dataframe(
    reports: List[Dict], drop_invalid: Optional[bool] = False
) -> DataFrame:
    """Converts list of processed reports (METARs or TAFs) to pandas dataframe
    where each row is a report and each column a feature

    Args:
        List (Dict): list of reports processed by metafora
        drop_invalid (Optional[bool], optional): drop invalid reports. Defaults to False.

    Returns:
        DataFrame: reports dataframe
    """
    # json normalize, back to pandas
    df = json_normalize(reports, sep="_")

    # convert time columns to datetime
    TIME_COLS = []
    for c in [
        "time",
        "validity_start_time",
        "validity_end_time",
        "maxtemperature_time",
        "mintemperature_time",
    ]:
        if c in df.columns:
            df[c] = to_datetime(df[c], errors="coerce")
            TIME_COLS.append(c)

    # specific columns
    if "validity_start_time" in TIME_COLS and "validity_end_time" in TIME_COLS:
        # TAF case
        SPECIFIC_COLS = TAF_SPECIFIC_COLS
        if drop_invalid:
            df.dropna(
                subset=["station", "time", "validity_start_time", "validity_end_time"],
                inplace=True,
            )

        # if max and min temperature times are missing
        for c in ["maxtemperature_time", "mintemperature_time"]:
            if c not in TIME_COLS:
                df[c] = NaT
    else:
        # METAR case
        SPECIFIC_COLS = METAR_SPECIFIC_COLS
        if drop_invalid:
            df.dropna(subset=["station", "time"], inplace=True)

    # cavok must be boolean
    if "visibility_cavok" in df.columns:
        df["visibility_cavok"] = df["visibility_cavok"].fillna(False)
    else:
        df["visibility_cavok"] = False

    # create simplified columns
    df = machine_learning_features(df)

    # enforce basic and specific columns
    for c in BASIC_COLS + SPECIFIC_COLS:
        if c not in df.columns:
            df[c] = None

    return df[BASIC_COLS + TIME_COLS + BOOLEAN_COLS + SPECIFIC_COLS]
