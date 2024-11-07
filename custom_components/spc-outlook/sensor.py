"""Platform for sensor integration."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

import requests
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from shapely.geometry import Point, shape

DAYS_WITH_DETAILED_OUTLOOKS = 3

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities([ExampleSensor()])


class ExampleSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Example Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def update(self) -> None:
        """
        Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = 23

def getspcoutlook() -> dict[str, int]:
    """Query SPC for latest severe weather outlooks."""
    output = {}
    location = Point(-83, 42) # add your lon lat here
    for day in range(1, 4):
        url = "https://www.spc.noaa.gov/products/outlook/day" + \
            str(day) + "otlk_cat.lyr.geojson"
        result = False
        resp = requests.get(url=url, timeout=10)
        data = resp.json()
        for feature in data["features"]:
            polygon = shape(feature["geometry"])
            if polygon.contains(location):
                output["cat_day"+str(day)] = feature["properties"]["LABEL2"]
                result = True
        if result and day < DAYS_WITH_DETAILED_OUTLOOKS:
            torn_url = "https://www.spc.noaa.gov/products/outlook/day" + \
                str(day)+ "otlk_torn.lyr.geojson"
            resp = requests.get(url=torn_url, timeout=10)
            data = resp.json()
            for feature in data["features"]:
                polygon = shape(feature["geometry"])
                if polygon.contains(location):
                    output["torn_day"+str(day)] = feature["properties"]["LABEL2"]
            hail_url = "https://www.spc.noaa.gov/products/outlook/day"+str(day)+\
                "otlk_hail.lyr.geojson"
            resp = requests.get(url=hail_url, timeout=10)
            data = resp.json()
            for feature in data["features"]:
                polygon = shape(feature["geometry"])
                if polygon.contains(location):
                    output["hail_day"+str(day)] = feature["properties"]["LABEL2"]
            wind_url = "https://www.spc.noaa.gov/products/outlook/day"+str(day)+\
                "otlk_wind.lyr.geojson"
            resp = requests.get(url=wind_url, timeout=10)
            data = resp.json()
            for feature in data["features"]:
                polygon = shape(feature["geometry"])
                if polygon.contains(location):
                    output["wind_day"+str(day)] = feature["properties"]["LABEL2"]
    return output
