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
    compression_data = 1

    # Параметры счета
    client_code = config.CLIENTCODE
    firm_id = config.FIRMID
    trade_account_id = config.TRADEACCOUNTID

    # Сервисные функции для визуализации подключения и параметров счета.
    appruve_server(symbol, compression_data)
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
        use_positions=False  # True не будет если открыты другие позиции кроме тикера symbol
    )
    cerebro.setbroker(broker)

    data = store.getdata(
        dataname=symbol,
        timeframe=bt.TimeFrame.Minutes,  # type: ignore
        compression=compression_data,
        fromdate=datetime(2021, 10, 1, 10, 00),
        LiveBars=True
    )
    cerebro.addsizer(
        # bt.sizers.FixedReverser,  # Для реверсных систем
        bt.sizers.FixedSize,
        stake=1000
    )
    cerebro.adddata(data)
    cerebro.run()
