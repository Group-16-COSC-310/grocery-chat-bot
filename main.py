# from app.bot import Bot
from dialogflow_migration.bot import Bot

def main():
    bot = Bot()
    #initiate conversation with customer
    bot.start_conversation()


if __name__ == '__main__':
  main()