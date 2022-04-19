from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
IP = env.str("IP")

DB_USER = env.str("DB_USER")
DB_PASS = env.str("DB_PASS")
DB_NAME = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST")


REDIS_HOST = env.str("REDIS_HOST")
REDIS_PORT = env.str("REDIS_PORT")


LIQPAY_TOKEN = env.str("LIQPAY_TOKEN")

