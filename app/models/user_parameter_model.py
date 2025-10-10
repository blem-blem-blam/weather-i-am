import uuid
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, Column, TIMESTAMP
from datetime import datetime
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB


class UserIndividualParameter(BaseModel):
    """A flexible model for a single user parameter, including its importance."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "importance": 8,
                    "parameter_name": "uv_index_threshold",
                    "parameter_value": 6.0,
                    "parameter_array_value": None,
                }
            ]
        }
    )
    importance: int = Field(
        default=1,
        ge=0,
        le=10,
        description="User-set rank of importance, from 0 (ignore) to 10 (utmost importance).",
    )
    parameter_name: str = Field(description="The name of the parameter.")
    parameter_value: Optional[float] = Field(
        default=None, description="The numeric value for the parameter threshold."
    )
    parameter_array_value: Optional[List[str]] = Field(
        default=None, description="The array of values for the parameter."
    )


class UserParameterBase(SQLModel):
    """Base model for user-specific weather and air quality preferences."""

    preferred_lat: float = Field(
        description="Preferred latitude for weather forecasts."
    )
    preferred_lon: float = Field(
        description="Preferred longitude for weather forecasts."
    )
    uv_index_threshold: UserIndividualParameter = Field(
        default_factory=lambda: UserIndividualParameter(
            importance=5, parameter_name="uv_index_threshold", parameter_value=6.0
        ),
        sa_column=Column(JSONB),
        description="UV index level that triggers a notification.",
    )
    aqi_threshold: UserIndividualParameter = Field(
        default_factory=lambda: UserIndividualParameter(
            importance=5, parameter_name="aqi_threshold", parameter_value=100.0
        ),
        sa_column=Column(JSONB),
        description="Air Quality Index (AQI) level that triggers a notification.",
    )
    wind_speed_threshold: UserIndividualParameter = Field(
        default_factory=lambda: UserIndividualParameter(
            importance=3, parameter_name="wind_speed_threshold", parameter_value=10.0
        ),
        sa_column=Column(JSONB),
        description="Wind speed (m/s) that triggers a notification.",
    )
    rain_chance_threshold: UserIndividualParameter = Field(
        default_factory=lambda: UserIndividualParameter(
            importance=7, parameter_name="rain_chance_threshold", parameter_value=0.5
        ),
        sa_column=Column(JSONB),
        description="Chance of rain percentage (0-1) that triggers a notification.",
    )
    pm10_threshold: UserIndividualParameter = Field(
        default_factory=lambda: UserIndividualParameter(
            importance=4, parameter_name="pm10_threshold", parameter_value=50.0
        ),
        sa_column=Column(JSONB),
        description="PM10 concentration (μg/m³) that triggers a notification.",
    )
    pm2_5_threshold: UserIndividualParameter = Field(
        default_factory=lambda: UserIndividualParameter(
            importance=4, parameter_name="pm2_5_threshold", parameter_value=35.0
        ),
        sa_column=Column(JSONB),
        description="PM2.5 concentration (μg/m³) that triggers a notification.",
    )
    allergens: UserIndividualParameter = Field(
        default_factory=lambda: UserIndividualParameter(
            importance=5,
            parameter_name="allergens",
            parameter_array_value=[],
        ),
        sa_column=Column(JSONB),
        description="List of allergens to be notified about.",
    )


class UserParameter(UserParameterBase, table=True):
    """Database model for user parameters, representing the 'user_parameters' table."""

    # The name of the table will be 'userparameter'
    __tablename__ = "user_parameters"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, unique=True
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True, index=True)

    time_created: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
    time_updated: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )


class UserParameterCreate(UserParameterBase):
    """Model for creating new user parameters. All fields are required."""

    pass


class UserParameterUpdate(SQLModel):
    """Model for updating existing user parameters. All fields are optional."""

    preferred_lat: Optional[float] = Field(
        default=None, description="Preferred latitude for weather forecasts."
    )
    preferred_lon: Optional[float] = Field(
        default=None, description="Preferred longitude for weather forecasts."
    )
    uv_index_threshold: Optional[UserIndividualParameter] = Field(
        default=None, description="UV index level that triggers a notification."
    )
    aqi_threshold: Optional[UserIndividualParameter] = Field(
        default=None,
        description="Air Quality Index (AQI) level that triggers a notification.",
    )
    wind_speed_threshold: Optional[UserIndividualParameter] = Field(
        default=None, description="Wind speed (m/s) that triggers a notification."
    )
    rain_chance_threshold: Optional[UserIndividualParameter] = Field(
        default=None,
        description="Chance of rain percentage (0-1) that triggers a notification.",
    )
    pm10_threshold: Optional[UserIndividualParameter] = Field(
        default=None,
        description="PM10 concentration (μg/m³) that triggers a notification.",
    )
    pm2_5_threshold: Optional[UserIndividualParameter] = Field(
        default=None,
        description="PM2.5 concentration (μg/m³) that triggers a notification.",
    )
    allergens: Optional[UserIndividualParameter] = Field(
        default=None,
        description="List of allergens to be notified about.",
    )
