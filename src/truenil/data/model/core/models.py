import datetime
from peewee import *
from dotenv import load_dotenv
from os import environ
from playhouse.postgres_ext import *

from truenil.data.model.ConnectionState import PeeweeConnectionState

load_dotenv()
PG_HOST = environ.get("POSTGRES_HOST_NAME", default="localhost")
POSTGRES_USER_NAME = environ.get("POSTGRES_USER_NAME", default="postgres")
POSTGRES_USER_PASSWORD = environ.get("POSTGRES_USER_PASSWORD", default="password")

#initialize connection to database
db = PostgresqlExtDatabase("truenil", user=POSTGRES_USER_NAME, password=POSTGRES_USER_PASSWORD, host=PG_HOST)
db._state = PeeweeConnectionState()


class BaseModel(Model):
    created_at= DateTimeTZField(default=datetime.datetime.now)
    updated_at= DateTimeTZField(default=datetime.datetime.now)
    created_by = TextField(default="SYSTEM")
    updated_by = TextField(default="SYSTEM")

    class Meta:
        database = db


class Organization(BaseModel):
    id = BigAutoField(primary_key=True)
    name = TextField(null=False)
    website = TextField(null=False)
    details = TextField()

    class Meta:
        table_name = "organization"
        schema = "core"


class CoreModel(BaseModel):
    id = BigAutoField(primary_key=True)
    organization = ForeignKeyField(Organization, null=False)


class User(CoreModel):
    user_first_name = TextField(null=False)
    user_last_name = TextField(null=False)
    # Email address used for login
    user_id= TextField(null=False)
    # Values would refer to IDP Provider details.
    # e.g. Google, AWS, Microsoft, Apple, ETC
    idp_provider = TextField(null=True)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = "organization_user"
        schema = "core"


user_org_unique_idx = User.index(
    User.organization,
    User.user_id,
    unique=True)
User.add_index(user_org_unique_idx)




