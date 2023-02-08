#!/usr/bin/env python
# coding: utf-8
"""
metafora - some helping functions for ML
"""
from metafora.taf import Forecast
from metafora.metar import Metar
from metafora.common import simplify_clouds
from typing import Union, Dict, Optional


def ml_features(report: Union[Metar, Forecast], max_weather: Optional[int] = 2) -> Dict:
    """
    Extracts features that can be used to train ML models

    :param report: a Metar or Forecast report
    :param max_weather: maximum weather events that will be considered
    :return: dictionary of features
    """
    features = report.to_dict()

    # simplify clouds
    features["clouds"] = simplify_clouds(report.clouds).to_dict()

    # simplify weather
    weather = features.pop("weather", [])

    for i, w in enumerate(weather[:max_weather]):
        features["weather_{}".format(i)] = w

    return features
