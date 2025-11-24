from typing import Literal, Annotated
from pydantic import BaseModel, Field

class StatsMeteoReading(BaseModel):
	type: Literal['stats'] = 'stats'
	icon: str
	title: str
	description: str

class StatsWindIconReading(BaseModel):
	type: Literal['wind_icon'] = 'wind_icon'
	wind_speed: int
	wind_direction: int
	wind_direction_deviation_left: int
	wind_direction_deviation_right: int
	wind_gust: int
	runway: str

MeteoReading = Annotated[StatsMeteoReading | StatsWindIconReading, Field(discriminator='type')]

class MeteoReadings(BaseModel):
	date: int
	readings: list[MeteoReading]