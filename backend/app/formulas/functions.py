from __future__ import annotations
"""
Built-in spreadsheet functions.

Each function takes a list of evaluated arguments and returns a value.
Arguments can be: float, str, bool, None, list[value] (from range expansion), or error strings.
"""

import math
import re
import statistics
from datetime import date, datetime, timedelta
from typing import Any, Callable

# Error constants
ERR_VALUE = "#VALUE!"
ERR_DIV0 = "#DIV/0!"
ERR_REF = "#REF!"
ERR_NAME = "#NAME?"
ERR_NA = "#N/A"
ERR_NUM = "#NUM!"
ERR_NULL = "#NULL!"

ALL_ERRORS = {ERR_VALUE, ERR_DIV0, ERR_REF, ERR_NAME, ERR_NA, ERR_NUM, ERR_NULL, "#CIRCULAR!"}


def is_error(v: Any) -> bool:
    return isinstance(v, str) and v in ALL_ERRORS


def is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def to_number(v: Any) -> float | str:
    """Convert value to number, return error string on failure."""
    if is_error(v):
        return v
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return ERR_VALUE
    if v is None:
        return 0.0
    return ERR_VALUE


def to_string(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


def flatten(args: list[Any]) -> list[Any]:
    """Flatten nested lists from range expansions."""
    result = []
    for a in args:
        if isinstance(a, list):
            result.extend(flatten(a))
        else:
            result.append(a)
    return result


def flat_numbers(args: list[Any]) -> list[float]:
    """Flatten args and extract numeric values only (skip None, str, bool)."""
    result = []
    for v in flatten(args):
        if is_error(v):
            continue
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            result.append(float(v))
    return result


def flat_numbers_coerce(args: list[Any]) -> list[float]:
    """Like flat_numbers but coerce booleans and numeric strings."""
    result = []
    for v in flatten(args):
        if is_error(v):
            continue
        n = to_number(v)
        if is_number(n):
            result.append(float(n))
    return result


# ── Math Functions ──

def fn_sum(args: list[Any]) -> float | str:
    nums = flat_numbers(args)
    return sum(nums)

def fn_average(args: list[Any]) -> float | str:
    nums = flat_numbers(args)
    if not nums:
        return ERR_DIV0
    return sum(nums) / len(nums)

def fn_count(args: list[Any]) -> int:
    return len(flat_numbers(args))

def fn_counta(args: list[Any]) -> int:
    return len([v for v in flatten(args) if v is not None and v != ""])

def fn_min(args: list[Any]) -> float | str:
    nums = flat_numbers(args)
    return min(nums) if nums else 0.0

def fn_max(args: list[Any]) -> float | str:
    nums = flat_numbers(args)
    return max(nums) if nums else 0.0

def fn_round(args: list[Any]) -> float | str:
    if len(args) < 1:
        return ERR_VALUE
    n = to_number(args[0])
    if is_error(n):
        return n
    digits = int(to_number(args[1])) if len(args) > 1 else 0
    return round(float(n), digits)

def fn_roundup(args: list[Any]) -> float | str:
    if len(args) < 1:
        return ERR_VALUE
    n = to_number(args[0])
    if is_error(n):
        return n
    digits = int(to_number(args[1])) if len(args) > 1 else 0
    factor = 10 ** digits
    return math.ceil(float(n) * factor) / factor

def fn_rounddown(args: list[Any]) -> float | str:
    if len(args) < 1:
        return ERR_VALUE
    n = to_number(args[0])
    if is_error(n):
        return n
    digits = int(to_number(args[1])) if len(args) > 1 else 0
    factor = 10 ** digits
    return math.floor(float(n) * factor) / factor

def fn_abs(args: list[Any]) -> float | str:
    n = to_number(args[0]) if args else ERR_VALUE
    return abs(float(n)) if is_number(n) else n

def fn_sqrt(args: list[Any]) -> float | str:
    n = to_number(args[0]) if args else ERR_VALUE
    if is_error(n):
        return n
    if float(n) < 0:
        return ERR_NUM
    return math.sqrt(float(n))

def fn_power(args: list[Any]) -> float | str:
    if len(args) < 2:
        return ERR_VALUE
    base = to_number(args[0])
    exp = to_number(args[1])
    if is_error(base):
        return base
    if is_error(exp):
        return exp
    try:
        return math.pow(float(base), float(exp))
    except (OverflowError, ValueError):
        return ERR_NUM

def fn_mod(args: list[Any]) -> float | str:
    if len(args) < 2:
        return ERR_VALUE
    n = to_number(args[0])
    d = to_number(args[1])
    if is_error(n):
        return n
    if is_error(d):
        return d
    if float(d) == 0:
        return ERR_DIV0
    return float(n) % float(d)

def fn_int(args: list[Any]) -> float | str:
    n = to_number(args[0]) if args else ERR_VALUE
    return float(math.floor(float(n))) if is_number(n) else n

def fn_ceiling(args: list[Any]) -> float | str:
    if len(args) < 2:
        return ERR_VALUE
    n = to_number(args[0])
    sig = to_number(args[1])
    if is_error(n) or is_error(sig):
        return ERR_VALUE
    if float(sig) == 0:
        return 0.0
    return math.ceil(float(n) / float(sig)) * float(sig)

def fn_floor(args: list[Any]) -> float | str:
    if len(args) < 2:
        return ERR_VALUE
    n = to_number(args[0])
    sig = to_number(args[1])
    if is_error(n) or is_error(sig):
        return ERR_VALUE
    if float(sig) == 0:
        return 0.0
    return math.floor(float(n) / float(sig)) * float(sig)

def fn_rand(args: list[Any]) -> float:
    import random
    return random.random()

def fn_randbetween(args: list[Any]) -> float | str:
    import random
    if len(args) < 2:
        return ERR_VALUE
    lo = to_number(args[0])
    hi = to_number(args[1])
    if is_error(lo) or is_error(hi):
        return ERR_VALUE
    return float(random.randint(int(lo), int(hi)))

def fn_pi(args: list[Any]) -> float:
    return math.pi

def fn_log(args: list[Any]) -> float | str:
    if not args:
        return ERR_VALUE
    n = to_number(args[0])
    if is_error(n):
        return n
    base = to_number(args[1]) if len(args) > 1 else 10.0
    if is_error(base):
        return base
    if float(n) <= 0 or float(base) <= 0 or float(base) == 1:
        return ERR_NUM
    return math.log(float(n), float(base))

def fn_ln(args: list[Any]) -> float | str:
    n = to_number(args[0]) if args else ERR_VALUE
    if is_error(n):
        return n
    if float(n) <= 0:
        return ERR_NUM
    return math.log(float(n))

def fn_exp(args: list[Any]) -> float | str:
    n = to_number(args[0]) if args else ERR_VALUE
    if is_error(n):
        return n
    try:
        return math.exp(float(n))
    except OverflowError:
        return ERR_NUM


# ── Text Functions ──

def fn_concatenate(args: list[Any]) -> str:
    return "".join(to_string(v) for v in flatten(args))

def fn_concat(args: list[Any]) -> str:
    return fn_concatenate(args)

def fn_left(args: list[Any]) -> str | str:
    if not args:
        return ERR_VALUE
    text = to_string(args[0])
    n = int(to_number(args[1])) if len(args) > 1 else 1
    return text[:n]

def fn_right(args: list[Any]) -> str | str:
    if not args:
        return ERR_VALUE
    text = to_string(args[0])
    n = int(to_number(args[1])) if len(args) > 1 else 1
    return text[-n:] if n > 0 else ""

def fn_mid(args: list[Any]) -> str | str:
    if len(args) < 3:
        return ERR_VALUE
    text = to_string(args[0])
    start = int(to_number(args[1]))
    length = int(to_number(args[2]))
    return text[start - 1: start - 1 + length]

def fn_len(args: list[Any]) -> int | str:
    if not args:
        return ERR_VALUE
    return len(to_string(args[0]))

def fn_trim(args: list[Any]) -> str:
    if not args:
        return ERR_VALUE
    return " ".join(to_string(args[0]).split())

def fn_upper(args: list[Any]) -> str:
    return to_string(args[0]).upper() if args else ERR_VALUE

def fn_lower(args: list[Any]) -> str:
    return to_string(args[0]).lower() if args else ERR_VALUE

def fn_proper(args: list[Any]) -> str:
    return to_string(args[0]).title() if args else ERR_VALUE

def fn_find(args: list[Any]) -> int | str:
    """Case-sensitive find. Returns 1-based position."""
    if len(args) < 2:
        return ERR_VALUE
    needle = to_string(args[0])
    haystack = to_string(args[1])
    start = int(to_number(args[2])) - 1 if len(args) > 2 else 0
    pos = haystack.find(needle, start)
    return pos + 1 if pos >= 0 else ERR_VALUE

def fn_search(args: list[Any]) -> int | str:
    """Case-insensitive find. Returns 1-based position."""
    if len(args) < 2:
        return ERR_VALUE
    needle = to_string(args[0]).lower()
    haystack = to_string(args[1]).lower()
    start = int(to_number(args[2])) - 1 if len(args) > 2 else 0
    pos = haystack.find(needle, start)
    return pos + 1 if pos >= 0 else ERR_VALUE

def fn_substitute(args: list[Any]) -> str | str:
    if len(args) < 3:
        return ERR_VALUE
    text = to_string(args[0])
    old = to_string(args[1])
    new = to_string(args[2])
    if len(args) > 3:
        n = int(to_number(args[3]))
        count = 0
        result = ""
        i = 0
        while i < len(text):
            pos = text.find(old, i)
            if pos < 0:
                result += text[i:]
                break
            count += 1
            result += text[i:pos]
            if count == n:
                result += new
            else:
                result += old
            i = pos + len(old)
        return result
    return text.replace(old, new)

def fn_replace(args: list[Any]) -> str | str:
    if len(args) < 4:
        return ERR_VALUE
    text = to_string(args[0])
    start = int(to_number(args[1])) - 1
    length = int(to_number(args[2]))
    new_text = to_string(args[3])
    return text[:start] + new_text + text[start + length:]

def fn_text(args: list[Any]) -> str:
    if len(args) < 2:
        return ERR_VALUE
    value = to_number(args[0])
    fmt = to_string(args[1])
    if is_error(value):
        return str(value)
    # Basic format handling
    if "%" in fmt:
        decimals = fmt.count("0") - 1 if "." in fmt else 0
        return f"{float(value) * 100:.{max(0, decimals)}f}%"
    if "." in fmt:
        decimals = len(fmt.split(".")[1].replace("#", "0"))
        return f"{float(value):.{decimals}f}"
    return str(int(float(value)))

def fn_value(args: list[Any]) -> float | str:
    if not args:
        return ERR_VALUE
    return to_number(args[0])

def fn_char(args: list[Any]) -> str | str:
    n = to_number(args[0]) if args else ERR_VALUE
    if is_error(n):
        return n
    return chr(int(float(n)))

def fn_code(args: list[Any]) -> int | str:
    if not args:
        return ERR_VALUE
    text = to_string(args[0])
    return ord(text[0]) if text else ERR_VALUE

def fn_rept(args: list[Any]) -> str | str:
    if len(args) < 2:
        return ERR_VALUE
    return to_string(args[0]) * int(to_number(args[1]))


# ── Logic Functions ──

def fn_if(args: list[Any]) -> Any:
    if len(args) < 2:
        return ERR_VALUE
    cond = args[0]
    if is_error(cond):
        return cond
    true_val = args[1] if len(args) > 1 else True
    false_val = args[2] if len(args) > 2 else False
    return true_val if cond else false_val

def fn_and(args: list[Any]) -> bool | str:
    vals = flatten(args)
    if not vals:
        return ERR_VALUE
    for v in vals:
        if is_error(v):
            return v
        if not v:
            return False
    return True

def fn_or(args: list[Any]) -> bool | str:
    vals = flatten(args)
    if not vals:
        return ERR_VALUE
    for v in vals:
        if is_error(v):
            return v
        if v:
            return True
    return False

def fn_not(args: list[Any]) -> bool | str:
    if not args:
        return ERR_VALUE
    v = args[0]
    if is_error(v):
        return v
    return not v

def fn_iferror(args: list[Any]) -> Any:
    if len(args) < 2:
        return ERR_VALUE
    return args[1] if is_error(args[0]) else args[0]

def fn_ifna(args: list[Any]) -> Any:
    if len(args) < 2:
        return ERR_VALUE
    return args[1] if args[0] == ERR_NA else args[0]

def fn_ifs(args: list[Any]) -> Any:
    """IFS(cond1, val1, cond2, val2, ...)"""
    for i in range(0, len(args) - 1, 2):
        if args[i]:
            return args[i + 1]
    return ERR_NA

def fn_switch(args: list[Any]) -> Any:
    """SWITCH(expr, match1, val1, match2, val2, ..., [default])"""
    if len(args) < 3:
        return ERR_VALUE
    expr = args[0]
    for i in range(1, len(args) - 1, 2):
        if expr == args[i]:
            return args[i + 1]
    # Odd number of remaining args means last is default
    if len(args) % 2 == 0:
        return args[-1]
    return ERR_NA

def fn_true(args: list[Any]) -> bool:
    return True

def fn_false(args: list[Any]) -> bool:
    return False


# ── Lookup Functions ──

def fn_vlookup(args: list[Any]) -> Any:
    """VLOOKUP(lookup_value, table_range, col_index, [range_lookup])"""
    if len(args) < 3:
        return ERR_VALUE
    lookup = args[0]
    table = args[1]  # should be a 2D list
    col_idx = int(to_number(args[2]))
    approx = args[3] if len(args) > 3 else True

    if not isinstance(table, list) or not table:
        return ERR_REF

    # table is a flat list from range; we need to reconstruct rows
    # Convention: table is list of rows, each row is a list
    rows = table if isinstance(table[0], list) else [table]

    if col_idx < 1 or (rows and col_idx > len(rows[0])):
        return ERR_REF

    for row in rows:
        if len(row) >= col_idx and row[0] == lookup:
            return row[col_idx - 1]

    if approx and rows:
        # Approximate match: find largest value <= lookup
        best = None
        for row in rows:
            if len(row) >= col_idx:
                val = row[0]
                if is_number(val) and is_number(lookup):
                    if float(val) <= float(lookup):
                        if best is None or float(val) > float(best[0]):
                            best = row
        if best:
            return best[col_idx - 1]

    return ERR_NA

def fn_hlookup(args: list[Any]) -> Any:
    """HLOOKUP(lookup_value, table_range, row_index, [range_lookup])"""
    if len(args) < 3:
        return ERR_VALUE
    lookup = args[0]
    table = args[1]
    row_idx = int(to_number(args[2]))

    if not isinstance(table, list) or not table:
        return ERR_REF

    rows = table if isinstance(table[0], list) else [table]
    if row_idx < 1 or row_idx > len(rows):
        return ERR_REF

    # Search first row
    for c in range(len(rows[0])):
        if rows[0][c] == lookup:
            return rows[row_idx - 1][c] if c < len(rows[row_idx - 1]) else ERR_REF
    return ERR_NA

def fn_index(args: list[Any]) -> Any:
    """INDEX(range, row_num, [col_num])"""
    if len(args) < 2:
        return ERR_VALUE
    data = args[0]
    row_num = int(to_number(args[1]))
    col_num = int(to_number(args[2])) if len(args) > 2 else 1

    if not isinstance(data, list):
        return ERR_REF

    rows = data if isinstance(data[0], list) else [data]
    if row_num < 1 or row_num > len(rows):
        return ERR_REF
    row = rows[row_num - 1]
    if col_num < 1 or col_num > len(row):
        return ERR_REF
    return row[col_num - 1]

def fn_match(args: list[Any]) -> int | str:
    """MATCH(lookup_value, lookup_range, [match_type])"""
    if len(args) < 2:
        return ERR_VALUE
    lookup = args[0]
    data = flatten(args[1]) if isinstance(args[1], list) else [args[1]]
    match_type = int(to_number(args[2])) if len(args) > 2 else 1

    if match_type == 0:
        # Exact match
        for i, v in enumerate(data):
            if v == lookup:
                return i + 1
        return ERR_NA
    elif match_type == 1:
        # Largest <= lookup
        best_idx = None
        for i, v in enumerate(data):
            if is_number(v) and is_number(lookup) and float(v) <= float(lookup):
                best_idx = i
        return best_idx + 1 if best_idx is not None else ERR_NA
    else:
        # Smallest >= lookup
        best_idx = None
        for i, v in enumerate(data):
            if is_number(v) and is_number(lookup) and float(v) >= float(lookup):
                if best_idx is None or float(v) < float(data[best_idx]):
                    best_idx = i
        return best_idx + 1 if best_idx is not None else ERR_NA

def fn_xlookup(args: list[Any]) -> Any:
    """XLOOKUP(lookup, lookup_array, return_array, [if_not_found], [match_mode])"""
    if len(args) < 3:
        return ERR_VALUE
    lookup = args[0]
    lookup_arr = flatten(args[1]) if isinstance(args[1], list) else [args[1]]
    return_arr = flatten(args[2]) if isinstance(args[2], list) else [args[2]]
    not_found = args[3] if len(args) > 3 else ERR_NA

    for i, v in enumerate(lookup_arr):
        if v == lookup:
            return return_arr[i] if i < len(return_arr) else ERR_REF
    return not_found


# ── Statistical Functions ──

def fn_countif(args: list[Any]) -> int:
    if len(args) < 2:
        return 0
    data = flatten(args[0]) if isinstance(args[0], list) else [args[0]]
    criteria = args[1]
    return sum(1 for v in data if _matches_criteria(v, criteria))

def fn_countifs(args: list[Any]) -> int:
    """COUNTIFS(range1, criteria1, range2, criteria2, ...)"""
    if len(args) < 2 or len(args) % 2 != 0:
        return 0
    ranges = [flatten(args[i]) if isinstance(args[i], list) else [args[i]] for i in range(0, len(args), 2)]
    criteria = [args[i] for i in range(1, len(args), 2)]
    length = min(len(r) for r in ranges) if ranges else 0
    count = 0
    for i in range(length):
        if all(_matches_criteria(ranges[j][i], criteria[j]) for j in range(len(ranges))):
            count += 1
    return count

def fn_sumif(args: list[Any]) -> float:
    if len(args) < 2:
        return 0.0
    data = flatten(args[0]) if isinstance(args[0], list) else [args[0]]
    criteria = args[1]
    sum_range = flatten(args[2]) if len(args) > 2 and isinstance(args[2], list) else data
    total = 0.0
    for i, v in enumerate(data):
        if _matches_criteria(v, criteria):
            sv = sum_range[i] if i < len(sum_range) else 0
            n = to_number(sv)
            if is_number(n):
                total += float(n)
    return total

def fn_sumifs(args: list[Any]) -> float:
    """SUMIFS(sum_range, range1, criteria1, ...)"""
    if len(args) < 3 or len(args) % 2 != 1:
        return 0.0
    sum_range = flatten(args[0]) if isinstance(args[0], list) else [args[0]]
    ranges = [flatten(args[i]) if isinstance(args[i], list) else [args[i]] for i in range(1, len(args), 2)]
    criteria = [args[i] for i in range(2, len(args), 2)]
    total = 0.0
    length = len(sum_range)
    for i in range(length):
        if all(i < len(ranges[j]) and _matches_criteria(ranges[j][i], criteria[j]) for j in range(len(ranges))):
            n = to_number(sum_range[i])
            if is_number(n):
                total += float(n)
    return total

def fn_averageif(args: list[Any]) -> float | str:
    if len(args) < 2:
        return ERR_VALUE
    data = flatten(args[0]) if isinstance(args[0], list) else [args[0]]
    criteria = args[1]
    avg_range = flatten(args[2]) if len(args) > 2 and isinstance(args[2], list) else data
    values = []
    for i, v in enumerate(data):
        if _matches_criteria(v, criteria):
            sv = avg_range[i] if i < len(avg_range) else 0
            n = to_number(sv)
            if is_number(n):
                values.append(float(n))
    return sum(values) / len(values) if values else ERR_DIV0

def fn_averageifs(args: list[Any]) -> float | str:
    if len(args) < 3 or len(args) % 2 != 1:
        return ERR_VALUE
    avg_range = flatten(args[0]) if isinstance(args[0], list) else [args[0]]
    ranges = [flatten(args[i]) if isinstance(args[i], list) else [args[i]] for i in range(1, len(args), 2)]
    criteria = [args[i] for i in range(2, len(args), 2)]
    values = []
    for i in range(len(avg_range)):
        if all(i < len(ranges[j]) and _matches_criteria(ranges[j][i], criteria[j]) for j in range(len(ranges))):
            n = to_number(avg_range[i])
            if is_number(n):
                values.append(float(n))
    return sum(values) / len(values) if values else ERR_DIV0

def fn_median(args: list[Any]) -> float | str:
    nums = flat_numbers(args)
    if not nums:
        return ERR_NUM
    return float(statistics.median(nums))

def fn_mode(args: list[Any]) -> float | str:
    nums = flat_numbers(args)
    if not nums:
        return ERR_NA
    try:
        return float(statistics.mode(nums))
    except statistics.StatisticsError:
        return ERR_NA

def fn_stdev(args: list[Any]) -> float | str:
    nums = flat_numbers(args)
    if len(nums) < 2:
        return ERR_DIV0
    return statistics.stdev(nums)

def fn_var(args: list[Any]) -> float | str:
    nums = flat_numbers(args)
    if len(nums) < 2:
        return ERR_DIV0
    return statistics.variance(nums)

def fn_large(args: list[Any]) -> float | str:
    if len(args) < 2:
        return ERR_VALUE
    nums = flat_numbers([args[0]]) if isinstance(args[0], list) else flat_numbers(args[:1])
    k = int(to_number(args[1]))
    nums.sort(reverse=True)
    if k < 1 or k > len(nums):
        return ERR_NUM
    return nums[k - 1]

def fn_small(args: list[Any]) -> float | str:
    if len(args) < 2:
        return ERR_VALUE
    nums = flat_numbers([args[0]]) if isinstance(args[0], list) else flat_numbers(args[:1])
    k = int(to_number(args[1]))
    nums.sort()
    if k < 1 or k > len(nums):
        return ERR_NUM
    return nums[k - 1]

def fn_rank(args: list[Any]) -> int | str:
    if len(args) < 2:
        return ERR_VALUE
    value = to_number(args[0])
    if is_error(value):
        return value
    nums = flat_numbers([args[1]]) if isinstance(args[1], list) else flat_numbers(args[1:2])
    order = int(to_number(args[2])) if len(args) > 2 else 0  # 0=desc, 1=asc
    if float(value) not in nums:
        return ERR_NA
    if order:
        nums.sort()
    else:
        nums.sort(reverse=True)
    return nums.index(float(value)) + 1


# ── Date Functions ──

def fn_today(args: list[Any]) -> date:
    return date.today()

def fn_now(args: list[Any]) -> datetime:
    return datetime.now()

def fn_date(args: list[Any]) -> date | str:
    if len(args) < 3:
        return ERR_VALUE
    try:
        y = int(to_number(args[0]))
        m = int(to_number(args[1]))
        d = int(to_number(args[2]))
        return date(y, m, d)
    except (ValueError, OverflowError):
        return ERR_VALUE

def fn_year(args: list[Any]) -> int | str:
    v = args[0] if args else None
    if isinstance(v, (date, datetime)):
        return v.year
    return ERR_VALUE

def fn_month(args: list[Any]) -> int | str:
    v = args[0] if args else None
    if isinstance(v, (date, datetime)):
        return v.month
    return ERR_VALUE

def fn_day(args: list[Any]) -> int | str:
    v = args[0] if args else None
    if isinstance(v, (date, datetime)):
        return v.day
    return ERR_VALUE

def fn_hour(args: list[Any]) -> int | str:
    v = args[0] if args else None
    if isinstance(v, datetime):
        return v.hour
    return 0 if isinstance(v, date) else ERR_VALUE

def fn_minute(args: list[Any]) -> int | str:
    v = args[0] if args else None
    if isinstance(v, datetime):
        return v.minute
    return 0 if isinstance(v, date) else ERR_VALUE

def fn_second(args: list[Any]) -> int | str:
    v = args[0] if args else None
    if isinstance(v, datetime):
        return v.second
    return 0 if isinstance(v, date) else ERR_VALUE

def fn_datevalue(args: list[Any]) -> date | str:
    if not args:
        return ERR_VALUE
    text = to_string(args[0])
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return ERR_VALUE

def fn_datedif(args: list[Any]) -> int | str:
    if len(args) < 3:
        return ERR_VALUE
    d1 = args[0]
    d2 = args[1]
    unit = to_string(args[2]).upper()
    if not isinstance(d1, (date, datetime)) or not isinstance(d2, (date, datetime)):
        return ERR_VALUE
    if isinstance(d1, datetime):
        d1 = d1.date()
    if isinstance(d2, datetime):
        d2 = d2.date()
    if unit == "D":
        return (d2 - d1).days
    if unit == "M":
        return (d2.year - d1.year) * 12 + (d2.month - d1.month)
    if unit == "Y":
        return d2.year - d1.year
    return ERR_VALUE

def fn_weekday(args: list[Any]) -> int | str:
    v = args[0] if args else None
    if isinstance(v, (date, datetime)):
        return v.isoweekday()  # Mon=1 ... Sun=7
    return ERR_VALUE

def fn_weeknum(args: list[Any]) -> int | str:
    v = args[0] if args else None
    if isinstance(v, (date, datetime)):
        return v.isocalendar()[1]
    return ERR_VALUE

def fn_edate(args: list[Any]) -> date | str:
    if len(args) < 2:
        return ERR_VALUE
    d = args[0]
    if not isinstance(d, (date, datetime)):
        return ERR_VALUE
    if isinstance(d, datetime):
        d = d.date()
    months = int(to_number(args[1]))
    new_month = d.month + months
    new_year = d.year + (new_month - 1) // 12
    new_month = (new_month - 1) % 12 + 1
    import calendar
    max_day = calendar.monthrange(new_year, new_month)[1]
    return date(new_year, new_month, min(d.day, max_day))

def fn_eomonth(args: list[Any]) -> date | str:
    if len(args) < 2:
        return ERR_VALUE
    d = args[0]
    if not isinstance(d, (date, datetime)):
        return ERR_VALUE
    if isinstance(d, datetime):
        d = d.date()
    months = int(to_number(args[1]))
    new_month = d.month + months
    new_year = d.year + (new_month - 1) // 12
    new_month = (new_month - 1) % 12 + 1
    import calendar
    max_day = calendar.monthrange(new_year, new_month)[1]
    return date(new_year, new_month, max_day)


# ── Info Functions ──

def fn_isblank(args: list[Any]) -> bool:
    return args[0] is None or args[0] == "" if args else True

def fn_isnumber(args: list[Any]) -> bool:
    return is_number(args[0]) if args else False

def fn_istext(args: list[Any]) -> bool:
    return isinstance(args[0], str) and not is_error(args[0]) if args else False

def fn_iserror(args: list[Any]) -> bool:
    return is_error(args[0]) if args else False

def fn_isna(args: list[Any]) -> bool:
    return args[0] == ERR_NA if args else False

def fn_type(args: list[Any]) -> int:
    v = args[0] if args else None
    if is_number(v):
        return 1
    if isinstance(v, str):
        return 2 if not is_error(v) else 16
    if isinstance(v, bool):
        return 4
    return 0

def fn_n(args: list[Any]) -> float:
    v = args[0] if args else None
    n = to_number(v)
    return float(n) if is_number(n) else 0.0


# ── Criteria matching helper ──

_CRITERIA_RE = re.compile(r"^([<>=!]+)(.+)$")

def _matches_criteria(value: Any, criteria: Any) -> bool:
    """Match a value against a criteria (like COUNTIF/SUMIF criteria)."""
    if not isinstance(criteria, str):
        return value == criteria

    m = _CRITERIA_RE.match(criteria)
    if m:
        op = m.group(1)
        crit_val_str = m.group(2)
        try:
            crit_val: float | str = float(crit_val_str)
        except ValueError:
            crit_val = crit_val_str

        v = to_number(value) if is_number(crit_val) else to_string(value)
        if is_error(v):
            return False

        if op == "=":
            return v == crit_val
        if op == "<>":
            return v != crit_val
        if op == "<":
            return v < crit_val  # type: ignore
        if op == ">":
            return v > crit_val  # type: ignore
        if op == "<=":
            return v <= crit_val  # type: ignore
        if op == ">=":
            return v >= crit_val  # type: ignore
    # Plain value comparison
    try:
        return float(value) == float(criteria)
    except (ValueError, TypeError):
        return to_string(value).lower() == criteria.lower()


# ── Registry ──

FUNCTIONS: dict[str, Callable[[list[Any]], Any]] = {
    # Math
    "SUM": fn_sum, "AVERAGE": fn_average, "COUNT": fn_count, "COUNTA": fn_counta,
    "MIN": fn_min, "MAX": fn_max, "ROUND": fn_round, "ROUNDUP": fn_roundup,
    "ROUNDDOWN": fn_rounddown, "ABS": fn_abs, "SQRT": fn_sqrt, "POWER": fn_power,
    "MOD": fn_mod, "INT": fn_int, "CEILING": fn_ceiling, "FLOOR": fn_floor,
    "RAND": fn_rand, "RANDBETWEEN": fn_randbetween, "PI": fn_pi,
    "LOG": fn_log, "LN": fn_ln, "EXP": fn_exp,
    # Text
    "CONCATENATE": fn_concatenate, "CONCAT": fn_concat, "LEFT": fn_left,
    "RIGHT": fn_right, "MID": fn_mid, "LEN": fn_len, "TRIM": fn_trim,
    "UPPER": fn_upper, "LOWER": fn_lower, "PROPER": fn_proper,
    "FIND": fn_find, "SEARCH": fn_search, "SUBSTITUTE": fn_substitute,
    "REPLACE": fn_replace, "TEXT": fn_text, "VALUE": fn_value,
    "CHAR": fn_char, "CODE": fn_code, "REPT": fn_rept,
    # Logic
    "IF": fn_if, "AND": fn_and, "OR": fn_or, "NOT": fn_not,
    "IFERROR": fn_iferror, "IFNA": fn_ifna, "IFS": fn_ifs, "SWITCH": fn_switch,
    "TRUE": fn_true, "FALSE": fn_false,
    # Lookup
    "VLOOKUP": fn_vlookup, "HLOOKUP": fn_hlookup, "INDEX": fn_index,
    "MATCH": fn_match, "XLOOKUP": fn_xlookup,
    # Statistical
    "COUNTIF": fn_countif, "COUNTIFS": fn_countifs, "SUMIF": fn_sumif,
    "SUMIFS": fn_sumifs, "AVERAGEIF": fn_averageif, "AVERAGEIFS": fn_averageifs,
    "MEDIAN": fn_median, "MODE": fn_mode, "STDEV": fn_stdev, "VAR": fn_var,
    "LARGE": fn_large, "SMALL": fn_small, "RANK": fn_rank,
    # Date
    "TODAY": fn_today, "NOW": fn_now, "DATE": fn_date, "YEAR": fn_year,
    "MONTH": fn_month, "DAY": fn_day, "HOUR": fn_hour, "MINUTE": fn_minute,
    "SECOND": fn_second, "DATEVALUE": fn_datevalue, "DATEDIF": fn_datedif,
    "WEEKDAY": fn_weekday, "WEEKNUM": fn_weeknum, "EDATE": fn_edate, "EOMONTH": fn_eomonth,
    # Info
    "ISBLANK": fn_isblank, "ISNUMBER": fn_isnumber, "ISTEXT": fn_istext,
    "ISERROR": fn_iserror, "ISNA": fn_isna, "TYPE": fn_type, "N": fn_n,
}
