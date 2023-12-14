from app.models import *
from app.main import *

if __name__ == "__main__":
    bot = SupportBot(db_handler=db, token=TOKEN)
    with db as Connection:
        create_tables(connection=False)
        bot.run()
