"""
Example of a custom MQTT component.

Shows how to communicate with MQTT. Follows a topic on MQTT and updates the
state of an entity to the last message received on that topic.

Also offers a service 'set_state' that will publish a message on the topic that
will be passed via MQTT to our message received listener. Call the service with
example payload {"new_state": "some new state"}.

Configuration:

To use the mqtt_example component you will need to add the following to your
configuration.yaml file.

mqtt_ESPRTU:
  topic: "home-assistant/mqtt_example"
"""
from __future__ import annotations

import voluptuous as vol
import logging
import json
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

# The domain of your component. Should be equal to the name of your component.
DOMAIN = "mqtt_ESPRTU"

CONF_TOPIC = 'topic'
DEFAULT_TOPIC = 'home-assistant/mqtt_example'

CONF_NAME = 'name'
DEFAULT_NAME = 'espMqttDev0'

_LOGGER = logging.getLogger(__name__)

# Schema to validate the configured MQTT topic
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_TOPIC, default=DEFAULT_TOPIC): mqtt.valid_subscribe_topic,
                #vol.Optional(CONF_NAME, default=DEFAULT_NAME) : str
            })
    },
    extra=vol.ALLOW_EXTRA,
)


#def setSensor(hass, sens_name, friendly_name, value)
def setSensor(hass_instance,sens_name,friendly_name,value,is_measurement,device_class,unit_of_measurement,icon):
    if (hass_instance is None) or (sens_name is None):
        return;
    if value is None:
        value = "No data"

    if icon is None:
        icon = 'mdi:battery-outline'

    attributes= {
        'icon': icon,
    }
    attributes['friendly_name']= friendly_name
    if is_measurement:
        attributes['state_class']='measurement'
    if unit_of_measurement is not None:
        attributes['unit_of_measurement']= unit_of_measurement
    if device_class is not None:
        attributes['device_class']= device_class

    hass_instance.states.set( sens_name, value, attributes )

def update_mqttGPS_location(hass, latitude, longitude):
    hass.states.set(
            'zone.RTU0', 0,
            {
                'longitude': longitude,
                'latitude': latitude,
                'radius' : 250,
                'icon': 'mdi:archive',
                'passive' : 'false',
                'friendly_name': 'hive 1',
            })

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the MQTT example component."""
    topic = config[DOMAIN][CONF_TOPIC]
    
   
   # entity_id = 'mqtt_ESPRTU.last_message' # TODO: config this from .yaml
    entity_id = 'testsens.test_tag' # TODO: config this from .yaml

    plaussible_tags = [ 
        ("msg_id",      "Mqtt msg ID",      False,  None,       None,   'mdi:counter'),
        ("v_bat",       "Battery voltage",  True,   "voltage",  "V",    'mdi:battery-outline'),
        ("v_solar",     "Solar voltage",    True,   "voltage",  "V",    'mdi:solar-power'),
        ("con_type",    "Connection type",  False,  None,       None,   'mdi:satellite-uplink'),
        ("latitude",    "Sens. latitude",   False,  None,       None,   'mdi:archive-marker'),
        ("longitude",   "Sens. longitude",  False,  None,       None,   'mdi:archive-marker'),
        ("gps_accuracy","GPS accuracy",     False,  None,       "m",    'mdi:archive-marker'),
        ("masl", "Metres above sea level",  False,  None,       "m",    'mdi:archive-marker'),
        ("sat_no", "Satelites visible",     False,  None,       None,   'mdi:satellite-variant'),
        ("cn0", "GNSS signal strength",     False,  None,       "dBHz", 'mdi:satellite-variant'),
        ("rssi", "GSM signal strength",     False,  None,       "dBm",  'mdi:satellite-uplink')
         ]
    # Listen to a message on MQTT.
    def message_received(topic: str, payload: str, qos: int) -> None:
        """A new MQTT message has been received."""
        mqttData = json.loads(payload)

        for tag in plaussible_tags:
            if tag[0] in mqttData:
                setSensor(
                    hass_instance = hass,
                    sens_name = ("HUB_RTU0." + str(tag[0])),
                    friendly_name = tag[1],
                    value = mqttData[tag[0]],
                    is_measurement = tag[2],
                    device_class = tag[3],
                    unit_of_measurement = tag[4],
                    icon = str(tag[5])
                )
                #setSensor(hass,"HUB","RTU0",tag[0], mqttData[tag[0]], tag[2], tag[1])

                #setSensor(hass, "HUB_RTU0." + str(tag[0]), mqttData[tag[0]], )

        if ("latitude" in mqttData) and ("longitude" in mqttData):
            update_mqttGPS_location(hass, mqttData['latitude'], mqttData['longitude'])
        #if 'BAT_V' in mqttData:
        #    setSensor(hass,"HUB","RTU0","T0", mqttData['BAT_V'], "Sens T0")
        hass.states.set(entity_id, payload)
        #hass.states.set('mqtt_ESPRTU.number', 10)

    hass.components.mqtt.subscribe(topic, message_received) # should be async?

    #name = config[DOMAIN][CONF_NAME]
    hass.states.set(entity_id, 'No messages')

    for tag in plaussible_tags:
        #setSensor(hass,"HUB","RTU0",tag[0], "No data", tag[2], tag[1])
        setSensor(
                    hass_instance = hass,
                    sens_name = ("HUB_RTU0." + str(tag[0])),
                    friendly_name = str(tag[1]),
                    value = "No data",
                    is_measurement = tag[2],
                    device_class = str(tag[3]),
                    unit_of_measurement = str(tag[4]),
                    icon = str(tag[5])
                )

   

    # temperature sensor
    #'''hass.states.set(
    #        'mqtt_ESPRTU.temperatureESP', 21,
    #        {
    #            'state_class': 'measurement',
    #            'unit_of_measurement': '°C',
    #            'device_class': 'temperature',
    #            'friendly_name': 'Example Temperature',
    #            'icon': 'mdi:thermometer',
    #            #'state_color': True
    #        })'''
    #Temp_sensor("mqtt_ESPRTU.temperatureESP", 21)

    # humidity sensor
    #hass.states.set(
    #        'mqtt_ESPRTU.humidityESP', 88,
    #        {
    #            'state_class': 'measurement',
    #            'unit_of_measurement': '%',
    #            'device_class': 'humidity',
    #            'friendly_name': 'humidity test',
    #            'icon': 'mdi:water-percent'
    #        })
    
    # gps sensor
    #hass.states.set(
    #        'mqtt_ESPRTU_zone.RTU0', 0,
    #        {
    #            'longitude': 19.6355585,
    #            'latitude': 46.1034267,
    #            'radius' : 250,
    #            'icon': 'mdi:archive',
    #            'passive' : 'false',
    #            'friendly_name': 'hive 1',
    #        })

    # Service to publish a message on MQTT.
    #def set_state_service(call: ServiceCall) -> None:
      # """Service to send a message."""
     #   hass.components.mqtt.publish(topic, call.data.get('new_state'))

    # Register our service with Home Assistant.
    #hass.services.register(DOMAIN, 'set_state', set_state_service)

    # Return boolean to indicate that initialization was successfully.
    return True


