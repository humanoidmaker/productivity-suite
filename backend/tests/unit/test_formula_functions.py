"""Tests for built-in spreadsheet functions."""
import pytest
from datetime import date, datetime
from app.formulas.functions import *


class TestMathFunctions:
    def test_sum_numbers(self):
        assert fn_sum([[1, 2, 3, 4, 5]]) == 15.0

    def test_sum_mixed(self):
        # Skips text and None
        assert fn_sum([[1, "text", None, 3]]) == 4.0

    def test_average(self):
        assert fn_average([[10, 20, 30]]) == 20.0

    def test_average_empty(self):
        assert fn_average([[]]) == ERR_DIV0

    def test_count_numeric(self):
        assert fn_count([[1, "text", None, 3, True]]) == 2

    def test_counta_non_empty(self):
        assert fn_counta([[1, "text", None, 3]]) == 3

    def test_min(self):
        assert fn_min([[5, 2, 8, 1]]) == 1.0

    def test_max(self):
        assert fn_max([[5, 2, 8, 1]]) == 8.0

    def test_round(self):
        assert fn_round([3.14159, 2]) == 3.14

    def test_roundup(self):
        assert fn_roundup([3.141, 2]) == 3.15

    def test_rounddown(self):
        assert fn_rounddown([3.149, 2]) == 3.14

    def test_abs(self):
        assert fn_abs([-5]) == 5.0

    def test_sqrt(self):
        assert fn_sqrt([9]) == 3.0

    def test_sqrt_negative(self):
        assert fn_sqrt([-1]) == ERR_NUM

    def test_power(self):
        assert fn_power([2, 10]) == 1024.0

    def test_mod(self):
        assert fn_mod([10, 3]) == 1.0

    def test_mod_zero(self):
        assert fn_mod([10, 0]) == ERR_DIV0

    def test_int(self):
        assert fn_int([3.9]) == 3.0

    def test_pi(self):
        import math
        assert fn_pi([]) == math.pi


class TestTextFunctions:
    def test_concatenate(self):
        assert fn_concatenate(["Hello", " ", "World"]) == "Hello World"

    def test_left(self):
        assert fn_left(["Hello", 3]) == "Hel"

    def test_right(self):
        assert fn_right(["Hello", 3]) == "llo"

    def test_mid(self):
        assert fn_mid(["Hello World", 7, 5]) == "World"

    def test_len(self):
        assert fn_len(["Hello"]) == 5

    def test_trim(self):
        assert fn_trim(["  hello   world  "]) == "hello world"

    def test_upper(self):
        assert fn_upper(["hello"]) == "HELLO"

    def test_lower(self):
        assert fn_lower(["HELLO"]) == "hello"

    def test_proper(self):
        assert fn_proper(["hello world"]) == "Hello World"

    def test_find_case_sensitive(self):
        assert fn_find(["World", "Hello World"]) == 7

    def test_find_not_found(self):
        assert fn_find(["xyz", "Hello"]) == ERR_VALUE

    def test_search_case_insensitive(self):
        assert fn_search(["world", "Hello World"]) == 7

    def test_substitute(self):
        assert fn_substitute(["Hello World", "World", "Python"]) == "Hello Python"

    def test_rept(self):
        assert fn_rept(["ab", 3]) == "ababab"


class TestLogicFunctions:
    def test_if_true(self):
        assert fn_if([True, "yes", "no"]) == "yes"

    def test_if_false(self):
        assert fn_if([False, "yes", "no"]) == "no"

    def test_and_all_true(self):
        assert fn_and([True, True, True]) is True

    def test_and_one_false(self):
        assert fn_and([True, False, True]) is False

    def test_or_one_true(self):
        assert fn_or([False, True, False]) is True

    def test_or_all_false(self):
        assert fn_or([False, False]) is False

    def test_not(self):
        assert fn_not([True]) is False

    def test_iferror_no_error(self):
        assert fn_iferror([42, 0]) == 42

    def test_iferror_with_error(self):
        assert fn_iferror([ERR_DIV0, 0]) == 0


class TestLookupFunctions:
    def test_vlookup_exact(self):
        table = [["apple", 1], ["banana", 2], ["cherry", 3]]
        assert fn_vlookup(["banana", table, 2]) == 2

    def test_vlookup_not_found(self):
        table = [["apple", 1]]
        assert fn_vlookup(["missing", table, 2, False]) == ERR_NA

    def test_index_match(self):
        data = [[10, 20, 30]]
        assert fn_index([data, 1, 2]) == 20

    def test_match_exact(self):
        data = ["a", "b", "c", "d"]
        assert fn_match(["c", data, 0]) == 3

    def test_xlookup_found(self):
        lookup = ["a", "b", "c"]
        returns = [10, 20, 30]
        assert fn_xlookup(["b", lookup, returns]) == 20

    def test_xlookup_not_found(self):
        assert fn_xlookup(["x", ["a"], [1], "default"]) == "default"


class TestStatisticalFunctions:
    def test_countif(self):
        data = [1, 2, 3, 2, 1]
        assert fn_countif([data, 2]) == 2

    def test_countif_criteria(self):
        data = [10, 20, 30, 40]
        assert fn_countif([data, ">15"]) == 3

    def test_sumif(self):
        data = [1, 2, 3, 4]
        assert fn_sumif([data, ">2"]) == 7.0

    def test_median_odd(self):
        assert fn_median([[1, 3, 5]]) == 3.0

    def test_median_even(self):
        assert fn_median([[1, 2, 3, 4]]) == 2.5

    def test_rank(self):
        data = [10, 30, 20, 40]
        assert fn_rank([30, data, 0]) == 2  # desc: 40,30,20,10

    def test_large(self):
        data = [10, 30, 20, 40]
        assert fn_large([data, 2]) == 30.0

    def test_small(self):
        data = [10, 30, 20, 40]
        assert fn_small([data, 2]) == 20.0


class TestDateFunctions:
    def test_today(self):
        result = fn_today([])
        assert isinstance(result, date)

    def test_now(self):
        result = fn_now([])
        assert isinstance(result, datetime)

    def test_date(self):
        result = fn_date([2024, 6, 15])
        assert result == date(2024, 6, 15)

    def test_year(self):
        assert fn_year([date(2024, 6, 15)]) == 2024

    def test_month(self):
        assert fn_month([date(2024, 6, 15)]) == 6

    def test_day(self):
        assert fn_day([date(2024, 6, 15)]) == 15

    def test_datedif_days(self):
        assert fn_datedif([date(2024, 1, 1), date(2024, 1, 31), "D"]) == 30

    def test_datedif_months(self):
        assert fn_datedif([date(2024, 1, 1), date(2024, 6, 1), "M"]) == 5


class TestInfoFunctions:
    def test_isblank_none(self):
        assert fn_isblank([None]) is True

    def test_isblank_empty_str(self):
        assert fn_isblank([""]) is True

    def test_isblank_value(self):
        assert fn_isblank([1]) is False

    def test_isnumber(self):
        assert fn_isnumber([42]) is True
        assert fn_isnumber(["text"]) is False

    def test_istext(self):
        assert fn_istext(["hello"]) is True
        assert fn_istext([42]) is False

    def test_iserror(self):
        assert fn_iserror([ERR_DIV0]) is True
        assert fn_iserror([42]) is False

    def test_type_number(self):
        assert fn_type([42]) == 1

    def test_type_text(self):
        assert fn_type(["hello"]) == 2
