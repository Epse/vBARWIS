from pydantic import BaseModel, Field, BeforeValidator
from typing import Literal, Any
from typing import Annotated

class InnerWind(BaseModel):
	wind_speed: int
	wind_direction: int
	wind_direction_deviation_left: int
	wind_direction_deviation_right: int
	wind_gust: int

	def to_human(self) -> str:
		return f"{self.wind_speed}G{self.wind_gust}KT{self.wind_direction} {self.wind_direction_deviation_left}V{self.wind_direction_deviation_right}"

class WindObservation(InnerWind):
	runway: str

class WindObservationTimed(WindObservation):
	time: str

class WindForecast(BaseModel):
	forecast_slots: list[WindObservationTimed]

class SensorReading(InnerWind):
	type: str
	label: Annotated[str, BeforeValidator(str)]
	date: int

class TailCrossWind(BaseModel):
	tail_wind: Annotated[float, Field(alias="tailWind")]
	cross_wind: Annotated[float, Field(alias="crossWind")]

class BaseSensorData(BaseModel):
	sensor_reading: SensorReading

class RunwaySensorData(BaseSensorData):
	sensor_type: Literal['runway']
	sensor_reading: SensorReading
	sensor_wind: TailCrossWind
	sensor_graph: dict[str, Any]

class SensorSensorData(BaseSensorData):
	sensor_type: Literal['sensor']
	sensor_reading: SensorReading

SensorDetail = Annotated[SensorSensorData | RunwaySensorData, Field(discriminator='sensor_type')]

class Reading(BaseModel):
	# skip airport_movements
	# skip meteo_readings as well, we want per runway part
	wind_forecast: WindForecast
	wind_sensor_detail: dict[str, SensorDetail]