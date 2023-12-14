from datetime import datetime
from peewee import *
import os
from dotenv import load_dotenv

load_dotenv()
DB_HOST = os.environ.get("DB_HOST")
DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = int(os.environ.get("DB_PORT"))
db = MySQLDatabase(DB_NAME, user=DB_USERNAME, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)


def logged_commit():
    """To print line of code where commit used."""
    # print("COMMIT: %s" % utils.get_line_number())
    db.commit()


db.logged_commit = logged_commit


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db
        order_by = "id"


class User(BaseModel):
    id = BigIntegerField(primary_key=True, unique=True)
    tg_name = CharField()
    tg_username = CharField(null=True)
    name = CharField(null=True)
    is_active = BooleanField(default=False)
    is_agent = BooleanField(default=False)
    is_admin = BooleanField(default=False)
    language = CharField(max_length=12)
    last_conversation = DeferredForeignKey('Conversation', backref='user', null=True)

    class Meta:
        db_table = "user"


class Token(BaseModel):
    token = CharField(unique=True, max_length=48)
    created_at = DateTimeField(default=datetime.now)
    is_activated = BooleanField(default=False)


class FutureAgent(BaseModel):
    tg_username = CharField(unique=True)
    is_added = BooleanField(default=False)


class Message(BaseModel):
    author = ForeignKeyField(User, backref="message")
    body = TextField()
    created_at = DateTimeField(default=datetime.now)


class Conversation(BaseModel):
    customer = ForeignKeyField(User, backref="conversation")
    customer_chat = BigIntegerField()
    agent = ForeignKeyField(User, null=True, backref="conversation")
    agent_chat = BigIntegerField(null=True)
    messages = ManyToManyField(Message, backref="conversation")
    created_at = DateTimeField(default=datetime.now)
    agent_join_at = DateTimeField(null=True)
    is_closed = BooleanField(default=False)

    class Meta:
        db_table = "conversation"

    def join_conv(self, agent, chat):
        if not self.agent:
            self.agent_join_at = datetime.now()
        self.agent = agent
        self.agent_chat = chat
        self.is_closed = False
        self.save()


ConversationThrough = Conversation.messages.get_through_model()


def create_tables(connection=True):
    if connection:
        db.connect()

    db_tables: list = db.get_tables()
    tables = ['conversation', 'conversation_message_through', 'futureagent', 'message', 'token', 'user']
    create = False
    for table in tables:
        try:
            db_tables.index(table)
        except ValueError:
            create = True

    if create:
        db.create_tables([User, Token, FutureAgent, Message, Conversation, ConversationThrough])
    if connection:
        db.close()
