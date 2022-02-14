from environs import Env

env = Env()
# Read .env into os.environ
env.read_env()

# Настройки счета для срочного рынка
CLIENTCODE = env.str('CLIENTCODE')
FIRMID = env.str('FIRMID')
TRADEACCOUNTID = env.str('TRADEACCOUNTID')

# Сервер/Брокер
SERVER = env.str('SERVER')

# Host
HOST = env.str('HOST')
