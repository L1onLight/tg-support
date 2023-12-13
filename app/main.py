import logging
import re
import sys
from utils import (
    generate_token, get_user, get_pages, check_callback_data, clear_context, paginate_closed_conversations,
    paginate_joined_conversations, paginate_active_conversations, paginate_tokens, paginate_inspect, paginate_agent_list
)
import keyboards as kb
from models import db, User, FutureAgent, Token, Conversation, Message
import telegram

from config import TOKEN
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler, ConversationHandler
)
from translation import translate


class SupportBot:
    def __init__(self, db_handler, token, logger=True):
        self.db = db_handler

        self.app = Application.builder().token(token).build()
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("agent", self.agent))
        self.app.add_handler(CommandHandler("admin", self.admin))
        self.app.add_handler(CallbackQueryHandler(self.query))
        self.app.add_handler(CommandHandler("end", self.end_conv))
        self.app.add_handler(CommandHandler("inspect", self.inspect))

        message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_reply)
        self.app.add_handler(message_handler)
        if logger:
            self.logger = self.logger_setup()

    async def inspect(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        lang = self.get_lang(update, context)
        if len(context.args) == 1:
            try:
                await self.query(update, context, data="inspect_id_" + context.args[0])
                return
            except TypeError:
                await update.message.reply_text(translate("wrong_type_1", lang=lang))
                return

    async def end_conv(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        lang = self.get_lang(update, context)
        conv: Conversation = context.user_data.get("conversation_context")
        if conv:
            conv.is_closed = True
            conv.save()
            db.logged_commit()
            del context.user_data["conversation_context"]
            await update.message.get_bot().send_message(text=translate("conv_closed_2", lang),
                                                        chat_id=conv.customer_chat)
            await update.message.reply_text(translate("conv_closed_1", lang) % conv.id)

    @staticmethod
    def logger_setup():
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
        )
        # set higher logging level for httpx to avoid all GET and POST requests being logged
        logging.getLogger("httpx").setLevel(logging.WARNING)

        logger = logging.getLogger(__name__)
        return logger

    async def query(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data=None, ):
        db.logged_commit()
        query = update.callback_query
        cd = query.data if query else data
        try:
            if cd in ("lang_en", "lang_uk"):
                tg_user = get_user(update, return_tg_data=True)

                user = get_user(update)
                if user:
                    if user.language != cd:
                        user.language = cd
                        user.save()
                else:
                    User.create(id=tg_user.id, tg_name=tg_user.first_name, tg_username=tg_user.username,
                                language=cd)
                context.user_data["lang"] = cd
                await self.welcome(update, context)
                return
            if check_callback_data(cd, ("page", "previous", "next")) and context.user_data.get("user_context"):
                user = context.user_data.get("user_context")
            else:
                user = get_user(update)
                context.user_data.setdefault("user_context", user)

            if not user:
                await self.start(update, context)
                return
            lang = user.language

            if cd == "start1":
                conversation: Conversation = Conversation.create(customer=user,
                                                                 customer_chat=update.callback_query.message.chat_id)
                await update.callback_query.message.edit_text(translate("conversation_start_1", lang))
                context.user_data.setdefault("conversation_created", True)
                context.user_data.setdefault("customer_conversation_context", conversation)
                return

            elif cd == "ag_token":
                context.user_data['waiting_for_token_reply'] = True
                kwargs = {
                    "text": translate("send_token", lang)
                }
                await update.callback_query.message.edit_text(**kwargs)
                return

            elif cd == "cancel":
                clear_context(context)
                await self.welcome(update, context)
                return

            elif cd == "agent_add":
                if not user.is_admin:
                    await self.start(update, context)
                    return

                context.user_data["waiting_for_username_reply"] = True
                await update.callback_query.message.edit_text(translate("future_agent_add", lang),
                                                              reply_markup=kb.admin_back_one_btn(lang))
                return

            elif cd in ("ag1", "a_c_previous", "a_c_next"):
                if not user.is_agent or not user.is_admin:
                    await self.start(update, context)
                    return
                await paginate_active_conversations(update, context, user, lang)
                return

            elif cd in ("ag2", "a_j_c_previous", "a_j_c_next"):
                if not user.is_agent or not user.is_admin:
                    await self.start(update, context)
                    return
                await paginate_joined_conversations(update, context, user, lang)
                return
            elif cd in ("ag3", "c_c_previous", "c_c_next"):
                if not user.is_agent or not user.is_admin:
                    await self.start(update, context)
                    return
                await paginate_closed_conversations(update, context, user, lang)

                return
            elif cd == "cancel_agent":
                clear_context(context)
                await self.authorized(update, context, is_agent=True)
                return

            elif cd == "cancel_admin":
                clear_context(context)
                await self.admin(update, context)
                return

            elif cd == "token_gen":
                if not user.is_admin:
                    await self.unauthorized(update, context)
                    return

                token = Token.create(token=generate_token())
                if self.logger:
                    self.logger.info("Token with ID %s created by: %s" % (token.id, user.id))
                await update.callback_query.message.edit_text(f"OTP Token:\n```{token.token}```",
                                                              parse_mode='MarkdownV2',
                                                              reply_markup=kb.admin_back_one_btn(lang))
                return

            elif cd in ("token_list", "tokens_previous", "tokens_next"):
                if not user.is_admin:
                    await self.unauthorized(update, context)
                    return
                await paginate_tokens(update, context, user, lang)
                return
            elif check_callback_data(cd, ("inspect_list", "inspect_previous_page",
                                          "inspect_next_page", "inspect_id_")):
                if not user.is_agent or not user.is_admin:
                    await self.unauthorized(update, context)
                    return
                await paginate_inspect(update, context, user, lang, data)
                return

            elif cd in ("agent_list", "agent_previous_page", "agent_next_page"):
                if not user.is_admin:
                    await self.start(update, context)
                    return
                await paginate_agent_list(update, context, user, lang)
                return

            elif cd == "bot_shutdown":
                if not user.is_admin:
                    await self.start(update, context)
                    return
                await query.answer()
                self.app.stop_running()
                # await self.app.stop()
                try:
                    sys.exit()
                except SystemExit:
                    pass

            elif check_callback_data(cd, ("join_conversation",)):

                if not user.is_admin or not user.is_agent:
                    return
                conv_id = context.user_data.get("conversation_id")
                if conv_id:
                    del context.user_data["conversation_id"]
                else:
                    if check_callback_data(cd, ("join_conversation",)):
                        conv_id = int(cd.split("_")[-1])
                    else:
                        pattern = re.compile(r'ID: (\d+)')
                        conv_id = pattern.search(update.callback_query.message.text).group(1)
                await update.callback_query.edit_message_text(text=update.callback_query.message.text)
                conv: Conversation = Conversation.get_or_none(id=conv_id)
                context.user_data["conversation_context"] = conv
                if not conv.agent:
                    await update.callback_query.get_bot().send_message(text=translate("ag_joined_2", lang),
                                                                       chat_id=conv.customer_chat)

                conv.join_conv(user, update.callback_query.message.chat_id)

                await update.callback_query.message.reply_text(translate("ag_joined_1", lang) % conv_id)
                return

        finally:
            if not data:
                await query.answer()

    def run(self):
        self.app.run_polling()

    @staticmethod
    def get_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """
        Retrieves the user's language from the context or the database.

        :param update: The Telegram update object.
        :type update: Update
        :param context: The Telegram context object.
        :type context: ContextTypes.DEFAULT_TYPE

        :return: The user's language code.
        :rtype: str
        """
        lang = context.user_data.get("lang")
        if not lang:
            db.logged_commit()
            user = get_user(update)
            if user:
                context.user_data["lang"] = user.language
            else:
                context.user_data["lang"] = "lang_en"
        return lang

    @staticmethod
    async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Starting message with choose language buttons"""
        kwargs = {
            "text": translate("starting_msg", "lang_en"),
            "reply_markup": kb.conversation_start()
        }

        try:
            await update.message.reply_text(**kwargs)
            return
        except AttributeError:
            await update.callback_query.message.reply_text(**kwargs)
            return

    async def welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Starting message with Contact Support button"""
        lang = self.get_lang(update, context)
        user = get_user(update, return_tg_data=True)

        kwargs = {
            "text": translate("welcome", lang, user.first_name),
            "reply_markup": kb.user_start(lang)
        }
        await update.callback_query.message.edit_text(**kwargs)

    async def authorized(self, update: Update, context: ContextTypes.DEFAULT_TYPE, is_agent=False, is_admin=False):
        """Creates menu for agent or admin"""
        if not context.user_data.get("lang"):
            self.get_lang(update, context)
            await self.authorized(update, context, is_agent, is_admin)
            return
        lang = self.get_lang(update, context)

        if is_agent:
            kwargs = {
                "text": translate("authorized_ag", lang),
                "reply_markup": kb.agent(lang)
            }
            try:
                await update.message.reply_text(**kwargs)
            except AttributeError:
                await update.callback_query.message.edit_text(**kwargs)
            return
        if is_admin:
            kwargs = {
                "text": translate("authorized_ad", lang),
                "reply_markup": kb.admin(lang)
            }
            try:
                await update.message.reply_text(**kwargs)
            except AttributeError:
                await update.callback_query.message.edit_text(**kwargs)
            return

    async def admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if is admin and create admin menu"""
        found = context.user_data.get("user_context") if context.user_data.get("user_context") else get_user(update)
        if not found:
            await self.start(update, context)
            return
        if found and found.is_admin:
            await self.authorized(update, context, is_admin=True)
            return
        else:
            await self.unauthorized(update, context)
            return

    async def agent(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if user is agent OR user is FutureAgent(by username) and create agent menu"""
        try:

            user = get_user(update, return_tg_data=True)
            found = get_user(update)

            if not found:
                await self.start(update, context)
                return
            lang = self.get_lang(update, context)
            if found and (found.is_agent or found.is_admin):
                await self.authorized(update, context, is_agent=True)
                return
            elif found and user.username:
                f_ag = FutureAgent.get_or_none(tg_username=user.username)
                if f_ag and not f_ag.is_added:
                    found.is_agent = True
                    f_ag.is_added = True
                    f_ag.save()
                    found.save()
                    if self.logger:
                        self.logger.info("User %s authorized as agent." % found.id)
                    await self.authorized(update, context, is_agent=True)
                    return
            if found and not found.is_agent and not found.is_admin:
                await self.unauthorized(update, context)
                return
            kwargs = {
                "text": translate("choose_auth", lang),
                "reply_markup": kb.authorization(lang)
            }
            await update.message.reply_text(**kwargs)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ab error occurred: {e}")
        finally:
            db.logged_commit()

    async def handle_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print("-------------------------------------")
        is_commit = False
        try:

            lang = self.get_lang(update, context)
            text_reply = update.message.text
            if 'waiting_for_token_reply' in context.user_data:
                if text_reply == "ADMIN_QWERTY":
                    db.logged_commit()
                    user = get_user(update)
                    user.is_agent = True
                    user.is_admin = True
                    user.save()
                    is_commit = True
                    await self.authorized(update, context, is_agent=True)
                    del context.user_data['waiting_for_token_reply']
                    return
                token = Token.get_or_none(token=text_reply)
                if token and not token.is_activated:
                    db.logged_commit()
                    user = get_user(update)
                    if not user:
                        await self.start(update, context)
                        return
                    user.is_agent = True
                    user.save()
                    token.is_activated = True
                    token.save()
                    is_commit = True
                    if self.logger:
                        self.logger.info("Agent permissions added to user %s via token" % user.id)
                    await self.authorized(update, context, is_agent=True)
                    del context.user_data['waiting_for_token_reply']
                    return
                else:

                    kwargs = {
                        "text": translate("wrong_token", lang),
                        "reply_markup": kb.token_try_again(lang)
                    }
                    if token and token.is_activated:
                        kwargs["text"] = translate("activated_token", lang)

                    await update.message.reply_text(**kwargs)
                    return

            elif context.user_data.get("waiting_for_username_reply"):
                db.logged_commit()
                if len(text_reply) < 5 or "@" not in text_reply:
                    await update.message.reply_text("Wrong username",
                                                    reply_markup=kb.agent_add_try_again(lang))
                    return
                del context.user_data['waiting_for_username_reply']
                filter = re.compile(r'@[\w_]+')
                if filter.search(text_reply):
                    nickname = text_reply.replace("@", "")
                    f_agent: FutureAgent = FutureAgent.get_or_none(tg_username=nickname)

                    if f_agent and not f_agent.is_added:
                        kwargs = {
                            "text": translate("already_added", lang, text_reply),
                            "reply_markup": kb.agent_add_try_again(lang)
                        }
                        await update.message.reply_text(**kwargs)
                        return
                    elif f_agent and not f_agent.is_added:
                        f_agent.is_added = False
                        f_agent.save()
                    elif not f_agent:
                        FutureAgent.create(tg_username=nickname)
                    kwargs = {
                        "text": translate("future_agent_added", lang, "@" + nickname)
                    }
                    is_commit = True

                    await update.message.reply_text(**kwargs)

                    await self.admin(update, context)
                    return

            elif context.user_data.get("conversation_context"):

                if context.user_data.get("user_context"):
                    user = context.user_data.get("user_context")
                else:
                    user = get_user(update)
                conv: Conversation = Conversation.get_or_none(id=context.user_data.get("conversation_context").id)
                msg = Message.create(author=user, body=text_reply)
                conv.messages.add(msg)

                await update.get_bot().send_message(chat_id=conv.customer_chat, text=text_reply)
            elif (context.user_data.get("customer_conversation_context")
                  or (context.user_data.get("customer_conversation_context")
                      and context.user_data.get("conversation_created"))):
                db.logged_commit()
                if context.user_data.get("user_context"):
                    user = context.user_data.get("user_context")
                else:
                    user = get_user(update)
                    context.user_data.setdefault("user_context", user)
                conv: Conversation = context.user_data.get("customer_conversation_context")
                if conv.is_closed:
                    context.user_data.pop("customer_conversation_context", None)
                    return
                elif not conv:
                    await self.start(update, context)
                    return
                conv = Conversation.get_or_none(conv.id)
                conv.messages.add(Message.create(author=user, body=text_reply))
                conv.save()
                user.last_conversation = conv
                user.save()
                is_commit = True
                if context.user_data.setdefault("conversation_created"):
                    await update.message.reply_text(translate("conversation_start_2", lang))
                    context.user_data.pop("conversation_created", None)

                if conv.agent_chat:
                    text_reply = f"{conv.customer.tg_name}\n#id{conv.customer.id}\n\n{text_reply}"
                    await update.message.get_bot().send_message(text=text_reply, chat_id=conv.agent_chat)

                return

        finally:
            if is_commit:
                db.logged_commit()

    async def unauthorized(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        lang = self.get_lang(update, context)
        await update.message.reply_text(translate("unauthorized_ad", lang))


if __name__ == "__main__":
    bot = SupportBot(db_handler=db, token=TOKEN)
    with db as Connection:
        bot.run()
