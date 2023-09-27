import uvicorn
from fastapi import FastAPI, HTTPException, Header
from peewee import DoesNotExist

from truenil.api.model.agent.models import Agent, MetricContainer
from truenil.data.model.agent.models import Agent as DataAgent, AgentMetrics, AgentToken, AgentTokenAudit
from typing import Annotated

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


@app.post("/v1/register_agent/")
async def register_agent(agent: Agent, authorization: Annotated[list[str] | None, Header()] = None):
    agent_token, is_valid = validate_token(get_bearer_token_from_header(authorization))
    if is_valid:
        existing_agent = None
        # get Agent based on UUID
        try:
            existing_agent = DataAgent.select().where(DataAgent.uuid == agent.uuid).where(
                DataAgent.health_status != 'lost').get()
            if compare_agent(agent, existing_agent):
                existing_agent.version = agent.version,
                existing_agent.health_status = agent.health_status,
                existing_agent.running_as_user_name = agent.running_as_user_name,
                existing_agent.environment_settings = agent.environment_settings,
                existing_agent.metadata = agent.agent_metadata
                existing_agent.save()
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
                                                 metadata=agent.agent_metadata
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
                                             metadata=agent.agent_metadata
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
            existing_agent = DataAgent.select().where(DataAgent.uuid == metric_container.agent_uuid).where(
                DataAgent.health_status != 'lost').get()
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
