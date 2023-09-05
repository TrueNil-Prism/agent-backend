from playhouse.migrate  import *
from playhouse.reflection import print_table_sql

from src.truenil.model.agent.models import Agent, Bucket, File, AgentFile, AgentBucket
from src.truenil.model.core.models import Organization, User

print_table_sql(Organization)
print(";")
print_table_sql(User)
print(";")
print_table_sql(Agent)
print(";")
print_table_sql(Bucket)
print(";")
print_table_sql(File)
print(";")
print_table_sql(AgentFile)
print(";")
print_table_sql(AgentBucket)
print(";")
