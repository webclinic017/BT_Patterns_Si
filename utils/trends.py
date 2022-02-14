from loguru import logger


def get_trend(fast: float, slow: float) -> str:
    """Определяет направление тренда.

    Args:
        fast (float): быстрый параметр.
        slow (float): медленный параметр.

    Returns:
       str : Направление тренда.
    """

    if fast > slow:
        logger.debug('Up trend.')
        return 'Up'
    elif fast < slow:
        logger.debug('Down trend.')
        return 'Down'
    else:
        logger.debug('Not trend.')
        return 'Not'
