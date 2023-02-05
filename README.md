# **METAFORA** :cloud: :sunny:

`metafora` is a simple tool to parse METARs and TAFs.
It is build on the `dataclasses`, which provides a simple way to create data classes without the need to write methods, as well as on `dataclasses-json` for encoding and decoding dataclasses to and from JSON.

## Installation

 ```
 will come soon
 ```

## Example

Parse raw METAR and TAF

```python
from metarfora import Metar, Taf, propagate_forecasts

raw_metar = "ULLI 041030Z 01005MPS 340V040 5000 R18R/1000FTD -SN SCT010 BKN018 VV000 M01/M05 A//// NOSIG"
raw_taf = (
    "TAF EHAM 041118Z 0412/0518 21005KT 9999 BKN040"
    "BECMG 0413/0416 7000 -DZ BKN012 "
    "TEMPO 0415/0501 3500 DZ BKN006 "
    "PROB30 TEMPO 0415/0501 2000 DZ BR BKN003 "
    "BECMG 0423/0502 9999 NSW BKN025 "
    "BECMG 0503/0506 35018KT RA"
    "TEMPO 0503/0506 4000 -DZ BKN008 "
    "BECMG 0515/0518 CAVOK 01008KT NSW"
)

taf = Taf.from_text(raw_taf)
metar = Metar.from_text(text)
```

Access their attributes
```python
...
metar.wind.speed
```

Convert to nested dictionary

```python
...
taf.to_dict()
```

Process TAF periods

```python
...
taf = propagate_forecasts(taf)
```

Convert a list of forecasts to JSON and vice-versa

```python
...
taf_json = Taf.schema().dumps(taf_list, many=True)
taf_list = Taf.schema().loads(taf_json, many=True)
```