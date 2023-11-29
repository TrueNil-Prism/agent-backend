from playhouse.migrate  import *
from playhouse.reflection import print_table_sql, print_model

from truenil.data.model.agent.models import Agent, Bucket, File, AgentFile, AgentBucket, AgentMetrics, AgentToken, \
    AgentTokenAudit, UserFilePermissions, AgentFileAudit
from truenil.data.model.core.models import Organization, User

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
print_table_sql(AgentMetrics)
print(";")
print_table_sql(AgentToken)
print(";")
print_table_sql(AgentTokenAudit)
print(";")
print_table_sql(UserFilePermissions)
print(";")
print_table_sql(AgentFileAudit)
