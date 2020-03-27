from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
)
import logging
import os

from settings import PROXY
from states import States
from handlers.add_pressure import add_pressure
from handlers.age import age
from handlers.arm import arm
from handlers.cancel import cancel
from handlers.graph_for_period import graph_for_period
from handlers.greeting import greeting
from handlers.pressure import pressure
from handlers.remove_timer import remove_timer
from handlers.set_timer import set_timer
from handlers.sex import sex
from handlers.skip import skip
from handlers.start_button import start_button
from handlers.weight import weight


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename="bot.log"
    )


def main():
    updater = Updater(
        token=os.environ.get('TOKEN'),
        request_kwargs=PROXY,
        use_context=True
    )
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', greeting)],

        states={

            States.START: [CommandHandler('start', greeting)],

            States.AGE: [MessageHandler(Filters.text, age)],

            States.SEX: [MessageHandler(Filters.text, sex)],

            States.WEIGHT: [MessageHandler(Filters.text, weight)],

            States.ADD_PRESSURE: [MessageHandler(Filters.text, add_pressure)],

            States.ARM: [MessageHandler(Filters.regex('^(Right|Left)$'), arm)],

            States.PRESSURE: [MessageHandler(Filters.text, pressure)],

            States.GRAPH_FOR_PERIOD: [CallbackQueryHandler(graph_for_period)],

            States.SET_TIMER: [MessageHandler(Filters.text, set_timer)],

            States.REMOVE_TIMER: [MessageHandler(Filters.text, remove_timer)],

            States.START_BUTTON: [MessageHandler(Filters.text, start_button)]

        },

        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('skip', skip),
            CommandHandler('start', greeting)
            ]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
