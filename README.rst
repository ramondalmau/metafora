**Metafora**
============================

``metafora`` is a simple tool to parse METARs and TAFs. It is build on
the ``dataclasses``, which provides a simple way to create data classes
without the need to write methods, as well as on ``dataclasses-json``
for encoding and decoding dataclasses to and from JSON.

Installation
------------

::

   pip install metafora

Example
-------

Parse raw METAR and TAF

.. code:: python

    from metarfora import Metar, Taf, propagate_forecasts

    raw_metar = "EHAM 051825Z 02007KT 340V050 9999 FEW017 06/03 Q1042 NOSIG"
    raw_taf = "TAF EHAM 051721Z 0518/0624 36007KT CAVOK " \
              "BECMG 0523/0602 4500 MIFG " \
              "PROB30 TEMPO 0603/0609 0600 BCFG " \
              "BECMG 0608/0611 VRB02KT CAVOK " \
              "BECMG 0619/0622 4500 MIFG " \
              "PROB30 TEMPO 0622/0624 0600 BCFG"

    taf = Taf.from_text(raw_taf)
    metar = Metar.from_text(raw_metar)

Access their attributes

.. code:: python

   ...
   metar.wind.speed

Convert to nested dictionary

.. code:: python

   ...
   taf.to_dict()

Unify TAF forecasts

.. code:: python

   ...
   forecasts = unify_forecasts(taf.forecasts)

Convert a list of forecasts to JSON and vice-versa

.. code:: python

   ...
   taf_json = Taf.schema().dumps(taf_list, many=True)
   taf_list = Taf.schema().loads(taf_json, many=True)
