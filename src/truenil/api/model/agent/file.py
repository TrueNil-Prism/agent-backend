import peewee
from pydantic import BaseModel, Json
from truenil.api.model.utils import PeeweeGetterDict
from typing import Any, List, Optional


class Agent(BaseModel):
    uuid: str
    version: str
    health_status: str
    ip_address: str
    host_name: str
    running_as_user_name: Optional[str]
    environment_settings: Optional[str]
    # Unstructured Metadata in JSON form. This would store OS information, and miscellaneous ones
    agent_metadata: Optional[Json[Any]]
    organization: str
