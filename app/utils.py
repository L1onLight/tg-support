import inspect
import secrets
from types import FrameType

import telegram.ext
from telegram import Update, _user
from telegram.ext import ContextTypes

import keyboards as kb
from app.translation import translate
from models import User, Conversation, ConversationThrough, Message, Token


def generate_token(length=48):
    """
    Generate a random token with the specified length.
    The default length is 48 characters.
    """
    return secrets.token_hex(length // 2)


def get_pages(length: int, max_q=5) -> int:
    """Requires query length as int to obtain n of pages.
    """
    n_pages = 0
    if length <= max_q:
        n_pages = 1
    elif length // max_q > 0:
        n_pages = length // max_q
        if n_pages * max_q < length:
            n_pages += 1
    return n_pages


def get_line_number() -> FrameType | None:
    """
    Retrieve the line number of the calling code.

    This function uses the `inspect` module to get information about the current and
    calling frames, allowing it to determine the line number of the calling code.

    :return: The line number of the calling code.
    :rtype: FrameType
    """
    frame = inspect.currentframe()
    try:
        return frame.f_back.f_back.f_lineno
    finally:
        del frame


def get_user(tg: int | Update, return_tg_data=False) -> User | _user.User:
    """
    Searches and returns User.
    :param tg: User Telegram ID(int) or Update
    :type tg: int | Update
    :param return_tg_data: If true, return as Telegram Data Dictionary
    :type return_tg_data: bool

    :return: User model instance
    """
    if isinstance(tg, Update):
        try:
            tg_data = tg.message.from_user
        except AttributeError:
            tg_data = tg.callback_query.from_user
        if return_tg_data:
            user = tg_data
        else:

            user = User.get_or_none(id=tg_data.id)

    else:
        user = User.get_or_none(id=tg)
    if isinstance(user, User):
        print("USER: %s" % get_line_number())
    return user


def check_callback_data(cd: str, to_inspect: tuple) -> bool:
    """
    Search inspect string in callback data
    :param cd: Telegram callback data
    :param to_inspect: Tuple of strings to search
    :return: If found returns True, else False
    """
    if any(s in cd for s in to_inspect):
        return True
    else:
        return False


def clear_context(context: ContextTypes.DEFAULT_TYPE, save: tuple = None, remove: tuple = None) -> None:
    """
    Clears specific keys from the user data in the provided context.
    :param context: (ContextTypes.DEFAULT_TYPE): The context object containing user data.
    :param save: (tuple, optional): A tuple of keys to be excluded from removal. Default is None.
    :param remove: A tuple of keys to be included in the cleanup.

    Default keys to remove:

    "waiting_for_username_reply",
    "waiting_for_token_reply",
    "a_c_page_list",
    "conversation_id",
    "inspect_list_page",
    "agent_list_page",
    "token_page_list"

    """
    to_remove = ["waiting_for_username_reply", "a_c_page_list", "conversation_id", "inspect_list_page",
                 "agent_list_page", "token_page_list", "waiting_for_token_reply"]

    if save:
        for item in save:
            to_remove.pop(item)
    if remove:
        for item in remove:
            to_remove.append(item)

    for item in to_remove:
        context.user_data.pop(item, None)


async def paginate_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE, _user: User, lang: str, ):
    query = update.callback_query
    callback_data = update.callback_query.data

    count = Token.filter(Token.is_activated == False).count()
    if count == 0:
        await query.answer(translate("no_active_tokens", lang), show_alert=True)
        return
    max_q = get_pages(count)
    context.user_data.setdefault("token_page_list", 1)

    if callback_data == "token_list":
        context.user_data["token_page_list"] = 1
    elif callback_data == "tokens_previous":
        context.user_data["token_page_list"] = max(1, context.user_data["token_page_list"] - 1)
    elif callback_data == "tokens_next":
        context.user_data["token_page_list"] = min(max_q, context.user_data["token_page_list"] + 1)

    pagination = Token.select().where(Token.is_activated == False).paginate(
        context.user_data["token_page_list"], 5)

    result = "".join(
        [f"```id:{token.id}\n{token.token}```\n\n" for token in pagination])

    try:
        await update.callback_query.message.edit_text(
            f"{translate("pagination", lang)} {context.user_data["token_page_list"]} / {max_q}\n{result}",
            parse_mode='MarkdownV2',
            reply_markup=kb.tokens_pagination(lang))
    except telegram.error.BadRequest:
        await query.answer(translate("last_page", lang))
    pass


async def paginate_active_conversations(update: Update, context: ContextTypes.DEFAULT_TYPE, _user: User, lang: str, ):
    query = update.callback_query
    callback_data = update.callback_query.data
    count = Conversation.filter(Conversation.is_closed == False).count()
    if count == 0:
        await query.answer(translate("no_active_conv", lang), show_alert=True)
        return
    max_q = get_pages(count, max_q=1)
    context.user_data.setdefault("a_c_page_list", 1)
    if callback_data == "ag1":

        context.user_data["a_c_page_list"] = 1
    elif callback_data == "a_c_previous":
        context.user_data["a_c_page_list"] = max(1, context.user_data[
            "a_c_page_list"] - 1)
    elif callback_data == "a_c_next":
        context.user_data["a_c_page_list"] = min(max_q, context.user_data[
            "a_c_page_list"] + 1)

    conv = Conversation.select().where(Conversation.is_closed == False).paginate(
        context.user_data["a_c_page_list"], 1).first()

    first_msg = Message.select().join(ConversationThrough).where(
        ConversationThrough.conversation == conv).order_by(Message.created_at).first()
    msg_body = first_msg.body if isinstance(first_msg, Message) else None
    context.user_data["conversation_id"] = conv.id

    result = "".join(f"ID: {conv.id}\n"
                     f"{translate("msg", lang)} {msg_body}\n"
                     f"{translate("name", lang)} {conv.customer.tg_name}\n\n ")
    try:
        await update.callback_query.edit_message_text(
            f"{translate("pagination", lang)} {context.user_data["a_c_page_list"]} / "
            f"{max_q}\n{result}", reply_markup=kb.a_c_pagination(lang, conv.id))
    except telegram.error.BadRequest:
        await query.answer(translate("last_page", lang))


async def paginate_joined_conversations(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, lang: str, ):
    query = update.callback_query
    callback_data = update.callback_query.data

    count = Conversation.filter((Conversation.is_closed == False) & (Conversation.agent == user)).count()
    if count == 0:
        await query.answer(translate("no_active_conv", lang), show_alert=True)
        return
    max_q = get_pages(count, max_q=1)
    context.user_data.setdefault("a_j_c_page_list", 1)
    if callback_data == "ag2":
        context.user_data["a_j_c_page_list"] = 1
    elif callback_data == "a_j_c_previous":
        context.user_data["a_j_c_page_list"] = max(1, context.user_data[
            "a_j_c_page_list"] - 1)
    elif callback_data == "a_j_c_next":
        context.user_data["a_j_c_page_list"] = min(max_q, context.user_data[
            "a_j_c_page_list"] + 1)

    conv = Conversation.filter((Conversation.is_closed == False) & (Conversation.agent == user)).paginate(
        context.user_data["a_j_c_page_list"], 1).first()

    first_msg = Message.select().join(ConversationThrough).where(
        ConversationThrough.conversation == conv).order_by(Message.created_at).first()
    msg_body = first_msg.body if hasattr(first_msg, "__data__") else None
    context.user_data["conversation_id"] = conv

    result = "".join(f"ID: {conv.id}\n"
                     f"{translate("msg", lang)} {msg_body}\n"
                     f"{translate("name", lang)} {conv.customer.tg_name}\n\n ")
    try:
        await update.callback_query.edit_message_text(
            f"{translate("pagination", lang)} {context.user_data["a_j_c_page_list"]} / "
            f"{max_q}\n{result}", reply_markup=kb.a_j_c_pagination(lang, conv.id))
    except telegram.error.BadRequest:
        await query.answer(translate("last_page", lang))


async def paginate_closed_conversations(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, lang: str, ):
    query = update.callback_query

    callback_data = update.callback_query.data

    count = Conversation.filter(Conversation.is_closed == True).count()
    if count == 0:
        await query.answer(translate("no_closed_conv", lang), show_alert=True)
        return

    max_q = get_pages(count, max_q=1)
    context.user_data.setdefault("c_c_page_list", 1)

    if callback_data in "ag3":
        context.user_data["c_c_page_list"] = 1
    elif callback_data == "c_c_previous":
        context.user_data["c_c_page_list"] = max(1, context.user_data["c_c_page_list"] - 1)
    elif callback_data == "c_c_next":
        context.user_data["c_c_page_list"] = min(max_q, context.user_data["c_c_page_list"] + 1)

    conv = Conversation.select().where(
        Conversation.agent == user, Conversation.is_closed == True).paginate(
        context.user_data["c_c_page_list"], 1).first()

    if conv:
        first_msg = Message.select().join(ConversationThrough).where(
            ConversationThrough.conversation == conv).order_by(Message.created_at).first()
        msg_body = first_msg.body if hasattr(first_msg, "__data__") else None
        context.user_data["conversation_id"] = conv

        result = "".join(f"ID: {conv.id}\n"
                         f"{translate('msg', lang)} {msg_body}\n"
                         f"{translate('name', lang)} {conv.customer.tg_name}\n\n ")

        try:
            await update.callback_query.edit_message_text(
                f"{translate('pagination', lang)} {context.user_data['c_c_page_list']} / "
                f"{max_q}\n{result}", reply_markup=kb.c_c_pagination(lang, conv.id))
        except telegram.error.BadRequest:
            await query.answer(translate("last_page", lang))
    else:
        await query.answer("No conversations found.")


async def paginate_inspect(update: Update, context: ContextTypes.DEFAULT_TYPE, _user: User, lang: str, data=None):
    query = update.callback_query

    callback_data = query.data if query else data

    context.user_data.setdefault("inspect_list_page", 1)

    conv_id = int(callback_data.split("_")[-1]) if data else \
        int(update.callback_query.message.reply_markup.inline_keyboard[0][0].callback_data.split("_")[-1])

    conv = Conversation.get_or_none(id=conv_id)
    if not conv:
        await update.message.reply_text(translate("conv_not_exist", lang) % conv_id)
        return
    max_q = Message.select().join(ConversationThrough).where(
        ConversationThrough.conversation == conv).count()

    max_q = get_pages(max_q)
    current_page = context.user_data["inspect_list_page"]
    if (max_q == current_page and callback_data == "inspect_next_page"
            or current_page == 1 and callback_data == "inspect_previous_page"):
        await query.answer(translate("last_page", lang))
        return
    if callback_data == "inspect_list" or data:
        context.user_data["inspect_list_page"] = 1
    elif callback_data == "inspect_previous_page":
        context.user_data["inspect_list_page"] = max(1, context.user_data["inspect_list_page"] - 1)
    elif callback_data == "inspect_next_page":
        context.user_data["inspect_list_page"] = min(max_q, context.user_data["inspect_list_page"] + 1)

    messages = Message.select().join(ConversationThrough).where(
        ConversationThrough.conversation == conv_id).paginate(
        context.user_data["inspect_list_page"], 5).order_by(
        Message.created_at)

    text = (f"{translate('pagination', lang)} {context.user_data["inspect_list_page"]}/{max_q}\n\n" +
            "".join(
                f"{msg.author.tg_name}:\n{msg.body}\n\n" for msg in messages))

    kwargs = {
        "text": text,
        "reply_markup": kb.inspect_messages(lang, conv_id)
    }

    if data:
        await update.message.reply_text(**kwargs)
    else:
        await update.callback_query.message.edit_text(**kwargs)

    pass


async def paginate_agent_list(update: Update, context: ContextTypes.DEFAULT_TYPE, _user: User, lang: str):
    query = update.callback_query
    callback_data = update.callback_query.data

    max_q = get_pages(User.filter(User.is_agent).count())

    context.user_data.setdefault("agent_list_page", 1)

    if callback_data == "agent_list":
        context.user_data["agent_list_page"] = 1
    elif callback_data == "agent_previous_page":
        context.user_data["agent_list_page"] = max(1, context.user_data["agent_list_page"] - 1)
    elif callback_data == "agent_next_page":
        context.user_data["agent_list_page"] = min(max_q, context.user_data["agent_list_page"] + 1)
    pagination = User.select().where(User.is_agent).paginate(
        context.user_data["agent_list_page"], 5)
    result = f"".join(
        [f"Telegram: [{agent.tg_name}](tg://user?id={agent.id})\n"
         f"{translate("agent_name", lang)} {agent.name}\n"
         f"{translate("tg_id", lang)} `{agent.id}`\n\n"
         for agent in
         pagination])
    try:
        await update.callback_query.message.edit_text(
            f"{translate("pagination", lang)} {context.user_data["agent_list_page"]} / {max_q}\n{result}",
            parse_mode='MarkdownV2',
            reply_markup=kb.agents_pagination(lang))
    except telegram.error.BadRequest as ex:
        if "Message is not modified" in str(ex):
            pass
        await query.answer(translate("last_page", lang))
