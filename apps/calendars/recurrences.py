import datetime as dt
# possible repetition frequencies
from gcsa.recurrence import _DayOfTheWeek


recurrence_keys = {
    "BYSECOND": "by_second",
    "BYMINUTE": "by_minute",
    "BYHOUR": "by_hour",
    "BYDAY": "by_week_day",
    "BYMONTH": "by_month",
    "BYYEARDAY": "by_year_day",
    "BYWEEKNO": "by_week",
    "BYMONTHDAY": "by_month_day",
    "BYSETPOS": "by_set_pos",
    "WKST": "week_start",
    
}


def clean_recurrence(recurrence) -> tuple:
    recurrence_dict = {}
    datetime_format = "%Y%m%dT%H%M%SZ"
    
    # split it to remove the str "RULE:"
    recurrence_rule = recurrence.split(":")[0]
    recurrence = recurrence.split(":")[1]
    if recurrence_rule in ("RDATE", "EXDATE"):
        recurrence_dict["dts"] = dt.datetime.strptime(recurrence, datetime_format)
    else:
        for r in recurrence.split(";"):

        # split it to remove the str "="
            r = r.split("=")

            # pass the key of the dict to avoid error by correspondinging it to gcsa key
            r[0] = recurrence_keys.get(r[0]) or r[0].lower()
            recurrence_dict[r[0]] = r[1]

            # split it to find if there is more than one value, if so then make a list with it.
            if r[1].find(",") != -1:
                if r[0] == "by_week_day":
                    r[1] = [_DayOfTheWeek(_) for _ in r[1].split(",")]
                else:
                    r[1] = [int(_) for _ in r[1].split(",")]
            elif r[0] == "by_week_day":
                r[1] = [_DayOfTheWeek(_) for _ in r[1].split(",")]
            elif r[0] == "until":
                r[1] = dt.datetime.strptime(r[1], datetime_format)
            elif r[0] in ("count", "interval", "by_month_day", "by_year_day"):
                r[1] = int(r[1])
            recurrence_dict[r[0]] = r[1]
    
    return recurrence_rule, recurrence_dict