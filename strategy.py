import time

import backtrader as bt
from loguru import logger

from utils import get_trend
from utils.patterns import check_pattern_for_long, check_pattern_for_short, check_high_above_ind, check_low_below_ind


class TrendStrategy(bt.Strategy):
    """Описание стратегии."""

    params = dict(
        trend_period=100,
        fast_period=10,
        slow_period=20,
    )

    def __init__(self):
        """Инициализация торговой системы"""
        # Сначала будут приходить исторические данные
        self.isLive = False

        # ===Инициализация аргументов===

        # Разные временные интервалы
        # По которому бегаем 1 мин
        self.check_datas = self.datas[0]
        # По которому работаем например 5 мин(сейчас тоже 1 мин)
        self.work_datas = self.datas[1]

        # data
        self.close = self.work_datas.close
        self.high = self.work_datas.high
        self.low = self.work_datas.low

        # indicators
        self.ma_fast = bt.ind.ExponentialMovingAverage(
            self.work_datas.close,  # type: ignore
            period=self.p.fast_period,  # type: ignore
        )

        self.ma_slow = bt.ind.ExponentialMovingAverage(
            self.work_datas.close,  # type: ignore
            period=self.p.slow_period,  # type: ignore
        )

        self.atr_ind = bt.ind.AverageTrueRange()

        # Trend значения Up/Down/Not
        self.trend = None

        # Limit orders
        self.buy_limit = None
        self.sell_limit = None

        # Stop orders
        self.buy_stop = None
        self.sell_stop = None

        # Параметры для настройки:
        # использовать Target
        self.is_target = True

        # Количество баров для паттерна (отрицательное)
        self.num_bars_pattern = -10

        # Количество баров для stop loss (отрицательное)
        self.num_bars_stoploss = -5

        # Количество баров для second if (отрицательное)
        self.num_bars_second_if = -5

        # ===Конец блока инициализации========================================

    def next(self):
        """Получение следующего исторического/нового бара"""

        if not self.isLive:  # Важно
            return

        if self.buy_limit and self.buy_limit.status == bt.Order.Submitted:
            return

        if self.sell_limit and self.sell_limit.status == bt.Order.Submitted:
            return

        if self.buy_stop and self.buy_stop.status == bt.Order.Submitted:
            return

        if self.sell_stop and self.sell_stop.status == bt.Order.Submitted:
            return

        # ===Основной блок с логикой==========================================
        # защита от множества заявок в секунду, после теста можно удалить
        # time.sleep(1)
        logger.info('<<< New next >>>')

        # Определяем тренд Up/Down/Not
        self.trend = get_trend(self.ma_fast[0], self.ma_slow[0])
        # Устанавливаем параметр ATR
        atr_for_all = self.atr_ind[0] * 1.5
        atr_for_all = round(atr_for_all, 3)

        # Определяем есть ли позиция.
        # Если позиция есть: Выставляем или пробуем улучшить стоп.
        # Если позиции нет: Проверяем паттерны на открытие позиции.
        if self.position.size > 0:
            logger.debug(f'Long position: {self.position.size}')
            # Заявки выставляем ОСО - исполнение одной отменяет другую.
            # Stop
            # При открытии позиции вблизи или чуть за slow изменим stop
            # минимум за 5 баров (?может - ATR)
            stop_price = self.get_stop_price_for_long()

            self.open_or_improve_sell_stop(stop_price)  # self.sell_stop

            # target ОСО. time.sleep после cancel stop, что бы stop и target выставлялись одновременно
            if self.is_target:
                # Выставляем заявку только если ее не было или нет(снята)
                # Будет выставляться только если self.sell_stop изменится,
                # а значит ОСО снимет self.sell_limit
                if not self.sell_limit or not self.sell_limit.alive():
                    target_price = self.buy_stop.price + atr_for_all  # type: ignore
                    target_price = round(target_price, 3)
                    self.sell_limit = self.sell(
                        exectype=bt.Order.Limit,
                        price=target_price,
                        oco=self.sell_stop,
                    )
                    logger.info(f'Target sell: {self.sell_limit.price}')  # type: ignore

        elif self.position.size < 0:
            logger.debug(f'Short position: {self.position.size}')
            # Заявки выставляем ОСО - исполнение одной отменяет другую.
            # Stop
            # При открытии позиции вблизи или чуть за slow изменим stop
            # max за 5 баров (?может + ATR)
            stop_price = self.get_stop_price_for_short()

            self.open_or_improve_buy_stop(stop_price)  # self.buy_stop

            # target ОСО. time.sleep после cancel stop, что бы stop и target выставлялись одновременно
            if self.is_target:
                # Выставляем заявку только если ее не было или нет(снята)
                # Будет выставляться только если self.buy_stop изменится,
                # а значит ОСО снимет self.buy_limit
                if not self.buy_limit or not self.buy_limit.alive():
                    target_price = self.sell_stop.price - atr_for_all  # type: ignore
                    target_price = round(target_price, 3)
                    self.buy_limit = self.buy(
                        exectype=bt.Order.Limit,
                        price=target_price,
                        oco=self.buy_stop,
                    )
                    logger.info(f'Target buy: {self.buy_limit.price}')  # type: ignore

        # Позиции нет
        else:
            logger.debug(f'Not position: {self.position.size}')

            # Список для второго условия входа(прокол индикатора)
            indicator_list = [self.ma_fast[i] for i in range(0, self.num_bars_pattern, -1)]

            if self.trend == 'Up':
                # Отменяем возможно оставшиеся заявки от 'Down'
                if self.sell_limit:
                    self.cancel(self.sell_limit)
                if self.sell_stop:
                    self.cancel(self.sell_stop)

                # Список для паттерна
                high_bars_list = [self.high[i] for i in range(0, self.num_bars_pattern, -1)]
                pattern_price = check_pattern_for_long(high_bars_list)
                # Список для стопа
                low_for_stop_list = [self.low[i] for i in range(0, self.num_bars_second_if, -1)]
                second_if = check_low_below_ind(low_for_stop_list, indicator_list)

                if pattern_price and second_if:
                    # Если соблюдены условия на вход проверим profit/loss
                    # Target должен быть больше stop loss
                    stop_price = self.get_stop_price_for_long()
                    price_stop_permission = self.check_price_stop_permission(stop_price, pattern_price, atr_for_all)
                    # Если есть permission выставляем заявку, если нет отменяем если была
                    if price_stop_permission:
                        self.open_or_improve_buy_stop(pattern_price)
                    else:
                        if self.buy_stop:
                            self.cancel(self.buy_stop)
                else:
                    logger.debug(f'pattern_price: {pattern_price}')
                    logger.debug(f'second_if: {second_if}')

            elif self.trend == 'Down':
                # Отменяем возможно оставшиеся заявки от 'Up'
                if self.buy_limit:
                    self.cancel(self.buy_limit)
                if self.buy_stop:
                    self.cancel(self.buy_stop)

                # Список для паттерна
                low_bars_list = [self.low[i] for i in range(0, self.num_bars_pattern, -1)]
                pattern_price = check_pattern_for_short(low_bars_list)
                # Список для стопа
                high_for_stop_list = [self.high[i] for i in range(0, self.num_bars_second_if, -1)]
                second_if = check_high_above_ind(high_for_stop_list, indicator_list)

                if pattern_price and second_if:
                    # Если соблюдены условия на вход проверим profit/loss
                    # Target должен быть больше stop loss
                    stop_price = self.get_stop_price_for_short()
                    price_stop_permission = self.check_price_stop_permission(stop_price, pattern_price, atr_for_all)
                    # Если есть permission выставляем заявку, если нет отменяем если была
                    if price_stop_permission:
                        self.open_or_improve_sell_stop(pattern_price)
                    else:
                        if self.sell_stop:
                            self.cancel(self.sell_stop)
                else:
                    logger.debug(f'pattern_price: {pattern_price}')
                    logger.debug(f'second_if: {second_if}')

    # ===Вспомогательные функции стратегии====================================

    def check_price_stop_permission(self, stop_price: float, pattern_price: float, atr_for_all: float) -> bool:
        """Разрешает открытие позиции при profit больше loss.

        Сравнивает разницу ценой открытия и ценой стопа по модулю с ценой atr(он target).
        Если разница меньше(Stop меньше Target): True

        Args:
            stop_price (float): Предполагаемый Stop loss позиции
            pattern_price (float): Предполагаемая цена открытия позиции
            atr_for_all (float): Среднее значение отклонения цены за период

        Returns:
            bool
        """
        delta = abs(stop_price-pattern_price)
        delta = round(delta, 3)
        pl = atr_for_all / delta
        pl = round(pl, 2)
        if delta <= atr_for_all:
            logger.debug(f'Permission is Ok. {pl}')
            return True
        else:
            logger.debug(f'delta:{delta} > atr:{atr_for_all}, pl:{pl}')
            logger.debug('Not permission.')
            return False

    def get_stop_price_for_long(self) -> float:
        """Возвращает цену Stop loss for long.

        Создает список из заданного количества low баров.
        Сравнивает min списка со значением индикатора(ma)
        Возвращает min значение как stop_price.

        Returns:
            stop_price (float): Значение Stop loss for long.
        """
        low_list = [self.low[i] for i in range(0, self.num_bars_stoploss, -1)]
        min_bars = min(low_list)
        return min_bars if min_bars < self.ma_slow[0] else self.ma_slow[0]

    def get_stop_price_for_short(self):
        """Возвращает цену Stop loss for short.

        Создает список из заданного количества high баров.
        Сравнивает max списка со значением индикатора(ma)
        Возвращает max значение как stop_price.

        Returns:
            stop_price (float): Значение Stop loss for short.
        """
        high_list = [self.high[i] for i in range(0, self.num_bars_stoploss, -1)]
        max_bars = max(high_list)
        return max_bars if max_bars > self.ma_slow[0] else self.ma_slow[0]

    # ===Функции выставления заявок===========================================

    def open_or_improve_sell_stop(self, price_order):
        """Выставляет стоп ордер на продажу.<class 'backtrader.order.SellOrder'>

        Проверяет, существует ли ордер:
            если нет - выставляет
            если есть - проверяет на лучшие условия
                если условия лучше снимает старый и ставит лучше

        Args:
            price_order (float): цена заявки
        """
        # Sell Stop Limit на 0.002 ниже полученной цены, округляет до 3 знаков после запятой.
        price_order = price_order - 0.002
        price_order = round(price_order, 3)

        # Если ордера вообще еще не было
        if not self.sell_stop:
            self._sell_stop_order(price_order)
            logger.debug('None.')
            return

        # Если ордер есть, проверяем условия улучшать или нет
        elif self.sell_stop and self.sell_stop.status == bt.Order.Accepted:
            if self.sell_stop.price < price_order:
                self.cancel(self.sell_stop)

                # MARK: Что бы успевала сработать OCO при перестановке
                # Отменяем и после паузы ставим максимально одновременно
                self._sleep_is_targets()
                self._sell_stop_order(price_order)
                logger.debug('Better.')
            else:
                logger.debug('Order is ok.')

        # Если ордера нет, но он уже был(исполнен или отменен)
        else:
            self._sell_stop_order(price_order)
            logger.debug('Not alive.')

    def open_or_improve_buy_stop(self, price_order):
        """Выставляет стоп ордер на покупку. <class 'backtrader.order.BuyOrder'>

        Проверяет, существует ли ордер:
            если нет - выставляет
            если есть - проверяет на лучшие условия
                если условия лучше снимает старый и ставит лучше

        Args:
            price_order (float): цена заявки
        """
        # Buy Stop Limit на 0.002 выше полученной цены, округляет до 3 знаков после запятой.
        price_order = price_order + 0.002
        price_order = round(price_order, 3)

        # Если ордера вообще еще не было
        if not self.buy_stop:
            self._buy_stop_order(price_order)
            logger.debug('None.')
            return

        # Если ордер есть, проверяем условия улучшать или нет
        elif self.buy_stop and self.buy_stop.status == bt.Order.Accepted:
            if self.buy_stop.price > price_order:
                self.cancel(self.buy_stop)

                # MARK: Что бы успевала сработать OCO при перестановке
                # Отменяем и после паузы ставим максимально одновременно
                self._sleep_is_targets()
                self._buy_stop_order(price_order)
                logger.debug('Better.')
            else:
                logger.debug('Order is ok.')

        # Если ордера нет, но он уже был(исполнен или отменен)
        else:
            self._buy_stop_order(price_order)
            logger.debug('Not alive.')

    def _buy_stop_order(self, price_order: float):
        """Выставляет Stop на покупку.

        Выставляет Buy Stop Limit.
        Округляет до 3 знаков после запятой.

        Args:
            price_order (float): price order
        """
        price_order = round(price_order, 3)
        self.buy_stop = self.buy(exectype=bt.Order.Stop, price=price_order)
        logger.info(f'Buy Stop: {self.buy_stop.price}')  # type: ignore

    def _sell_stop_order(self, price_order: float):
        """Выставляет Stop на продажу.

        Выставляет Sell Stop Limit.
        Округляет до 3 знаков после запятой.

        Args:
            price_order (float): price order
        """
        price_order = round(price_order, 3)
        self.sell_stop = self.sell(exectype=bt.Order.Stop, price=price_order)
        logger.info(f'Sell Stop: {self.sell_stop.price}')  # type: ignore

    def _sleep_is_targets(self):
        """Sleep если is_target = True."""
        if self.is_target:
            time.sleep(1)

        # ===Конец основного блока этой стратегии===========================================

    def log(self, txt: str, dt=None) -> None:
        """Вывод строки с датой на консоль.

        Выводит str на консоль. если dt is None, берет текущую дату.
        """
        dt = bt.num2date(self.datas[0].datetime[0]) if dt is None else dt
        print(f'{dt.strftime("%d.%m.%Y %H:%M")}, {txt}')

    def notify_data(self, data, status, *args, **kwargs):  # noqa
        """Изменение статуса приходящих баров на 'LIVE' после получения исторических данных."""
        # Получаем статус (только при LiveBars=True)
        dataStatus = data._getstatusname(status)  # noqa
        # Не можем вывести в лог, т.к. первый статус DELAYED получаем до первого бара (и его даты)
        print(dataStatus)
        self.isLive = dataStatus == 'LIVE'  # noqa

    def notify_order(self, order):
        """Вывод на консоль изменение статуса заявки или результат исполнения."""
        # Если заявка не исполнена: status in [order.Submitted, order.Accepted]
        # (отправлена брокеру или принята брокером)
        if order.status in [order.Submitted, order.Accepted]:
            self.log(f'Order Status: {order.getstatusname()}. TransId={order.ref}')
            return  # то выходим, дальше не продолжаем

        # Если заявка отменена: status in [order.Canceled]
        if order.status in [order.Canceled]:
            self.log(f'Order Status: {order.getstatusname()}. TransId={order.ref}')
            return  # то выходим, дальше не продолжаем

        # Если заявка исполнена: status in [order.Completed]
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'Bought @{order.executed.price:.2f}, '
                    f'Cost={order.executed.value:.2f}, '
                    f'Comm={order.executed.comm:.2f}'
                )
            elif order.issell():
                self.log(
                    f'Sold @{order.executed.price:.2f}, '
                    f'Cost={order.executed.value:.2f}, '
                    f'Comm={order.executed.comm:.2f}'
                )

        # Нет средств, или заявка отклонена брокером
        elif order.status in [order.Margin, order.Rejected]:
            self.log(f'Order Status: {order.getstatusname()}. TransId={order.ref}')
        self.order = None  # Этой заявки больше нет  # noqa

    def notify_trade(self, trade):
        """Выводит на консоль результат при закрытии позиции."""
        # Если позиция не закрыта
        if not trade.isclosed:
            return  # то статус позиции не изменился, выходим, дальше не продолжаем
        # Если позиция закрыта, выводим результат.
        self.log(f'Trade Profit, Gross={trade.pnl:.2f}, NET={trade.pnlcomm:.2f}')
