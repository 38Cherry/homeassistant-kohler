from homeassistant.components.water_heater import (
    STATE_OFF,
    STATE_ON,
    SUPPORT_OPERATION_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    WaterHeaterEntity
)

from homeassistant.const import (
    ATTR_TEMPERATURE,
    TEMP_CELSIUS,
    PRECISION_WHOLE
)

from . import DATA_KOHLER, KohlerData

SUPPORT_FLAGS_HEATER = (
    SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE
)

SUPPORT_WATER_HEATER = [STATE_ON, STATE_OFF]


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Kohler platform."""
    data: KohlerData = hass.data[DATA_KOHLER]
    add_entities([KohlerWaterHeater(data)])


class KohlerWaterHeater(WaterHeaterEntity):
    """Representation of a Kohler Shower."""

    def __init__(self, data: KohlerData):
        """Initialize the shower device."""
        self._name = "Kohler Shower"
        self._data = data
        self._current_mode = None
        self._current_temperature = None
        self._target_temperature = None
        self._unit_of_measurement = data.unitOfMeasurement()

    def update(self):
        """Let HA know there has been an update from the Kohler API."""
        self._current_mode = STATE_ON if self._data.isShowerOn() else STATE_OFF
        self._current_temperature = self._data.getCurrentTemperature()
        self._target_temperature = self._data.getTargetTemperature()
        self._unit_of_measurement = self._data.unitOfMeasurement()

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._sensor.id
    
    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS_HEATER

    @property
    def name(self):
        """Return the name of the water_heater device."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    def set_temperature(self, **kwargs):
        """Set new target temperatures."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is not None:
            if self._current_mode == STATE_ON:
                self._data.turnOnShower(temp)
            else:
                self._data.setTargetTemperature(temp)
            self._target_temperature = temp

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return 30 if self._unit_of_measurement == TEMP_CELSIUS else 86

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return 45 if self._unit_of_measurement == TEMP_CELSIUS else 113

    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_WHOLE

    @property
    def current_operation(self):
        """Return current operation ie. on, off."""
        return self._current_mode

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return SUPPORT_WATER_HEATER

    def set_operation_mode(self, operation_mode):
        """Set operation mode."""
        if operation_mode == STATE_ON:
            self._data.turnOnShower(self._target_temperature)
        else:
            self._data.turnOffShower()

    @property
    def icon(self):
        """Get the icon to use in the front end."""
        return "mdi:shower"
