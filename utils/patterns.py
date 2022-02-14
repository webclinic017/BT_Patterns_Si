from loguru import logger


def check_pattern_for_long(data: list) -> float | None:
    """Паттерн два максимума. BW line balance.

    Находит второй максимум бара от базового.

    Returns:
        price [float]: второй максимум бара.
        None: Если условие не выполнено в заданном диапазоне.
    """
    price = data[0]
    count = 0
    for i in range(len(data)):
        if data[i] > price:
            price = data[i]
            count += 1
            if count == 2:
                logger.debug(f'i[{i}], pattern: {price:.3f}')
                return price
    return None


def check_pattern_for_short(data: list) -> float | None:
    """Паттерн два минимума. BW line balance.

    Находит второй минимум бара от базового.

    Returns:
        price [float]: второй минимум бара.
        None: Если условие не выполнено в заданном диапазоне.
    """
    price = data[0]
    count = 0
    for i in range(len(data)):
        if data[i] < price:
            price = data[i]
            count += 1
            if count == 2:
                logger.debug(f'i[{i}], pattern: {price:.3f}')
                return price
    return None


def check_high_above_ind(high_bars_list: list, indicator_list: list) -> bool:
    """Проверяет что максимум бара был выше индикатора.

    Args:
        high_bars_list (list): Список максимумов за период
        indicator_list (list): Список значений индикатора

    Returns:
        Bool
    """
    for i in range(len(high_bars_list)):
        if high_bars_list[i] > indicator_list[i]:
            return True
    return False


def check_low_below_ind(low_bars_list: list, indicator_list: list) -> bool:
    """Проверяет что минимум бара был ниже индикатора.

    Args:
        low_bars_list (list): Список минимумов за период
        indicator_list (list): Список значений индикатора

    Returns:
        Bool
    """
    for i in range(len(low_bars_list)):
        if low_bars_list[i] < indicator_list[i]:
            return True
    return False
