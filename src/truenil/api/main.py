from datetime import datetime
from typing import Annotated
from urllib.parse import urlparse

import uvicorn
from fastapi import FastAPI, HTTPException, Header
from peewee import DoesNotExist

from truenil.api.model.agent.models import Agent, MetricContainer, AgentFiles, UserFilePermission, \
    AgentFileAuditContainer
from truenil.data.model.agent.models import Agent as DataAgent, AgentMetrics, AgentToken, AgentTokenAudit, Bucket, File, \
    AgentFile, AgentBucket, UserFilePermissions, AgentFileAudit

app = FastAPI()


def validate_token(token: str) -> (AgentToken, bool):
    try:
        token_instance = AgentToken.select().where(AgentToken.token == token).where(AgentToken.is_active == True).get()
        return token_instance, True
    except DoesNotExist:
        return None, False


@app.get("/")
async def ping():
    return {"message": "pong"}


def compare_agent(agent: Agent, modelAgent: DataAgent):
    return agent.ip_address == modelAgent.ip_address and agent.host_name == modelAgent.host_name


def get_bearer_token_from_header(auth_token):
    split_token = auth_token[0].split(' ')
    if len(split_token) == 2 and split_token[0].lower() == 'bearer':
        return split_token[1]
    else:
        return None


def get_agent(uuid):
    return DataAgent.select().where(DataAgent.uuid == uuid).where(
        DataAgent.health_status != 'lost').get()


def get_file(file_url):
    return File.select().where(File.file_path == file_url).get()


@app.post("/v1/register_agent/")
async def register_agent(agent: Agent, authorization: Annotated[list[str] | None, Header()] = None):
    agent_token, is_valid = validate_token(get_bearer_token_from_header(authorization))
    if is_valid:
        existing_agent = None
        # get Agent based on UUID
        try:
            existing_agent = get_agent(agent.uuid)
            if compare_agent(agent, existing_agent):
                (DataAgent.update(version=agent.version,
                                  health_status=agent.health_status,
                                  running_as_user_name=agent.running_as_user_name,
                                  environment_settings=agent.environment_settings,
                                  metadata=agent.agent_metadata,
                                  updated_at=datetime.now(),
                                  agent_state=agent.agent_state
                                  ).where(DataAgent.id == existing_agent.id).execute()
                 )
            else:
                existing_agent.health_status = 'lost'
                existing_agent.save()
                created_agent = DataAgent.create(organization_id=agent.organization,
                                                 uuid=agent.uuid,
                                                 version=agent.version,
                                                 health_status=agent.health_status,
                                                 ip_address=agent.ip_address,
                                                 host_name=agent.host_name,
                                                 running_as_user_name=agent.running_as_user_name,
                                                 environment_settings=agent.environment_settings,
                                                 metadata=agent.agent_metadata,
                                                 agent_state=agent.agent_state
                                                 )
                existing_agent = created_agent
        except DoesNotExist:
            created_agent = DataAgent.create(organization_id=agent.organization,
                                             uuid=agent.uuid,
                                             version=agent.version,
                                             health_status=agent.health_status,
                                             ip_address=agent.ip_address,
                                             host_name=agent.host_name,
                                             running_as_user_name=agent.running_as_user_name,
                                             environment_settings=agent.environment_settings,
                                             metadata=agent.agent_metadata,
                                             agent_state=agent.agent_state
                                             )
            existing_agent = created_agent
        AgentTokenAudit.create(agent=existing_agent, token=agent_token, organization=agent.organization)
        return {"message": "success", "agent_id": existing_agent.id}
    else:
        raise HTTPException(status_code=401, detail="Not Authorized")


@app.post("/v1/metrics/")
async def metrics(metric_container: MetricContainer, authorization: Annotated[list[str] | None, Header()] = None):
    agent_token, is_valid = validate_token(get_bearer_token_from_header(authorization))
    if is_valid:
        existing_agent = None
        # get Agent based on UUID
        try:
            existing_agent = get_agent(metric_container.agent_uuid)
            for metric in metric_container.agent_metrics:
                """
                metric_name : str
        metric_value : float
        # Optional field
        process_name : Optional[str]
                """
                if metric.process_name is not None:
                    AgentMetrics.create(agent=existing_agent, metric_name=metric.metric_name,
                                        metric_value=metric.metric_value, process_name=metric.process_name,
                                        organization=existing_agent.organization)
                else:
                    AgentMetrics.create(agent=existing_agent, metric_name=metric.metric_name,
                                        metric_value=metric.metric_value, organization=existing_agent.organization)
            AgentTokenAudit.create(agent=existing_agent, token=agent_token, organization=existing_agent.organization)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Agent not found")
    else:
        raise HTTPException(status_code=401, detail="Not Authorized")

    return {"message": "success", "agent_id": existing_agent.id}


@app.post("/v1/file/")
async def files(agent_file_container: AgentFiles, authorization: Annotated[list[str] | None, Header()] = None):
    agent_token, is_valid = validate_token(get_bearer_token_from_header(authorization))
    if is_valid:
        # get Agent based on UUID
        try:
            existing_agent = get_agent(agent_file_container.agent_uuid)
            for agent_file in agent_file_container.agent_files:
                # parse url
                url_components = urlparse(agent_file.file_url, allow_fragments=False)
                bucket_name = f"{url_components.scheme}://{url_components.netloc}"
                # get bucket, create if not exists
                existing_bucket = None
                try:
                    existing_bucket = Bucket.select().where(Bucket.bucket_key == bucket_name).get()
                except DoesNotExist:
                    existing_bucket = Bucket.create(bucket_key=bucket_name, cloud="aws",
                                                    organization_id=existing_agent.organization)
                # get file, create if not exists
                existing_file = None
                try:
                    existing_file = File.select().where(File.file_path == agent_file.file_url).get()
                    existing_file.file_path = agent_file.file_url
                    existing_file.encryption_status = agent_file.encryption_status
                    existing_file.storage_type = agent_file.storage_type
                    existing_file.file_type = agent_file.file_type
                    existing_file.compression_type = agent_file.compression_type
                    existing_file.updated_at = datetime.now(),
                    existing_file.save()
                    # update file
                except DoesNotExist:
                    # create file
                    existing_file = File.create(organization_id=existing_agent.organization,
                                                file_path=agent_file.file_url,
                                                encryption_status=agent_file.encryption_status,
                                                storage_type=agent_file.storage_type, file_type=agent_file.file_type,
                                                compression_type=agent_file.compression_type, bucket=existing_bucket)
                # associate file with agent
                AgentFile.get_or_create(agent=existing_agent, file=existing_file,
                                        organization_id=existing_agent.organization)
                # associate bucket with agent
                AgentBucket.get_or_create(agent=existing_agent, bucket=existing_bucket,
                                          organization_id=existing_agent.organization)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Agent not found")
    else:
        raise HTTPException(status_code=401, detail="Not Authorized")

    return {"message": "success", "agent_id": existing_agent.id}


@app.post("/v1/health/")
async def health(agent: Agent, authorization: Annotated[list[str] | None, Header()] = None):
    return await register_agent(agent, authorization)


def get_file_user_permission(existing_file, user_name):
    return UserFilePermissions.select().where(UserFilePermissions.file == existing_file).where(
        UserFilePermissions.user == user_name).get()


@app.post("/v1/user_file_permissions/")
async def user_file_permissions(user_file_permissions: list[UserFilePermission],
                                authorization: Annotated[list[str] | None, Header()] = None):
    agent_token, is_valid = validate_token(get_bearer_token_from_header(authorization))
    if is_valid:
        for permission in user_file_permissions:
            existing_file = None
            try:
                # lookup file
                existing_file = get_file(file_url=permission.file_url)
            except DoesNotExist:
                raise HTTPException(status_code=404, detail="Not Found")
            try:
                existing_permission = get_file_user_permission(existing_file, permission.user_name)
                existing_permission.permissions = permission.permissions
                existing_permission.updated_at = datetime.now()
                existing_permission.save()
                # update if found
            except DoesNotExist:
                # insert if not found
                UserFilePermissions.create(organization_id=existing_file.organization, file=existing_file,
                                           permissions=permission.permissions, user=permission.user_name)
    else:
        raise HTTPException(status_code=401, detail="Not Authorized")


@app.post("/v1/file_audits/")
async def file_audit_lines(audit_container: AgentFileAuditContainer, authorization: Annotated[list[str] | None, Header()] = None):
    agent_token, is_valid = validate_token(get_bearer_token_from_header(authorization))
    if is_valid:
        existing_agent = None
        # get Agent based on UUID
        try:
            existing_agent = get_agent(audit_container.agent_uuid)
            for audit_line in audit_container.audit_lines:
                file_name: str
                user_name: str
                operation: str
                AgentFileAudit.create(agent=existing_agent,
                                      organization=existing_agent.organization,
                                      file_name=audit_line.file_name,
                                      user_name=audit_line.user_name,
                                      user_email=audit_line.user_email,
                                      operation=audit_line.operation)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Agent not found")
    else:
        raise HTTPException(status_code=401, detail="Not Authorized")

    return {"message": "success", "agent_id": existing_agent.id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
