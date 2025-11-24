from pydantic import BaseModel, Field, BeforeValidator
from typing import Literal, Any
from typing import Annotated
from .meteo_reading import MeteoReadings

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

	def __str__(self) -> str:
		return f"{self.tail_wind}T{self.cross_wind}X"

class BaseSensorData(BaseModel):
	sensor_reading: SensorReading

	def to_human(self) -> str:
		return self.sensor_reading.to_human()

class RunwaySensorData(BaseSensorData):
	sensor_type: Literal['runway']
	sensor_reading: SensorReading
	sensor_wind: TailCrossWind
	sensor_graph: dict[str, Any]

	def to_human(self) -> str:
		return super().to_human() + f" {self.sensor_wind}"

class SensorSensorData(BaseSensorData):
	sensor_type: Literal['sensor']
	sensor_reading: SensorReading

SensorDetail = Annotated[SensorSensorData | RunwaySensorData, Field(discriminator='sensor_type')]

class Reading(BaseModel):
	# skip airport_movements, we care about VATSIM
	wind_forecast: WindForecast
	wind_sensor_detail: dict[str, SensorDetail]
	wind_aloft: dict[str, Any] | None
	meteo_readings: MeteoReadings