import pytest
from utils import get_trend
from utils.patterns import check_pattern_for_short, check_pattern_for_long, check_high_above_ind, check_low_below_ind


def test_test():
    assert 1 == 1


data_get_trend = [
    (2.0, 1.0, 'Up'),
    (1.0, 2.0, 'Down'),
    (2.0, 2.0, 'Not'),
]


@pytest.mark.parametrize("price,indicator,expected", data_get_trend)
def test_check_trend(price, indicator, expected):
    """Проверяет правильность определения тренда."""
    assert get_trend(price, indicator) == expected


data_long_pattern = [
    ((10, 12, 11, 10, 9, 14, 8, 15), 14),
    ((10, 9, 11, 10, 12, 9, 8, 15), 12),
    ((10, 12, 11, 10, 9, 11, 8, 11), None),
    ((10, 12, 11, 10, 9, 1, 8, 1), None),
]


@pytest.mark.parametrize("data,expected", data_long_pattern)
def test_check_pattern_for_long(data, expected):
    assert check_pattern_for_long(data) == expected


data_short_patterns = [
    ((10, 9, 11, 10, 8, 14, 5, 15), 8),
    ((10, 9, 11, 9, 9, 9, 9, 7), 7),
    ((10, 9, 11, 10, 22, 11, 18, 11), None),
    ((10, 9, 11, 9, 9, 9, 9, 9), None),
]


@pytest.mark.parametrize("data,expected", data_short_patterns)
def test_check_pattern_for_short(data, expected):
    assert check_pattern_for_short(data) == expected


data_check_high_above_ind = [
    ((1, 3, 3), (1, 2, 3), True),
    ((1, 2, 3), (1, 2, 3), False),
]


@pytest.mark.parametrize("high_bars_list,indicator_list,expected", data_check_high_above_ind)
def test_check_high_above_ind(high_bars_list, indicator_list, expected):
    assert check_high_above_ind(high_bars_list, indicator_list) == expected


data_check_low_below_ind = [
    ((1, 1, 3), (1, 2, 3), True),
    ((1, 2, 3), (1, 2, 3), False),
]


@pytest.mark.parametrize("low_bars_list,indicator_list,expected", data_check_low_below_ind)
def test_check_low_below_ind(low_bars_list, indicator_list, expected):
    assert check_low_below_ind(low_bars_list, indicator_list) == expected
