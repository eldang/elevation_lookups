#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# data source management



class BoundingBox:
    W: float
    S: float
    E: float
    N: float
    empty: bool = True

    def __init__(
        self,
        W: float = None, S: float = None, E: float = None, N: float = None
    ) -> None:
        if W is not None:
            self.W = W
            self.empty = False
        if S is not None:
            self.S = S
            self.empty = False
        if E is not None:
            self.E = E
            self.empty = False
        if N is not None:
            self.N = N
            self.empty = False

    def __str__(self) -> str:
        if self.empty:
            return '[]'
        else:
            return 'W: ' + str(self.W) + ' S: ' + str(self.S) \
                + ' E: ' + str(self.E) + ' N: ' + str(self.N)


class Coordinate:
    x: float
    y: float
    empty: bool = True

    def __init__(self, x: float = None, y: float = None) -> None:
        if x is not None:
            self.x = x
            self.empty = False
        if y is not None:
            self.y = y
            self.empty = False

    def __str__(self) -> str:
        if self.empty:
            return '()'
        else:
            return '(' + str(self.x) + ', ' + str(self.y) + ')'
