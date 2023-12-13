dictionary = {
    "lang_en": {
        "ag_b1":
            "⌛️ Awaiting response from agent",

        "ag_b2":
            "😴 Awaiting response from customer",

        "ag_b3":
            "✅ Completed conversations",

        "token_b":
            "🔐 Using Token",

        "add_agent_b":
            "➕ Add Support Agent",

        "agent_list_b":
            "💻 Active Support Agents",

        "ot_token_b":
            "🔐 One time Tokens",

        "gen_token_b":
            "🎲 Generate Token",

        "shutdown_b":
            "❌ Shutdown Bot",

        "previous_page_b":
            "◀️ Previous page",

        "return_b":
            "↩️ Go Back",

        "next_page_b":
            "▶️ Next page",

        "try_again_b":
            "🔁 Try Again",

        "contact_support_b":
            "Contact Support",

        "something_b":
            "Something Else",

        "welcome":
            "Hello %s! My name is HelPy. I'm your assistant bot for today :)\n\nHow can i help you?",

        "authorized_ag":
            "🔑 Authorized as Agent",

        "choose_auth":
            "Choose an authorization method:",

        "send_token":
            "Send me your Token:",

        "wrong_token":
            "Wrong Token",

        "activated_token":
            "Token has been already activated",

        "authorized_ad":
            "🔑 Authorized as Admin",

        "unauthorized_ad": "Unauthorized. \nPlease contact Management to obtain access.",

        "future_agent_add": "Send me username of future agent:",

        "wrong_username": "Wrong username",

        "already_added": "%s already added",

        "future_agent_added":
            "%s added as agent",

        "pagination":
            "Page:",

        "agent_name":
            "Agent name:",

        "tg_id":
            "TG Id:",

        "last_page":
            "Last page",

        "conversation_start_1":
            "Send me your question to start a conversation:",

        "conversation_start_2":
            "Wait for a support agent to join...",

        "msg":
            "Message:",

        "name":
            "Name:",

        "give_answer_b":
            "Join",

        "no_active_conv":
            "There are no active conversations",

        "ag_joined_1":
            "Joined to conversation with ID: %s",

        "ag_joined_2":
            "Agent joined...",

        "conv_closed_1":
            "Conversation closed with ID: %s",

        "conv_closed_2":
            "Conversation closed. Did you get an answer to your question?",

        "wrong_type_1":
            "Wrong ID",

        "conv_not_exist":
            "Conversation with ID %s doesn't exist",

        "inspect_conv_b":
            "🔎 Inspect",

        "no_closed_conv":
            "No closed conversations",

        "no_active_tokens":
            "No active tokens"

    }
    ,
    "lang_uk": {
        "ag_b1":
            "⌛️ Очікують відповіді від агента",

        "ag_b2":
            "😴 Очікують відповіді від користувача",

        "ag_b3":
            "✅ Завершені діалоги",

        "token_b":
            "🔐 Використовуючи токен",

        "add_agent_b":
            "➕ Додати агента",

        "agent_list_b":
            "💻 Активні агенти",

        "ot_token_b":
            "🔐 Одноразові токени",

        "gen_token_b":
            "🎲 Згенерувати токен",

        "shutdown_b":
            "❌ Вимкнути бота",

        "previous_page_b":
            "◀️ Минула сторінка",

        "return_b":
            "↩️ Повернутись назад",

        "next_page_b":
            "▶️ Наступна сторінка",

        "try_again_b":
            "🔁 Повторити",

        "contact_support_b":
            "Зв'язатися з оператором",

        "something_b":
            "Щось ще",

        "welcome":
            "Привіт, %s! Мене звати HelPy. Сьогодні я твій помічник :) \n\nЧим я можу тобі допомогти?",

        "authorized_ag":
            "🔑 Авторизований як агент",

        "choose_auth":
            "Оберіть спосіб авторизації:",

        "send_token":
            "Надішліть мені токен:",

        "wrong_token":
            "Неправильний токен",

        "activated_token":
            "Токен вже активований",

        "authorized_ad":
            "🔑 Авторизований як адмін",

        "unauthorized_ad": "Не авторизовано. \nБудь-ласка, зв'яжіться з адміністрацією для отримання доступу.",

        "future_agent_add": "Надішліть мені прізвисько майбутнього агента:",

        "wrong_username": "Неправильне прізвисько користувача",

        "already_added": "%s вже додано",

        "future_agent_added":
            "Користувача %s додано як агента",

        "pagination":
            "Сторінка:",

        "agent_name":
            "Ім'я агента:",

        "tg_id":
            "TG Id:",

        "last_page":
            "Остання сторінка",

        "conversation_start_1":
            "Надішліть мені ваше запитання:",

        "conversation_start_2":
            "Зачекайте поки агент підтримки під'єднається...",

        "msg":
            "Повідомлення:",

        "name":
            "Ім'я:",

        "give_answer_b":
            "Приєднатися",

        "no_active_conv":
            "Немає активних діалогів",

        "ag_joined_1":
            "Приєднано до чату з ID: %s",

        "ag_joined_2":
            "Агента під'єднано...",

        "conv_closed_1":
            "Спілкування завершено з ID: %s",

        "conv_closed_2":
            "Спілкування завершено. Чи ви отримали відповідь на ваше питання?",

        "wrong_type_1":
            "Неправильний ID",

        "conv_not_exist":
            "Розмови з ID %s не існує",

        "inspect_conv_b":
            "🔎 Оглянути",

        "no_closed_conv":
            "Немає завершених розмов",

        "no_active_tokens":
            "Немає активних токенів"

    },
}
starting_message = """
Select the language of communication:
-----------------------------------------------------------
Оберіть мову спілкування:
"""


def translate(keyword, lang, insert=None):
    try:
        if keyword == "starting_msg":
            return starting_message
        if lang not in ("lang_uk", "lang_ru", "lang_en"):
            if insert:
                return dictionary["lang_en"][keyword] % insert
            return dictionary["lang_en"][keyword]
        if insert:
            return dictionary[lang][keyword] % insert
        return dictionary[lang][keyword]
    except KeyError:
        print("Dictionary error occurred:", lang, keyword)
        return keyword
