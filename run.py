from datetime import datetime

import backtrader as bt

import config
from BackTraderQuik.QKStore import QKStore  # Хранилище QUIK
from strategy import TrendStrategy
from utils import appruve_server, print_account_money, print_connection

if __name__ == "__main__":
    # Инструмент
    symbol = 'SPBFUT.SiH2'
    # Time Frame
    compression_data_work = 1  # MARK: Time Frame по которому работаем(проводим все расчеты)

    # Параметры счета
    client_code = config.CLIENTCODE
    firm_id = config.FIRMID
    trade_account_id = config.TRADEACCOUNTID

    # Сервисные функции для визуализации подключения и параметров счета.
    appruve_server(symbol, compression_data_work)
    print_connection()
    print_account_money(trade_account_id, firm_id)

    # BackTrader
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TrendStrategy)
    store = QKStore()

    broker = store.getbroker(
        ClientCode=client_code,
        FirmId=firm_id,
        TradeAccountId=trade_account_id,
        IsFutures=True,
        use_positions=False  # True не будет если открыты другие позиции кроме тикера symbol(Опционы например)
    )
    cerebro.setbroker(broker)

    data = store.getdata(
        dataname=symbol,
        timeframe=bt.TimeFrame.Minutes,  # type: ignore
        compression=1,  # MARK: Time Frame по которому бегаем
        fromdate=datetime(2022, 2, 1, 7, 00),
        LiveBars=True
    )
    cerebro.addsizer(
        # bt.sizers.FixedReverser,  # Для реверсных систем
        bt.sizers.FixedSize,
        stake=1000
    )
    # Берем два временных интервала, по первому(младшему) бегает и проверяет ежеминутно
    # По второму (cerebro.resampledata) ведутся расчеты и сама торговля
    cerebro.adddata(data)
    cerebro.resampledata(
        data,
        timeframe=bt.TimeFrame.Minutes,  # type: ignore
        compression=compression_data_work  # MARK: Time Frame по которому работаем
    )
    cerebro.run()
