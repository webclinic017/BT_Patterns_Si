from BackTraderQuik.QKStore import QKStore
from QuikPy import QuikPy


def print_connection() -> None:
    """Выводит параметры соединения с QUIK в консоль."""
    qp_provider = QuikPy()  # Вызываем конструктор QuikPy с подключением к удаленному компьютеру с QUIK
    trade_date = qp_provider.GetInfoParam("TRADEDATE")["data"]
    server_time = qp_provider.GetInfoParam("SERVERTIME")["data"]
    msg = f'Python check connection: {server_time}'

    print('-' * 25)
    print(f'Подключено к терминалу QUIK по адресу: {qp_provider.Host}')
    print(f'Терминал QUIK подключен к серверу: {qp_provider.IsConnected()["data"] == 1}')
    print(f'Дата на сервере: {trade_date}')
    print(f'Время на сервере: {server_time}')
    print(f'Отправка сообщения в QUIK: {msg}{qp_provider.MessageInfo(msg)["data"]}')
    print('-' * 25)


def print_account_money(trade_account_id: str, firm_id: str) -> None:
    """Получает из QUIK План чистых позиций и Текущиие позиций в деньгах и выводит в консоль.
    
    Args:
        trade_account_id (str):
        firm_id (str): 

    Returns:
        Print()
    """

    trade_account_id = trade_account_id
    firm_id = firm_id

    store = QKStore()

    money_limits = store.GetMoneyLimits(
        ClientCode='',
        FirmId=firm_id,
        TradeAccountId=trade_account_id,
        LimitKind=0,
        CurrencyCode='SUR',
        IsFutures=True
    )
    positions_limits = store.GetPositionsLimits(
        FirmId=firm_id,
        TradeAccountId=trade_account_id,
        IsFutures=True
    )

    print('-' * 25)
    print(f'План чистых позиций: {money_limits}')
    print(f'Текущих чистых позиций: {positions_limits}')
    print('-' * 25)
