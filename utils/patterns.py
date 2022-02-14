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
