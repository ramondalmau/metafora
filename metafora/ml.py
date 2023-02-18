#!/usr/bin/env python
# coding: utf-8
"""
metafora - some helping functions for ML
"""
from metafora.taf import Forecast
from metafora.metar import Metar, runway_info_distance_max, runway_info_distance_min
from metafora.common import simplify_clouds
from typing import Union, Dict


def ml_features(report: Union[Metar, Forecast]) -> Dict:
    """
    Extracts features that can be used to train ML models

    :param report: a Metar or Forecast report
    :return: dictionary of features
    """
    features = report.to_dict()

    # simplify clouds
    features["clouds"] = simplify_clouds(report.clouds).to_dict()

    # simplify runway visual range
    if features.pop("runway_info", None):
        features["runway_info_min"] = runway_info_distance_min(report.runway_info).to_dict()
        features["runway_info_max"] = runway_info_distance_max(report.runway_info).to_dict()

    # flatten weather
    for i, w in enumerate(features.pop("weather", [])):
        features["weather_{}".format(i)] = w

    return features
