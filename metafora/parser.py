#!/usr/bin/env python
# coding: utf-8
"""
metafora - parser
"""
from dataclasses import fields, dataclass
from typing import Union, get_origin, get_args
import re


def sanitise_string(raw: str) -> str:
    """
    Remove duplicates spaces, newlines and tabs from string

    :param raw:
    :return:
    """
    return re.sub("[\t\\s]+", " ", raw).strip().rstrip('=')


@dataclass
class ParserMixIn:
    """
    Text parser
    """

    @classmethod
    def from_text(cls, token: str):
        """
        Parse parts using the fields of a structure

        :param token: raw text
        :return:
        """
        substrings = sanitise_string(token).split(" ")
        class_fields = fields(cls)
        kwargs = dict()

        # current field index
        j = 0

        # for each word
        for s in substrings:
            i = j

            # try to parse this substring
            # until exhausting all class fields
            while i < len(class_fields):
                cf = class_fields[i]

                # get class field type
                cf_type = cf.type

                # get class field name
                cf_name = cf.name

                # get origin of class field type
                if get_origin(cf_type) == Union:
                    cf_origin = get_args(cf_type)[0]
                else:
                    cf_origin = cf_type

                # if it is a list
                if get_origin(cf_origin) == list:
                    is_list = True
                    cf_origin = get_args(cf_origin)[0]
                else:
                    is_list = False

                # the base class can be parsed from text
                if hasattr(cf_origin, "from_text"):
                    result = cf_origin.from_text(s)

                    # parsed
                    if result:
                        if is_list:
                            if cf_name not in kwargs.keys():
                                kwargs[cf_name] = [result]
                            else:
                                kwargs[cf_name].append(result)

                            # keep using this field
                            j = i
                        else:
                            kwargs[cf_name] = result
                            # move to the next field
                            j = j + 1

                        # stop
                        break

                # move to next field
                i = i + 1

        return cls(**kwargs)
