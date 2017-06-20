#!/usr/bin/env python2

import re
import math


class SPathList:

    def __init__(self, paths=None):
        self.paths = []
        if paths is not None:
            self.paths.extend(paths)

    def findNeighs(self, ignoreDist=600, maxDist=7.0, minPoints=3):
        for p in self.paths:
            p.path.setPoints()

        l = len(self.paths)
        for i in xrange(0, l-1):
            for j in xrange(i+1, l):
                ap = self.paths[i]
                bp = self.paths[j]
                a = ap.path
                b = bp.path
                dx = a.points[0] - b.points[0]
                dy = a.points[1] - b.points[1]
                dist = math.sqrt(dx*dx + dy*dy)

                if dist > ignoreDist:
                    continue
                dists = self.calcDists(a, b)
                n = len([1 for x in dists if x <= maxDist])
                if n >= minPoints:
                    print ap.id, bp.id
                    ap.neighs.append(bp)
                    bp.neighs.append(ap)

    def calcDists(self, a, b):
        ap = a.points
        bp = b.points
        dists = []
        for i in xrange(0, len(ap), 2):
            for j in xrange(0, len(bp), 2):
                dx = ap[i] - bp[j]
                dy = ap[i + 1] - bp[j + 1]
                dists.append(math.sqrt(dx*dx + dy*dy))
        dists.sort()
        return dists

    def getExtremes(self):
        xs = []
        ys = []

        for p in self.paths:
            for e in p.path.elems:
                for i in xrange(0, len(e.nums), 2):
                    xs.append(e.nums[i])
                    ys.append(e.nums[i+1])
        return min(xs), max(xs), min(ys), max(ys)

    def translate(self, trX, trY):
        for p in self.paths:
            for e in p.path.elems:
                for i in xrange(0, len(e.nums), 2):
                    e.nums[i] += trX
                    e.nums[i + 1] += trY

    def writeSvg(self, out, w, h):
        f = open(out, 'w')
        f.write("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>

<svg
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   version="1.1"
   width="%s"
   height="%s">
   <g transform='scale(0.1)'>
   """ % (w, h))
        for sPath in self.paths:
            sPath.path
            d = sPath.path.toString('%d')
            f.write('<path style="fill:#DDD;stroke:#333;stroke-width:40px" id="%s" d="%s"/>\n' % (sPath.id, d))  # NOQA
        f.write("</g></svg>\n")
        f.close()


class SPath:
    def __init__(self):
        self.path = None
        self.id = None
        self.index = -1
        self.name = None
        self.county = None
        self.neighs = []


class Path:

    ABSOLUTE = 'MLHVCSQTAZ'
    RELATIVE = 'mlhvcsqtaz'
    ABSOLUTE_SET = set(ABSOLUTE)
    RELATIVE_SET = set(RELATIVE)
    TYPES = ABSOLUTE + RELATIVE
    TYPES_REGEX = '([' + TYPES + '])'
    TYPES_SET = set(TYPES)

    def __init__(self, pathString=None):
        self.elems = []
        self.points = None
        if pathString is not None:
            self.addFromSvgString(pathString)

    def addFromSvgString(self, pathString):
        s = pathString.replace(',', ' ')
        s = re.sub(Path.TYPES_REGEX, r' \1 ', s)
        s = s.strip()
        v = re.split(r'\s+', s)

        type = None
        nums = []

        for i in v:
            if i in Path.TYPES_SET:
                if type is not None:
                    p = PathElem(type, nums)
                    self.elems.append(p)
                type = i
                nums = []
            else:
                nums.append(float(i))

        if type is not None:
            p = PathElem(type, nums)
            self.elems.append(p)

    def setPoints(self):
        self.points = []
        for p in self.elems:
            if p.type == 'z':
                continue
            if p.type not in set('MLC'):
                raise
            v = p.nums
            mul = PathElem.MULTIPL[p.type.lower()]
            for i in xrange(0, len(v), mul):
                self.points.extend([v[i+mul-2], v[i+mul-1]])

    def toString(self, numFormat='%.4f'):
        ret = ''
        for p in self.elems:
            ret += p.type
            ret += ' '.join([numFormat % x for x in p.nums])
        return ret

    def getExtremes(self):
        xs = []
        ys = []
        for e in self.elems:
            for i in xrange(0, len(e.nums), 2):
                xs.append(e.nums[i])
                ys.append(e.nums[i+1])
        return min(xs), max(xs), min(ys), max(ys)

    def translate(self, trX, trY):
        for e in self.elems:
            for i in xrange(0, len(e.nums), 2):
                e.nums[i] += trX
                e.nums[i + 1] += trY

    def scale(self, sx, sy=None):
        if sy is None:
            sy = sx
        for e in self.elems:
            for i in xrange(0, len(e.nums), 2):
                e.nums[i] *= sx
                e.nums[i + 1] *= sy

    def toAbsolute(self):
        ret = Path()
        x = 0
        y = 0
        for i, e in enumerate(self.elems):
            t = e.type
            if t in ('z', 'Z'):
                p = e
            elif t in Path.RELATIVE_SET:
                nr = PathElem.MULTIPL[t.lower()]
                nums = []
                for i in xrange(0, len(e.nums), nr):
                    for j in xrange(0, nr, 2):
                        nums.append(x + e.nums[i + j + 0])
                        nums.append(y + e.nums[i + j + 1])
                    x += e.nums[i + nr - 2]
                    y += e.nums[i + nr - 1]

                p = PathElem(t.upper(), nums)
            elif t in Path.ABSOLUTE_SET:
                p = e
                x = e.nums[len(e.nums)-2]
                y = e.nums[len(e.nums)-1]
            else:
                raise
            ret.elems.append(p)
        return ret

    def toJoined(self):
        ret = Path()
        ret.elems.append(self.elems[0])
        for e in self.elems[1:]:
            prev = ret.elems[-1]
            if e.type == prev.type:
                prev.nums.extend(e.nums)
            else:
                ret.elems.append(e)
        return ret

    def _addRel(self, v, x, y):
        ret = []
        for i in xrange(0, len(v), 2):
            ret.append(x + v[i])
            ret.append(y + v[i+1])
        return ret


class PathElem:
    MULTIPL = {
        'm': 2,
        'z': None,
        'l': 2,
        'h': 1,
        'v': 1,
        'c': 6,
        's': 4,
        'q': 4,
        't': 2,
        'a': 10
    }

    def __init__(self, type, nums):
        self.type = type
        self.nums = nums

        multipl = PathElem.MULTIPL[type.lower()]
        if multipl is None:
            if len(nums) != 0:
                raise TypeError()
        else:
            if len(nums) % multipl != 0:
                raise TypeError()

    def __str__(self):
        return '(%s %s)' % (self.type, ' '.join([str(x) for x in self.nums]))
    __repr__ = __str__


def test():
    p = Path('  m 4 5.5l  5,   10   L2e-3,999  z  ')
    print p.elems
    print p.toString('%d')


if __name__ == '__main__':
    test()
