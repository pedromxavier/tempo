import pylatex
from pathlib import Path
import random

WEEK_DAYS: int = 7
DAY_HOURS: int = 24
HOUR_MINS: int = 60

A4_W: float = 29.7
A4_H: float = 21.0


class Event:
    def __init__(
        self, d: int, D: int, h: int, H: int, m: int, M: int, *, label: str = ...
    ):
        self.__type_check(d, D, h, H, m, M)
        self.__value_check(d, D, h, H, m, M)

        self.d = d
        self.D = D
        self.h = h
        self.H = H
        self.m = m
        self.M = M

        self.label = label

        self._next = None
        self._down = None

        self._a = None
        self._b = None

    def __str__(self):
        return f"[{self.label}|{self.h:02d}:{self.m:02d}~{self.H:02d}:{self.M:02d}]"

    def __repr__(self):
        return f"Event({self.d}, {self.D}, {self.h}, {self.H}, {self.m}, {self.M}, label={self.label!r})"

    def __type_check(self, d: int, D: int, h: int, H: int, m: int, M: int):
        """"""
        if not isinstance(d, int):
            raise TypeError(f"'d' must be of type 'int', not '{type(d)}'")
        if not isinstance(D, int):
            raise TypeError(f"'D' must be of type 'int', not '{type(D)}'")
        if not isinstance(h, int):
            raise TypeError(f"'h' must be of type 'int', not '{type(h)}'")
        if not isinstance(H, int):
            raise TypeError(f"'H' must be of type 'int', not '{type(H)}'")
        if not isinstance(m, int):
            raise TypeError(f"'m' must be of type 'int', not '{type(m)}'")
        if not isinstance(M, int):
            raise TypeError(f"'M' must be of type 'int', not '{type(M)}'")

    def __value_check(self, d: int, D: int, h: int, H: int, m: int, M: int):
        """"""
        if d > D:
            raise ValueError("'d' must come before 'D'")
        if h > H:
            raise ValueError("'h' must come before 'D'")
        if m > M:
            raise ValueError("'m' must come before 'D'")

    @property
    def a(self):
        if self._a is None:
            self._a = HOUR_MINS * self.h + self.m
        return self._a

    @property
    def b(self):
        if self._b is None:
            self._b = HOUR_MINS * self.H + self.M
        return self._b


class Schedule:

    WEEK_MAP = {
        "de": [
            "Sontag",
            "Montag",
            "Dienstag",
            "Mittwoch",
            "Freitag",
            "Donnerstag",
            "Samstag",
        ],
        "en": [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ],
        "pt-BR": ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"],
    }

    class ScheduleError(Exception):
        pass

    def __init__(self, **params):
        self.__params_check(params)
        self.__pallete = {}
        self.__c = 0

        self.roots = [
            Event(i, i + 1, 0, 0, 0, 0, label=f"day{i}") for i in range(WEEK_DAYS)
        ]

        for i in range(WEEK_DAYS):
            self.roots[i]._next = self.roots[(i + 1) % WEEK_DAYS]

        self.PALLETE = self._PALLETE.copy()

    def __params_check(self, params: dict):
        self.params = {}

        if "seed" in params:
            self.params["seed"] = params["seed"]
        else:
            self.params["seed"] = None

        if "title" in params:
            self.params["title"] = params["title"]
        else:
            self.params["title"] = None

        if "subtitle" in params:
            self.params["subtitle"] = params["subtitle"]
        else:
            self.params["subtitle"] = None

        if "logo" in params:
            self.params["logo"] = params["logo"]
        else:
            self.params["logo"] = None

        if "logo-width" in params:
            self.params["logo-width"] = params["logo-width"]
        else:
            self.params["logo-width"] = None

        if "start" in params:
            self.params["start"] = params["start"]
        else:
            self.params["start"] = 6

        if "hours" in params:
            self.params["hours"] = params["hours"]
        else:
            self.params["hours"] = 18

        if "lang" in params:
            self.params["lang"] = params["lang"]
        else:
            self.params["lang"] = "en"

        if "left" in params:
            self.params["left"] = params["left"]
        else:
            self.params["left"] = 2.0  # cm

        if "right" in params:
            self.params["right"] = params["right"]
        else:
            self.params["right"] = 2.0  # cm

        if "top" in params:
            self.params["top"] = params["top"]
        else:
            self.params["top"] = 4.0  # cm

        if "bottom" in params:
            self.params["bottom"] = params["bottom"]
        else:
            self.params["bottom"] = 2.0  # cm

    def free(self, e: Event):
        for i in range(e.d, e.D):
            root = self.roots[i]

            while root._down is not None:
                root = root._down

                if root.a < e.a < root.b or root.a < e.b < root.b:
                    return False
                if e.a < root.a < e.b or e.a < root.b < e.b:
                    return False
                if e.a == root.a and e.b == root.b:
                    return False

        return True

    def search(self, e: Event):
        root = self.roots[e.d]

        while root._down is not None and e.h > root._down.h:
            root = root._down

        while root._down is not None and e.h == root._down.h and e.m > root._down.m:
            root = root._down

        return root

    def insert(self, e: Event):

        if not self.free(e):
            raise self.ScheduleError("The requested time is not available")

        root = self.search(e)

        if root._down is not None:
            e._down = root._down
        root._down = e

    def __str__(self):
        days = []
        for i in range(WEEK_DAYS):
            days.append([])
            root = self.roots[i]
            while root._down is not None:
                days[i].append(str(root))
                root = root._down
            days[i].append(str(root))
            days[i] = "->".join(days[i])

        return "\n".join(days)

    def latex(self, fpath: Path, tex: bool = False):
        if self.params["seed"] is not None:
            random.seed(self.params["seed"])

        self.PALLETE = self._PALLETE.copy()
        random.shuffle(self.PALLETE)

        doc = pylatex.Document(
            documentclass="standalone", document_options=["tikz"]
        )
        doc.packages.append(pylatex.Package(
            "firasans", options=["light", "sfdefault"]))
        with doc.create(pylatex.TikZ()) as pic:
            self._grid(pic)

        doc.generate_pdf(fpath, clean_tex=not tex)

    _PALLETE = [
        "blue",
        "red",
        "yellow",
        "orange",
        "brown",
        "violet"
    ]

    def _pallete(self):
        self.__c += 1
        return f"{self.PALLETE[self.__c % len(self.PALLETE)]}!30"

    def pallete(self, label: str):
        if label not in self.__pallete:
            self.__pallete[label] = self._pallete()
        return self.__pallete[label]

    def _grid(self, pic: pylatex.TikZ):

        l = self.params["left"]
        r = self.params["right"]
        t = self.params["top"]
        b = self.params["bottom"]

        h = b  # cm
        w = l  # cm
        W = A4_W - (l + r)  # cm
        H = A4_H - (t + b)  # cm

        if self.params["title"] is not None:
            xy = pylatex.TikZCoordinate(
                0.5 * A4_W,
                A4_H - 0.5 * t,
            )
            pic.append(pylatex.Command('Huge'))
            pic.append(pylatex.TikZNode(at=xy, text=self.params["title"]))
            pic.append(pylatex.Command('normalsize'))

        if self.params["subtitle"] is not None:
            xy = pylatex.TikZCoordinate(
                0.5 * A4_W,
                A4_H - 0.7 * t,
            )
            pic.append(pylatex.Command('Large'))
            pic.append(pylatex.TikZNode(at=xy, text=self.params["subtitle"]))
            pic.append(pylatex.Command('normalsize'))

        if self.params["logo"] is not None:
            lw = self.params["logo-width"]
            xy = pylatex.TikZCoordinate(
                w + 0.5 * lw,
                A4_H - 0.5 * t,
            )
            tx = pylatex.Command("includegraphics", arguments=[
                                 self.params["logo"]], options=[f"width={lw:.2f}cm"])
            pic.append(pylatex.TikZNode(at=xy, text=tx.dumps()))

        pic.append(pylatex.TikZDraw(
            ["(0, 0)", "rectangle", f"({A4_W}, {A4_H})"]))

        M = WEEK_DAYS
        N = self.params["hours"]
        S = self.params["start"]

        WEEK_MAP = self.WEEK_MAP[self.params['lang']]

        dx = (W / (M + 1))
        dy = (H / (N + 1))

        # -*- Vertical Lines and Day Names -*-
        for i in range(1, M + 1):
            x = w + i * dx
            y = h + H
            Y = h
            pic.append(pylatex.TikZDraw(
                [f"({x:.2f}, {y:.2f})", "--", f"({x:.2f}, {Y:.2f})"]))

            xx = x + 0.5 * dx
            yy = y - 0.5 * dy
            xy = pylatex.TikZCoordinate(round(xx, 2), round(yy, 2))
            pic.append(pylatex.TikZNode(at=xy, text=WEEK_MAP[i-1]))

        # -*- Finish Grid -*-
        x = w + W
        y = h
        Y = h + H
        pic.append(pylatex.TikZDraw(
            [f"({x:.2f}, {y:.2f})", "--", f"({x:.2f}, {Y:.2f})"]))

        # -*- Close Hours Section -*-
        x = w
        y = h
        Y = h + H - dy
        pic.append(pylatex.TikZDraw(
            [f"({x:.2f}, {y:.2f})", "--", f"({x:.2f}, {Y:.2f})"]))

        # -*- Horizontal Lines and Hourly Times -*-
        for j in range(1, N + 1):
            x = w
            X = w + W
            y = h + H - j * dy - dy

            xx = x + 0.5 * dx
            yy = y + 0.5 * dy
            xy = pylatex.TikZCoordinate(xx, yy)
            pic.append(pylatex.TikZNode(at=xy, text=f"{S+j-1:02d}:00"))
            pic.append(pylatex.TikZDraw(
                [f"({x:.2f}, {y:.2f})", "--", f"({X:.2f}, {y:.2f})"]))

        # -*- Finish Grid -*-
        x = w
        X = w + W
        y = h + H - dy
        pic.append(pylatex.TikZDraw(
            [f"({x:.2f}, {y:.2f})", "--", f"({X:.2f}, {y:.2f})"]))

        # -*- Close Days Section -*-
        x = w + dx
        X = w + W
        y = h + H
        pic.append(pylatex.TikZDraw(
            [f"({x:.2f}, {y:.2f})", "--", f"({X:.2f}, {y:.2f})"]))

        # -*- Place Events -*-
        for root in self.roots:
            while True:
                if root.a != root.b:
                    # -*- Draw Something -*-
                    x = w + dx * (root.d + 1)
                    X = w + dx * (root.D + 1)
                    y = h + H - dy * ((root.h - S + root.m / HOUR_MINS) + 1)
                    Y = h + H - dy * ((root.H - S + root.M / HOUR_MINS) + 1)
                    fill = self.pallete(root.label)
                    # opts = pylatex.TikZOptions(fill=fill)
                    pic.append(pylatex.NoEscape(
                        f"\\draw [text width={abs(X-x):.2f}cm, align=center, fill={fill}] ({x:.2f}, {y:.2f}) rectangle ({X:.2f}, {Y:.2f}) node[midway] {{{root.label}}};"))
                    # xx = 0.5 * (x + X)
                    # yy = 0.5 * (y + Y)
                    # xy = pylatex.TikZCoordinate(xx, yy)
                    # pic.append(pylatex.TikZNode(at=xy, text=root.label))
                if root._down is not None:
                    root = root._down
                else:
                    break


__all__ = ["Schedule", "Event"]
