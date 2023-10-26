=============================
🌦️ Metafora - Your Weather Wizard! ☀️
=============================

Welcome to **Metafora**, the tool for parsing meteorological aerodrome reports (METARs) and terminal area forecasts (TAFs) with ease. 🚀

What Is Metafora All About?
---------------------------

**Metafora** is your weather data partner. It's built on the robust foundation of `dataclasses`, simplifying data class creation without the need for extensive methods. It also harnesses the power of `dataclasses-json` for efficient encoding and decoding of dataclasses to and from JSON.

This tool is meticulously designed to streamline the creation of weather datasets, making it a breeze for developing machine learning that require meteorological data.

Installation
------------

Getting started is simple:

.. code-block:: shell

   pip install metafora

Examples
--------

These are just a few examples of the many possibilities **Metafora** offers. Feel free to explore and adapt the tool to your specific needs, whether you're a data enthusiast, meteorologist, or a machine learning practitioner. 

Parsing METAR and TAF
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from metafora import Metar, Taf

   raw_metar = "LEBL 260730Z 19003KT 160V290 9999 RA VV001 FEW045 OVC003 20/15 Q1006 NOSIG"
   raw_taf = "TAF LEBL 260500Z 2606/2706 26009KT 9999 FEW030 TX25/2613Z TN16/2706Z TEMPO 2607/2611 27014KT BECMG 2611/2613 23015G25KT BECMG 2619/2621 29010KT"

   taf = Taf.from_text(raw_taf)
   metar = Metar.from_text(raw_metar)

   # Access their attributes (e.g., wind speed)
   metar.wind.speed

Converting to a Nested Dictionary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Convert data to a structured nested dictionary
   taf.to_dict()

Converting to JSON
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Convert datasets to JSON and vice versa
   dummy_taf_list_before = [taf, taf]
   taf_json = Taf.schema().dumps(dummy_taf_list_before, many=True)
   dummy_taf_list_after = Taf.schema().loads(taf_json, many=True)
   assert dummy_taf_list_after == dummy_taf_list_before

Propagating TAF Forecasts
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Propagate TAF forecasts efficiently
   from metafora.taf import propagate_forecasts
   propagated_forecasts = propagate_forecasts(taf.forecasts)

Data Processing for Machine Learning
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Convert data to pandas dataframes for machine learning applications
   from metafora.engineering import reports_to_dataframe, process_tafs, process_metars
   from pprint import pprint

   # process a list of METARs or TAFs
   processed_metars = process_metars([{"time": "2023-10-26T07:30:00", "report": raw_metar}])
   processed_tafs = process_tafs(
       [{"time": "2023-10-26T05:00:00", "report": raw_taf}])

   # convert to pandas dataframe
   df_metar = reports_to_dataframe(processed_metars)
   df_taf = reports_to_dataframe(processed_tafs)

   # check the result!
   pprint(df_metar.to_dict(orient="records"))
   pprint(df_taf.to_dict(orient="records"))

Contributions Welcome
----------------------

We welcome contributions from the open-source community to make **Metafora** even better! If you are passionate about meteorological data or have expertise in related fields, we'd love to have you on board.

One specific area where we're looking for contributions is the implementation of `impunity`, a Python library consisting of a single decorator function designed to ensure the consistency of physical quantities. This feature can add tremendous value to our project.

- **Check out `impunity`**: [impunity Repository](https://github.com/achevrot/impunity)

Please feel free to fork the repository, make improvements, and submit pull requests. Your contributions will help us enhance the capabilities of **Metafora** and make it a more powerful tool for everyone. 🚀
