from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from app.translation import translate


def conversation_start() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🦅🦅🦅🦅🦅", callback_data="lang_en"),
         InlineKeyboardButton("🎈👈🤓🤙👶", callback_data="lang_uk")],
    ])


def user_start(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(translate("contact_support_b", lang), callback_data="start1")]])


def agent(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(translate("ag_b1", lang), callback_data="ag1")],
        [InlineKeyboardButton(translate("ag_b2", lang), callback_data="ag2")],
        [InlineKeyboardButton(translate("ag_b3", lang), callback_data="ag3")]
    ])


def authorization(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(translate("token_b", lang), callback_data="ag_token")]
    ])


def admin(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(translate("add_agent_b", lang), callback_data="agent_add"),
         InlineKeyboardButton(translate("agent_list_b", lang), callback_data="agent_list")],
        [InlineKeyboardButton(translate("ot_token_b", lang), callback_data="token_list"),
         InlineKeyboardButton(translate("gen_token_b", lang), callback_data="token_gen")],
        [InlineKeyboardButton(translate("shutdown_b", lang), callback_data="bot_shutdown")]
    ])


def tokens_pagination(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(translate("previous_page_b", lang), callback_data="tokens_previous")],
        [InlineKeyboardButton(translate("return_b", lang), callback_data="cancel_admin")],
        [InlineKeyboardButton(translate("next_page_b", lang), callback_data="tokens_next")]
    ])


def a_c_pagination(lang: str, *args) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(translate("inspect_conv_b", lang), callback_data="inspect_id_%s" % args[0])],
        [InlineKeyboardButton(translate("previous_page_b", lang), callback_data="a_c_previous")],
        [InlineKeyboardButton(translate("return_b", lang), callback_data="cancel_agent")],
        [InlineKeyboardButton(translate("next_page_b", lang), callback_data="a_c_next")]
    ])


def c_c_pagination(lang: str, *args):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(translate("inspect_conv_b", lang), callback_data="inspect_id_%s" % args[0])],
        [InlineKeyboardButton(translate("previous_page_b", lang), callback_data="c_c_previous")],
        [InlineKeyboardButton(translate("return_b", lang), callback_data="cancel_agent")],
        [InlineKeyboardButton(translate("next_page_b", lang), callback_data="c_c_next")]
    ])


def a_j_c_pagination(lang: str, *args):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(translate("inspect_conv_b", lang), callback_data="inspect_id_%s" % args[0])],
        [InlineKeyboardButton(translate("previous_page_b", lang), callback_data="a_j_c_previous")],
        [InlineKeyboardButton(translate("return_b", lang), callback_data="cancel_agent")],
        [InlineKeyboardButton(translate("next_page_b", lang), callback_data="a_j_c_next")]
    ])


def agents_pagination(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(translate("previous_page_b", lang), callback_data="agent_previous_page")],
        [InlineKeyboardButton(translate("return_b", lang), callback_data="cancel_admin")],
        [InlineKeyboardButton(translate("next_page_b", lang), callback_data="agent_next_page")]
    ])


def admin_back_one_btn(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(translate("return_b", lang), callback_data="cancel_admin")],
    ])


def agent_add_try_again(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(translate("try_again_b", lang), callback_data="agent_add")],
        [InlineKeyboardButton(translate("return_b", lang), callback_data="cancel_admin")],
    ])


def token_try_again(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(translate("try_again_b", lang), callback_data="ag_token"),
         InlineKeyboardButton(translate("return_b", lang), callback_data="cancel", )]
    ])


def inspect_messages(lang: str, *args) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text="ID: %s" % args[0], callback_data='inspect_id_%s' % args[0])],
        [InlineKeyboardButton(text=translate("give_answer_b", lang),
                              callback_data="join_conversation_%s" % args[0])],
        [InlineKeyboardButton(translate("previous_page_b", lang), callback_data="inspect_previous_page")],
        [InlineKeyboardButton(translate("return_b", lang), callback_data="cancel_agent")],
        [InlineKeyboardButton(translate("next_page_b", lang), callback_data="inspect_next_page")]
    ])
