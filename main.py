from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from database import Database
from buttons import *
from utils import get_translation, get_user_language

from config import TOKEN, ADMIN_IDS

# Initialize DB
db = Database()

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    db_user = db.get_user(user.id)

    if db_user:
        # State
        context.user_data['state'] = "STATE_HOME"

        user_language = get_user_language(user.id)

        message = get_translation("main_menu", user_language)

        buttons = get_home_buttons(user_language)

        await update.message.reply_html(
            text=message,
            reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        )
    else:
        # State
        context.user_data['state'] = "STATE_LANGUAGE"

        keyboard = [
            ["🇺🇿 O'zbek", "🇷🇺 Русский"],
            ["🇬🇧 English"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        message = ("<b>"
                   "🇺🇿 Assalom aleykum. Botdan foydalanish uchun o'zingizga qulay tilni tanlang:\n\n"
                   "🇷🇺 Мир вам. Выберите предпочитаемый язык для использования бота:\n\n"
                   "🇬🇧 Peace be upon you. Choose your preferred language to use the bot:"
                   "</b>"
                   )

        await update.message.reply_html(message, reply_markup=reply_markup)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    text = update.message.text

    state = context.user_data.get('state', 'STATE_HOME')

    if state == "STATE_LANGUAGE":
        language_map = {
            "🇺🇿 O'zbek": "uz",
            "🇷🇺 Русский": "ru",
            "🇬🇧 English": "en"
        }

        if text in language_map:
            language = language_map[text]

            # Save language
            context.user_data['user_language'] = language

            message = get_translation("enter_name", language)
            await update.message.reply_html(message, reply_markup=ReplyKeyboardRemove())

            # State
            context.user_data['state'] = "STATE_FULL_NAME"
        else:
            message = ("<b>"
                       "🇺🇿 Berilgan tillardan birini tanlang:\n\n"
                       "🇷🇺 Выберите один из предложенных языков:\n\n"
                       "🇬🇧 Choose one of the given languages:"
                       "</b>"
                       )

            keyboard = [
                ["🇺🇿 O'zbek", "🇷🇺 Русский"],
                ["🇬🇧 English"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

            await update.message.reply_html(text=message, reply_markup=reply_markup)

    elif state == "STATE_FULL_NAME":
        # Save data
        context.user_data['user_full_name'] = text

        message = get_translation("enter_phone", context.user_data.get('user_language', ''))

        keyboard = get_phone_button(context.user_data.get('user_language', ''))
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_html(text=message, reply_markup=reply_markup)

        # State
        context.user_data['state'] = "STATE_PHONE"

    # Settings state
    elif state == "STATE_SETTINGS":
        if text == get_translation("change_name", get_user_language(user.id)):
            message = get_translation("enter_name", get_user_language(user.id))

            keyboard = get_cansel_button(get_user_language(user.id))
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_html(message, reply_markup=reply_markup)

            # State
            context.user_data['state'] = "STATE_CHANGE_NAME"

        elif text == get_translation("change_language", get_user_language(user.id)):
            message = get_translation("welcome_language", get_user_language(user.id))

            keyboard = [
                ["🇺🇿 O'zbek", "🇷🇺 Русский"],
                ["🇬🇧 English"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_html(text=message, reply_markup=reply_markup)

            # State
            context.user_data['state'] = "STATE_CHANGE_LANGUAGE"

        elif text == get_translation("back", get_user_language(user.id)):
            await start(update, context)

            # State
            context.user_data['state'] = "STATE_HOME"

    # Change states
    elif state == "STATE_CHANGE_NAME":
        if text == get_translation("cancel", get_user_language(user.id)):
            keyboard = get_settings_buttons(get_user_language(user.id))
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            message = get_translation("cancel_success", get_user_language(user.id))

            await update.message.reply_html(
                text=message,
                reply_markup=reply_markup

            )

            # State
            context.user_data['state'] = "STATE_SETTINGS"
        else:
            db.update_full_name(
                chat_id=user.id,
                full_name=text
            )

            message = get_translation("success", get_user_language(user.id))

            keyboard = get_settings_buttons(get_user_language(user.id))
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_html(
                text=message,
                reply_markup=reply_markup

            )

            # State
            context.user_data['state'] = "STATE_SETTINGS"

    elif state == "STATE_CHANGE_LANGUAGE":
        language_map = {
            "🇺🇿 O'zbek": "uz",
            "🇷🇺 Русский": "ru",
            "🇬🇧 English": "en"
        }

        if text in language_map:
            language = language_map[text]

            db.update_language(
                chat_id=user.id,
                language=language
            )

            message = get_translation("success", get_user_language(user.id))

            keyboard = get_settings_buttons(get_user_language(user.id))
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_html(
                text=message,
                reply_markup=reply_markup

            )

            # State
            context.user_data['state'] = "STATE_SETTINGS"
        else:
            message = ("<b>"
                       "🇺🇿 Berilgan tillardan birini tanlang:\n\n"
                       "🇷🇺 Выберите один из предложенных языков:\n\n"
                       "🇬🇧 Choose one of the given languages:"
                       "</b>"
                       )

            keyboard = [
                ["🇺🇿 O'zbek", "🇷🇺 Русский"],
                ["🇬🇧 English"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

            await update.message.reply_html(text=message, reply_markup=reply_markup)

    elif state == "STATE_SEND_APPEAL":
        if text == get_translation("cancel", get_user_language(user.id)):
            keyboard = get_home_buttons(get_user_language(user.id))
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            message = get_translation("cancel_success", get_user_language(user.id))

            await update.message.reply_html(
                text=message,
                reply_markup=reply_markup

            )

            # State
            context.user_data['state'] = "STATE_HOME"
        else:
            # Save data
            appeal = db.create_appeal(
                user_id=user.id,
                text=text
            )

            print(appeal)

            message = get_translation("appeal_created", get_user_language(user.id))

            # User message
            await update.message.reply_html(text=message)

            # Admin message
            db_user = db.get_user(user.id)
            for admin_id in ADMIN_IDS:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"<b>🪧 Yangi muroojat:</b>\n\n"
                         f"🙂 <b>Kimdan: </b>{db_user[1]}({db_user[5]})\n"
                         f"✍️ <b>Muroojat:</b> {text}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(text="✍️ Javob yozish", callback_data=f"appeal_{appeal[0]}")]
                    ])
                )

            await start(update, context)

            # State
            context.user_data['state'] = "STATE_HOME"

    elif state == "STATE_ADMIN_WRITE":
        if user.id in ADMIN_IDS:
            db.update_appeal_status(
                appeal_id=context.user_data['appeal_id'],
                response_text=text,
                status="✅ Javob berildi"
            )

            await update.message.reply_html(
                text="✅ Javob foydalanuvchiga yuborildi!"
            )

            await context.bot.send_message(
                chat_id=db.get_appeal(context.user_data['appeal_id'])[1],
                text=f"🪧 <b>Muroojatingiz:</b> {db.get_appeal(context.user_data['appeal_id'])[2]}\n\n"
                     f"✅ <b>Javob:</b> {db.get_appeal(context.user_data['appeal_id'])[3]}",
                parse_mode="HTML",
            )

            await start(update, context)

            # State
            context.user_data['state'] = "STATE_HOME"

    elif state == "STATE_HOME":
        if text == get_translation("send_appeal", get_user_language(user.id)):
            message = get_translation("send_appeal_text", get_user_language(user.id))

            keyboard = get_cansel_button(get_user_language(user.id))
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_html(text=message, reply_markup=reply_markup)

            # State
            context.user_data['state'] = "STATE_SEND_APPEAL"

        elif text == get_translation("my_appeals", get_user_language(user.id)):
            my_appeals = db.get_user_appeals(user.id)
            my_appeals_str = ""
            if my_appeals:
                for appeal in my_appeals:
                    my_appeals_str += f"<b>{appeal[0]}.</b> {appeal[2]} <b>| {appeal[4]}</b>\n\n"
            else:
                my_appeals_str += get_translation("empty_appeals", get_user_language(user.id))

            keyboard = get_home_buttons(get_user_language(user.id))
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_html(text=my_appeals_str, reply_markup=reply_markup)

        elif text == get_translation("settings", get_user_language(user.id)):
            keyboard = get_settings_buttons(get_user_language(user.id))
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            message = f"<b>{get_translation('settings', get_user_language(user.id))}:</b>"

            await update.message.reply_html(text=message, reply_markup=reply_markup)

            # State
            context.user_data['state'] = "STATE_SETTINGS"

        elif text == get_translation("about", get_user_language(user.id)):
            message = get_translation("bot_info", get_user_language(user.id))

            keyboard = get_home_buttons(get_user_language(user.id))
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_html(text=message, reply_markup=reply_markup)

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    state = context.user_data.get('state', '')

    if state == "STATE_PHONE":
        phone = update.message.contact.phone_number

        user_data = context.user_data

        # Save user
        db.insert_user(
            full_name=user_data.get('user_full_name', ''),
            username=user.username,
            chat_id=user.id,
            language=user_data.get('user_language', ''),
            phone=phone
        )

        message = get_translation("main_menu", user_data.get('user_language', ''))

        keyboard = get_home_buttons(user_data.get('user_language', ''))
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_html(text=message, reply_markup=reply_markup)

        # State
        context.user_data['state'] = "STATE_HOME"

async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = update.effective_user

    await query.answer()

    if query.data.split("_")[0] == "appeal":
        if user.id in ADMIN_IDS:
            # Save data
            context.user_data['appeal_id'] = query.data.split("_")[1]

            keyboard = get_cansel_button_inline(get_user_language(user.id), f"back_{query.data.split('_')[1]}")
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = "<b>👉 Muroojatga javob yozing:</b>"

            await query.edit_message_text(text=message, parse_mode="HTML")
            await query.edit_message_reply_markup(reply_markup=reply_markup)

            # State
            context.user_data['state'] = "STATE_ADMIN_WRITE"
    elif query.data.split("_")[0] == "back":
        print(True)
        if user.id in ADMIN_IDS:
            appeal = db.get_appeal(query.data.split("_")[1])
            appeal_user = db.get_user(appeal[1])

            message = (f"<b>🪧 Javob berilgan muroojat:</b>\n\n"
                       f"🙂 <b>Kimdan: </b>{appeal_user[1]}({appeal_user[5]})\n"
                       f"✍️ <b>Muroojat:</b> {appeal[2]}")

            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(text="✍️ Javob yozish", callback_data=f"appeal_{query.data.split('_')[1]}")]
            ])

            await query.edit_message_text(
                text=message,
                parse_mode="HTML"
            )

            await query.edit_message_reply_markup(reply_markup=reply_markup)


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT, message_handler))
    application.add_handler(MessageHandler(filters.CONTACT, contact_handler))

    application.add_handler(CallbackQueryHandler(inline_handler))

    application.run_polling()

if __name__ == "__main__":
    main()
