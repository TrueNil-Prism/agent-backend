import peewee
from pydantic import BaseModel, Json
from truenil.api.model.utils import PeeweeGetterDict
from typing import Any, List, Optional


class ReportedAgentMetrics(BaseModel):
    """
    metric_name is one of the below. Exact case
        cpu_usage
        number_of_vcpu
        max_memory
        memory_used
        disk_space
        free_space
        network_connectivity
        response_time
        error_rate
    """
    metric_name : str
    metric_value : float
    # Optional field
    process_name : str | None = None


class MetricContainer(BaseModel):
    agent_uuid: str
    agent_metrics: list[ReportedAgentMetrics]


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

