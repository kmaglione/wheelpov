from __future__ import print_function

import io
from itertools import groupby

class Hex(object):
    @classmethod
    def save(cls, image, filename):
        file = io.open(filename, 'wb')

        pixel_bin = lambda p: ''.join(map(chr, p))

        offsets = []

        y_off = 0
        byte_off = 0
        for npixels, rings in groupby(image.rings,
                                      lambda r: r.pixels):
            offsets.append((y_off, byte_off))

            n = sum(1 for x in rings)

            for x in range(0, npixels):
                for y in range(y_off, y_off + n):
                    file.write(pixel_bin(image.pixels[y][x]))

            y_off += n
            byte_off += n * 3

        print('''
struct {
    uint8_t     y;
    uint16_t    bytes
} column_stops[] PROGMEM = {'''[1:])

        print(',\n'.join('    { %d, %d }' % o
                        for o in offsets))

        print('}')

        file.close()
