#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import os
from svg_path_tools import Path

SVG_TEMPLATE = """<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg">
<metadata>%(metadata)s</metadata>
<defs>
<font id="%(fontId)s" horiz-adv-x="1000" >
<font-face font-family="%(fontId)s" font-weight="400" font-stretch="normal" units-per-em="1000" ascent="850" descent="-150" />
<missing-glyph horiz-adv-x="1000" />
%(glyphs)s
</font>
</defs>
</svg>"""  # NOQA
GLYPH_TEMPLATE = """<glyph unicode="%(unicode)s" d="%(d)s" horiz-adv-x="%(adv)d" />"""  # NOQA
ALPHABET = u"aăâbcdefghiîjklmnopqrsștțuvwxyz"


def fixPath(pathStr, height=850, widthMultiplier=9.2):
    p = Path(pathStr).toJoined()
    minX, maxX, minY, maxY = p.getExtremes()
    # Moving the shape to (0, 0).
    p.translate(-minX, -minY)
    # Scaling it so that the height is the same as provided.
    p.scale(height / (maxY - minY))
    # Turning upside down.
    p.scale(1, -1)
    p.translate(0, height)

    genPath = p.toString('%d')

    return genPath, (maxX - minX) * widthMultiplier


def generateGlyphs(paths):
    glyphs = []
    for i, path in enumerate(paths):
        d, adv = fixPath(path)
        glyph = GLYPH_TEMPLATE % {
            'unicode': ALPHABET[i],
            'd': d,
            'adv': adv
        }
        glyphs.append(glyph)
    return '\n'.join(glyphs)


def main():
    dir = os.path.dirname(os.path.realpath(__file__))
    paths = json.loads(open(dir + '/input/paths.json').read())
    glyphs = generateGlyphs(paths)
    svg = SVG_TEMPLATE % {
        'metadata': 'Created by Paul Nechifor (http://nechifor.net/)',
        'fontId': 'sidrem',
        'glyphs': glyphs
    }

    f = open(dir + '/../static/sidrem.svg', 'w')
    f.write(svg.encode('utf-8'))
    f.close()


main()
