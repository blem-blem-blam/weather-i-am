from enum import Enum


class Allergens(Enum):
    NONE = "none"
    POLLEN = "pollen"
    DUST = "dust"
    MOLD = "mold"
    ALDER_POLLEN = "alder_pollen"
    BIRCH_POLLEN = "birch_pollen"
    GRASS_POLLEN = "grass_pollen"
    RAGWEED_POLLEN = "ragweed_pollen"
    OLIVE_POLLEN = "olive_pollen"


class AirQualityLevels(Enum):
    GOOD = "good"
    MODERATE = "moderate"
    UNHEALTHY_FOR_SENSITIVE_GROUPS = "unhealthy_for_sensitive_groups"
    UNHEALTHY = "unhealthy"
    VERY_UNHEALTHY = "very_unhealthy"
    HAZARDOUS = "hazardous"


class WeatherConditions(Enum):
    CLEAR = "clear"
    CLOUDS = "clouds"
    RAIN = "rain"
    DRIZZLE = "drizzle"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"
    MIST = "mist"
    SMOKE = "smoke"
    HAZE = "haze"
    DUST = "dust"
    FOG = "fog"
    SAND = "sand"
    ASH = "ash"
    SQUALL = "squall"
    TORNADO = "tornado"


class WindSpeedLevels(Enum):
    CALM = "calm"
    LIGHT_AIR = "light_air"
    LIGHT_BREEZE = "light_breeze"
    GENTLE_BREEZE = "gentle_breeze"
    MODERATE_BREEZE = "moderate_breeze"
    FRESH_BREEZE = "fresh_breeze"
    STRONG_BREEZE = "strong_breeze"
    HIGH_WIND = "high_wind"
    GALE = "gale"
    STRONG_GALE = "strong_gale"
    STORM = "storm"
    VIOLENT_STORM = "violent_storm"
    HURRICANE = "hurricane"


class UVIndexLevels(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"


class Pollutants(Enum):
    NO2 = "no2"
    SO2 = "so2"
    CO = "co"
    PM10 = "pm10"
    PM2_5 = "pm2_5"
    OZONE = "ozone"
