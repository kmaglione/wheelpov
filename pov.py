from __future__ import print_function

import os
import sys

sys.path.insert(0,
                os.path.dirname(os.path.abspath(__file__)))

from wheelpov.image import RadialImage
from wheelpov.svg import SVG

ri = RadialImage(filename=sys.argv[1],
                 r_inner=33,
                 r_outer=33 + 333,
                 r_pixel=5,
                 npixels=48,
                 outer_pixels=256)

SVG.save(ri, sys.argv[2], mosaic=False)

# vim:se sts=4 sw=4 et ft=python:
