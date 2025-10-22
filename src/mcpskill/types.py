"""Type definitions for MCPSkill."""

from typing import Optional
from pydantic import BaseModel, Field


class DownstreamConfig(BaseModel):
    """Configuration for a downstream MCP server."""

    command: str = Field(description="Command to run the MCP server")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    env: dict[str, str] = Field(default_factory=dict, description="Environment variables")


class Config(BaseModel):
    """Main MCPSkill configuration."""

    name: str = Field(description="Name of the MCP skill")
    description: str = Field(
        default="Direct access to MCP server tools",
        description="Description shown to users"
    )
    downstream: DownstreamConfig = Field(description="Downstream MCP server configuration")

    class Config:
        extra = "forbid"
