from telegram import KeyboardButton, InlineKeyboardButton

from utils import get_translation

def get_home_buttons(language):
    return [
        [get_translation("send_appeal", language), get_translation("my_appeals", language)],
        [get_translation("settings", language), get_translation("about", language)]
    ]

def get_phone_button(language):
    return [
        [KeyboardButton(get_translation("phone", language), request_contact=True)]
    ]

def get_settings_buttons(language):
    return [
        [get_translation("change_name", language)],
        [get_translation("change_language", language), get_translation("back", language)]
    ]

def get_cansel_button(language):
    return [
        [get_translation("cancel", language)]
    ]

def get_cansel_button_inline(language, callback_data):
    return [
        [InlineKeyboardButton(get_translation("cancel", language), callback_data=callback_data)]
    ]