import math
from math import sin, cos, degrees

import svgwrite
from svgwrite.container import Group
from svgwrite.path import Path

class SVG(object):
    @staticmethod
    def color_hex(c):
        return '#%02x%02x%02x' % (c.red, c.green, c.blue)

    @classmethod
    def save(cls, image, filename, mosaic=False):
        # Use debug=False everywhere to turn off SVG validation,
        # which turns out to be obscenely expensive in this
        # library.
        DEBUG = False

        svg = svgwrite.Drawing(filename=filename,
                               style='background-color: black;',
                               size=(("%dpx" % (2 * image.r_outer),
                                      "%dpx" % (2 * image.r_outer))),
                               debug=DEBUG)

        group = Group(debug=DEBUG)
        group.translate(image.r_outer, image.r_outer)

        for y, row in enumerate(image.pixels):
            ring = image.rings[y]

            theta = 2 * math.pi / len(row)

            r1 = ring.center + image.r_ring / 2
            r2 = ring.center - image.r_ring / 2

            for x, c in enumerate(row):

                if mosaic:
                    path = Path(stroke='black',
                                stroke_width=1,
                                fill=cls.color_hex(c),
                                debug=DEBUG)

                    path.push((('M', 0, r2),
                               ('L', 0, r1),
                               ('A', r1, r1, 0, '0,0',
                                (r1 * sin(theta),
                                 r1 * cos(theta))),
                               ('L', r2 * sin(theta),
                                     r2 * cos(theta)),
                               ('A', r2, r2, 0, '0,1',
                                (0, r2))))
                else:
                    path = Path(stroke=cls.color_hex(c),
                                stroke_width=image.r_pixel,
                                fill='none',
                                debug=DEBUG)

                    path.push((('M', 0, ring.center),
                               ('A', ring.center, ring.center, 0, '0,0',
                                (ring.center * sin(theta),
                                 ring.center * cos(theta)))))

                path.rotate(180 - degrees(theta * (x + 1)),
                            center=(0, 0))

                group.add(path)

        svg.add(group)
        svg.save()
