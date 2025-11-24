from pydantic import BaseModel
from .readings import *


class MeteoDocument(BaseModel):
	timepoints: dict[str, Reading]
	currentLabel: str
	rangeValues: list[str]
