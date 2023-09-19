import uvicorn
from fastapi import FastAPI
from peewee import DoesNotExist

import truenil
from truenil.api.model.agent.file import Agent
from truenil.data.model.agent.models import Agent as DataAgent

app = FastAPI()


@app.get("/")
async def ping():
    return {"message": "pong"}


def compare_agent(agent: Agent, modelAgent: DataAgent):
    return agent.ip_address == modelAgent.ip_address and agent.host_name == modelAgent.host_name

@app.post("/register_agent/")
async def create_item(agent: Agent):
    print(agent)
    existing_agent = None
    # get Agent based on UUID
    try:
        existing_agent = DataAgent.select().where(DataAgent.uuid ==agent.uuid).where(DataAgent.health_status!='lost').get()
        if compare_agent(agent, existing_agent):
            existing_agent.version = agent.version,
            existing_agent.health_status = agent.health_status,
            existing_agent.running_as_user_name = agent.running_as_user_name,
            existing_agent.environment_settings = agent.environment_settings,
            existing_agent.metadata = agent.agent_metadata
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
    except  DoesNotExist:
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
    return {"message": "success", "agent_id": existing_agent.id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
