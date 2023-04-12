import os
import re
import ROOT
import sys
#from TkAlExceptions import AllInOneError
import six


class AllInOneError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self._msg = msg
        return

    def __str__(self):
        return self._msg








def parsecolor(color):
    try: #simplest case: it's an int
        return int(color)
    except ValueError:
        pass

    try:   #kRed, kBlue, ...
        color = str(getattr(ROOT, color))
        return int(color)
    except (AttributeError, ValueError):
        pass

    if color.count("+") + color.count("-") == 1:  #kRed+5, kGreen-2
        if "+" in color:                          #don't want to deal with nonassociativity of -
            split = color.split("+")
            color1 = parsecolor(split[0])
            color2 = parsecolor(split[1])
            return color1 + color2

        if "-" in color:
            split = color.split("-")
            color1 = parsecolor(split[0])
            color2 = parsecolor(split[1])
            return color1 - color2

    raise AllInOneError("color has to be an integer, a ROOT constant (kRed, kBlue, ...), or a two-term sum or difference (kGreen-5)!")

def parsestyle(style):
    try: #simplest case: it's an int
        return int(style)
    except ValueError:
        pass

    try: #kStar, kDot, ...
        style = str(getattr(ROOT,style))
        return int(style)
    except (AttributeError, ValueError):
        pass

    raise AllInOneError("style has to be an integer or a ROOT constant (kDashed, kStar, ...)!")
