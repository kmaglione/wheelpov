from __future__ import print_function

import signal
import subprocess
from collections import namedtuple

from wand.image import Image

Ring = namedtuple('Ring', ('center', 'pixels'))

RGB = namedtuple('RGB', ('red', 'green', 'blue'))

constrain = lambda v, min_, max_: min(max_, max(min_, v))

class RadialImage(object):
    def __init__(self, filename, r_inner, r_outer, r_pixel, npixels, outer_pixels):
        self.filename = filename

        self.r_inner = r_inner
        self.r_outer = r_outer
        self.r_pixel = r_pixel
        self.r_ring  = float(r_outer - r_inner) / npixels

        self.outer_pixels = outer_pixels
        self.npixels = npixels


        # Compute resolution changes
        Res = namedtuple('Res', ('r', 'pixels'))
        resolution = [Res(r_outer, outer_pixels)]
        p = 1
        while resolution[-1].r > r_inner:
            r = r_outer * 1. / (1 << p)
            resolution.append(Res(r, 256 >> p))

            p += 1


        # Compute ring geometry
        rings = []
        ring = 0
        r = r_outer

        for i in range(0, npixels):
            center = r - self.r_ring / 2
            rings.append(Ring(center=center,
                              pixels=resolution[ring].pixels))

            for j in range(ring, len(resolution)):
                if resolution[j].r > center:
                    ring = j

            r -= self.r_ring

        self.rings = rings

    _pixels = None

    @property
    def pixels(self):
        if not self._pixels:
            with Image(filename=self.filename) as image:
                size = image.size

            # Compute inner radius cut-off for depolar distortion
            r = int(round(size[1]
                            * (float(self.r_inner) / self.r_outer)
                            / 2))

            # Wand does not support distortions :/
            args = ('convert', self.filename, '-distort', 'DePolar', '0,%d' % r, '-')

            p = subprocess.Popen(args, stdout=subprocess.PIPE,
                                 preexec_fn=lambda: signal.signal(signal.SIGPIPE,
                                                                  signal.SIG_DFL))


            with Image(blob=p.communicate(None)[0]) as image:
                # Extract pixels
                img = None
                pixels = []
                for y, ring in enumerate(self.rings):
                    if not img or img.width != ring.pixels:
                        img = image.clone()
                        img.resize(ring.pixels, self.npixels)

                    pixels.append(tuple(self.rgb(img[x, -(y + 1)])
                                        for x in range(0, ring.pixels)))

                self._pixels = tuple(pixels)

        return self._pixels

    @staticmethod
    def rgb(c):
        with c:
            return RGB(int(round(0xff * constrain(c.red, 0, 1))),
                       int(round(0xff * constrain(c.green, 0, 1))),
                       int(round(0xff * constrain(c.blue, 0, 1))))

# vim:se sts=4 sw=4 et ft=python:
