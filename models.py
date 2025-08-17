from typing import Annotated
from pydantic import BaseModel
from langgraph.graph import add_messages


class State(BaseModel):
    messages: Annotated[list, add_messages]
