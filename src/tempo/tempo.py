import re
import yaml
import argparse
from cstream import stderr
from pathlib import Path

from .tempolib import Schedule, Event

RE_FLAG = re.UNICODE
RE_TIME = re.compile(r"^([0-1][0-9]|2[0-3])\:([0-5][0-9])\-([0-1][0-9]|2[0-3])\:([0-5][0-9])$", RE_FLAG)
RE_DAYS = re.compile(r"^([a-z]+)\-([a-z]+)$", RE_FLAG)

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

LANG_DAY_MAP = {
    "en" : {
        "sun": 0,
        "mon": 1,
        "tue": 2,
        "wed": 3,
        "thu": 4,
        "fri": 5,
        "sat": 6,
    },
    "pt-BR" : {
        "dom": 0,
        "seg": 1,
        "ter": 2,
        "qua": 3,
        "qui": 4,
        "sex": 5,
        "sab": 6,
    }
}

def event(day_A, day_B, time_A, time_B):
    return (day_A, day_B, time_A, time_B)

def parse(fname: str) -> int:
    """\
    """

    fpath = Path(fname)

    if not fpath.exists() or not fpath.is_file():
        stderr << f"Error: File {fname!r} doesn't exists"
        return EXIT_FAILURE

    with fpath.open(encoding="utf-8") as file:
        data = yaml.load(file, Loader=yaml.Loader)

    if "config" in data:
        conf = data["config"]
        if "lang" in conf:
            lang = conf["lang"]
            if lang not in LANG_DAY_MAP:
                stderr << f"Invalid language '{lang}'"
                return EXIT_FAILURE
            else:
                DAY_MAP = LANG_DAY_MAP[lang]
        else:
            lang = "en"

        if "title" in conf:
            title = conf["title"]
        else:
            title = None
    else:
        lang = "en"

    del data["config"]

    schedule = Schedule(lang=lang, title=title)

    for days_ in data:

        days: set[int] = set()

        for day_ in days_.split(","):
            re_match = RE_DAYS.match(day_)

            if re_match is not None:
                day_a = re_match.group(1)
                if day_a not in DAY_MAP:
                    stderr << f"Invalid day '{day_a}' for language '{lang}'"
                    return EXIT_FAILURE
                day_b = re_match.group(2)
                if day_b not in DAY_MAP:
                    stderr << f"Invalid day '{day_a}' for language '{lang}'"
                    return EXIT_FAILURE
                for day__ in range(DAY_MAP[day_a], DAY_MAP[day_b]+1):
                    days.add(day__)
            elif day_ not in DAY_MAP:
                stderr << f"Invalid day '{day_}' for language '{lang}'"
                return EXIT_FAILURE
            else:
                days.add(DAY_MAP[day_])

        for time in data[days_]:
            re_match = RE_TIME.match(time)
            if re_match is None:
                stderr << f"Invalid time spec '{time}'"
                return EXIT_FAILURE

            h, m = (int(re_match.group(1)), int(re_match.group(2)))
            H, M = (int(re_match.group(3)), int(re_match.group(4)))
            
            for d in days:
                e = Event(d, d+1, h, H, m, M, label=data[days_][time])

                schedule.insert(e)
            

    schedule.latex(fpath.with_suffix(""))

    return EXIT_SUCCESS


def main():
    """\
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("source", type=str, help="Source code.")

    args = parser.parse_args()

    code = parse(args.source)

    exit(code)


