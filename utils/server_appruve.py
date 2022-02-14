import config


def appruve_server(symbol: str, compression_data: int):
    """Выводит запрос на подтверждение соединения с сервером.

    Выводит в консоль тикер и временной интервал.

    Args:
        symbol (str): Ticker symbol    
        compression_data (int): Time Frame

    Если сервер не подтвержден - exit()
    """
    server_broker = config.SERVER

    print('-' * 25)
    print(f'Сервер: {server_broker}.')
    print(f'Ticker symbol: {symbol}')
    print(f'Time Frame: {compression_data}')
    
    appruve_server = str(input(f'(y/n): '))

    if appruve_server != 'y':
        print('Соединение с сервером отменено.')
        exit()

    else:
        print('-' * 25)
