"""MQTT interface of picture_frame."""

import logging
import time
import paho.mqtt.client as mqtt
import json
import os
from picframe import __version__


class InterfaceMQTT:
    """MQTT interface of picture_frame.
    
    This interface interacts via mqtt with the user to steer the image display.

    Attributes
    ----------
    controller : Controler 
        Controller for picture_frame
   

    Methods
    -------

    """

    def __init__(self, controller, mqtt_config):
        self.__logger = logging.getLogger("interface_mqtt.InterfaceMQTT")
        self.__logger.info('creating an instance of InterfaceMQTT')
        self.__controller = controller
        try:
            device_id = mqtt_config['device_id']
            self.__client = mqtt.Client(client_id = device_id, clean_session=True)
            login = mqtt_config['login']
            password = mqtt_config['password']
            self.__client.username_pw_set(login, password) 
            tls = mqtt_config['tls']
            if tls:
                self.__client.tls_set(tls)
            server = mqtt_config['server']
            port = mqtt_config['port']
            self.__client.connect(server, port, 60) 
            self.__client.will_set("homeassistant/switch/" + mqtt_config['device_id'] + "/available", "offline", qos=0, retain=True)
            self.__client.on_connect = self.on_connect
            self.__client.on_message = self.on_message
            self.__device_id = mqtt_config['device_id']
        except Exception as e:
            self.__logger.info("MQTT not set up because of: {}".format(e))
    
    def start(self):
        try:
            self.__controller.publish_state = self.publish_state
            self.__client.loop_start()
        except Exception as e:
            self.__logger.info("MQTT not started because of: {}".format(e))

    def stop(self):
        try:
            self.__controller.publish_state = None
            self.__client.loop_stop()
        except Exception as e:
            self.__logger.info("MQTT stopping failed because of: {}".format(e))


    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            self.__logger.warning("Can't connect with mqtt broker. Reason = {0}".format(rc))   
            return 
        self.__logger.info('Connected with mqtt broker')

        sensor_topic_head = "homeassistant/sensor/" + self.__device_id
        switch_topic_head = "homeassistant/switch/" + self.__device_id

        # send last will and testament
        available_topic = switch_topic_head + "/available"
        client.publish(available_topic, "online", qos=0, retain=True)

        # state_topic for all picframe sensors
        state_topic = sensor_topic_head + "/state"

        # send date_from sensor configuration 
        config_topic = sensor_topic_head + "_date_from/config"
        config_payload = '{"name":"' + self.__device_id + '_date_from", "icon":"mdi:calendar-arrow-left", "state_topic":"' + state_topic + '", "value_template": "{{ value_json.date_from}}", "avty_t":"' + available_topic + '",  "uniq_id":"' + self.__device_id + '_date_from", "dev":{"ids":["' + self.__device_id + '"]}}'
        client.publish(config_topic, config_payload, qos=0, retain=True)
        client.subscribe(self.__device_id + "/date_from", qos=0)

        # send date_to sensor configuration 
        config_topic = sensor_topic_head + "_date_to/config"
        config_payload = '{"name":"' + self.__device_id + '_date_to", "icon":"mdi:calendar-arrow-right", "state_topic":"' + state_topic + '", "value_template": "{{ value_json.date_to}}", "avty_t":"' + available_topic + '",  "uniq_id":"' + self.__device_id + '_date_to", "dev":{"ids":["' + self.__device_id + '"]}}'
        client.publish(config_topic, config_payload, qos=0, retain=True)
        client.subscribe(self.__device_id + "/date_to", qos=0)

        # send time_delay sensor configuration 
        config_topic = sensor_topic_head + "_time_delay/config"
        config_payload = '{"name":"' + self.__device_id + '_time_delay", "icon":"mdi:image-plus", "state_topic":"' + state_topic + '", "value_template": "{{ value_json.time_delay}}", "avty_t":"' + available_topic + '",  "uniq_id":"' + self.__device_id + '_time_delay", "dev":{"ids":["' + self.__device_id + '"]}}'
        client.publish(config_topic, config_payload, qos=0, retain=True)
        client.subscribe(self.__device_id + "/time_delay", qos=0)

        # send brightness sensor configuration 
        config_topic = sensor_topic_head + "_brightness/config"
        config_payload = '{"name":"' + self.__device_id + '_brightness", "icon":"mdi:image-plus", "state_topic":"' + state_topic + '", "value_template": "{{ value_json.brightness}}", "avty_t":"' + available_topic + '",  "uniq_id":"' + self.__device_id + '_brightness", "dev":{"ids":["' + self.__device_id + '"]}}'
        client.publish(config_topic, config_payload, qos=0, retain=True)
        client.subscribe(self.__device_id + "/brightness", qos=0)

        # send fade_time sensor configuration 
        config_topic = sensor_topic_head + "_fade_time/config"
        config_payload = '{"name":"' + self.__device_id + '_fade_time", "icon":"mdi:image-size-select-large", "state_topic":"' + state_topic + '", "value_template": "{{ value_json.fade_time}}", "avty_t":"' + available_topic + '",  "uniq_id":"' + self.__device_id + '_fade_time", "dev":{"ids":["' + self.__device_id + '"]}}'
        client.publish(config_topic, config_payload, qos=0, retain=True)
        client.subscribe(self.__device_id + "/fade_time", qos=0)

        # send image counter sensor configuration 
        config_topic = sensor_topic_head + "_image_counter/config"
        config_payload = '{"name":"' + self.__device_id + '_image_counter", "icon":"mdi:camera-burst", "state_topic":"' + state_topic + '", "value_template": "{{ value_json.image_counter}}", "avty_t":"' + available_topic + '",  "uniq_id":"' + self.__device_id + '_ic", "dev":{"ids":["' + self.__device_id + '"]}}'
        client.publish(config_topic, config_payload, qos=0, retain=True)

        # send  image sensor configuration
        config_topic = sensor_topic_head + "_image/config"
        attributes_topic = sensor_topic_head + "_image/attributes"
        config_payload = '{"name":"' + self.__device_id + '_image", "icon":"mdi:file-image", "state_topic":"' + state_topic + '",  "value_template": "{{ value_json.image}}", "json_attributes_topic":"' + attributes_topic + '","avty_t":"' + available_topic + '",  "uniq_id":"' + self.__device_id + '_fn", "dev":{"ids":["' + self.__device_id + '"]}}'
        client.publish(config_topic, config_payload, qos=0, retain=True)

        # send  directory sensor configuration
        config_topic = sensor_topic_head + "_dir/config"
        attributes_topic = sensor_topic_head + "_dir/attributes"
        config_payload = '{"name":"' + self.__device_id + '_dir", "icon":"mdi:folder-multiple-image", "state_topic":"' + state_topic + '",  "value_template": "{{ value_json.dir}}", "json_attributes_topic":"' + attributes_topic + '","avty_t":"' + available_topic + '",  "uniq_id":"' + self.__device_id + '_dir", "dev":{"ids":["' + self.__device_id + '"]}}'
        client.publish(config_topic, config_payload, qos=0, retain=True)
        client.subscribe(self.__device_id + "/subdirectory", qos=0)

        self.__setup_switch(client, switch_topic_head, self.__device_id, "_text_refresh", "mdi:image-plus", available_topic)
        self.__setup_switch(client, switch_topic_head, self.__device_id, "_delete", "mdi:image-minus", available_topic)
        self.__setup_switch(client, switch_topic_head, self.__device_id, "_name_toggle", "mdi:image-plus", available_topic,
                            self.__controller.text_is_on("name"))
        self.__setup_switch(client, switch_topic_head, self.__device_id, "_date_toggle", "mdi:image-plus", available_topic,
                            self.__controller.text_is_on("date"))
        self.__setup_switch(client, switch_topic_head, self.__device_id, "_location_toggle", "mdi:image-plus", available_topic,
                            self.__controller.text_is_on("location"))
        self.__setup_switch(client, switch_topic_head, self.__device_id, "_directory_toggle", "mdi:image-plus", available_topic,
                            self.__controller.text_is_on("directory"))
        self.__setup_switch(client, switch_topic_head, self.__device_id, "_text_off", "mdi:image-plus", available_topic)
        self.__setup_switch(client, switch_topic_head, self.__device_id, "_display", "mdi:panorama", available_topic,
                            self.__controller.display_is_on)
        self.__setup_switch(client, switch_topic_head, self.__device_id, "_shuffle", "mdi:shuffle-variant", available_topic,
                            self.__controller.shuffle)
        self.__setup_switch(client, switch_topic_head, self.__device_id, "_paused", "mdi:pause", available_topic,
                            self.paused)
        self.__setup_switch(client, switch_topic_head, self.__device_id, "_back", "mdi:skip-previous", available_topic)
        self.__setup_switch(client, switch_topic_head, self.__device_id, "_next", "mdi:skip-next", available_topic)

    def __setup_switch(self, client, switch_topic_head, topic, icon,
                       available_topic, is_on=False):
        config_topic = switch_topic_head + topic + "/config"
        command_topic = switch_topic_head + topic + "/set"
        state_topic = switch_topic_head + topic + "/state"
        config_payload = json.dumps({"name": self.__device_id + "_next",
                                     "icon": icon,
                                     "command_topic": command_topic,
                                     "state_topic": state_topic,
                                     "avty_t": available_topic,
                                     "uniq_id": self.__device_id + topic,
                                     "dev": {"ids": [self.__device_id]}})
        client.subscribe(command_topic , qos=0)
        client.publish(config_topic, config_payload, qos=0, retain=True)
        client.publish(state_topic, "ON" if is_on else "OFF", qos=0, retain=True)

    def on_message(self, client, userdata, message):
        msg = message.payload.decode("utf-8") 
        switch_topic_head = "homeassistant/switch/" + self.__device_id
       
        ###### switches ######
        # display
        if message.topic == switch_topic_head + "_display/set":
            state_topic = switch_topic_head + "_display/state"
            if msg == "ON":
                self.__controller.display_is_on = True
                client.publish(state_topic, "ON", retain=True)
            elif msg == "OFF":
                self.__controller.display_is_on = False
                client.publish(state_topic, "OFF", retain=True)
        # shuffle
        elif message.topic == switch_topic_head + "_shuffle/set":
            state_topic = switch_topic_head + "_shuffle/state"
            if msg == "ON":
                self.__controller.shuffle = True
                client.publish(state_topic, "ON", retain=True)
            elif msg == "OFF":
                self.__controller.shuffle = False
                client.publish(state_topic, "OFF", retain=True)
        # paused
        elif message.topic == switch_topic_head + "_paused/set":
            state_topic = switch_topic_head + "_paused/state"
            if msg == "ON":
                self.__controller.paused = True
                client.publish(state_topic, "ON", retain=True)
            elif msg == "OFF":
                self.__controller.paused = False
                client.publish(state_topic, "OFF", retain=True)
        # back buttons
        elif message.topic == switch_topic_head + "_back/set":
            state_topic = switch_topic_head + "_back/state"
            if msg == "ON":
                client.publish(state_topic, "OFF", retain=True)
                self.__controller.back()
        # next buttons
        elif message.topic == switch_topic_head + "_next/set":
            state_topic = switch_topic_head + "_next/state"
            if msg == "ON":
                client.publish(state_topic, "OFF", retain=True)
                self.__controller.next()
        # delete
        elif message.topic == switch_topic_head + "_delete/set":
            state_topic = switch_topic_head + "_delete/state"
            if msg == "ON":
                client.publish(state_topic, "OFF", retain=True)
                self.__controller.delete()
        # name toggle
        elif message.topic == switch_topic_head + "_name_toggle/set":
            state_topic = switch_topic_head + "_name_toggle/state"
            if msg in ("ON", "OFF"):
                self.__controller.set_show_text("name", msg)
                client.publish(state_topic, "OFF" if msg == "ON" else "ON", retain=True)
        # date_on
        elif message.topic == switch_topic_head + "_date_toggle/set":
            state_topic = switch_topic_head + "_date_toggle/state"
            if msg in ("ON", "OFF"):
                self.__controller.set_show_text("date", msg)
                client.publish(state_topic, msg, retain=True)
        # location_on
        elif message.topic == switch_topic_head + "_location_toggle/set":
            state_topic = switch_topic_head + "_location_toggle/state"
            if msg in ("ON", "OFF"):
                self.__controller.set_show_text("location", msg)
                client.publish(state_topic, msg, retain=True)
        # directory_on
        elif message.topic == switch_topic_head + "_directory_toggle/set":
            state_topic = switch_topic_head + "_directory_toggle/state"
            if msg in ("ON", "OFF"):
                self.__controller.set_show_text("directory", msg)
                client.publish(state_topic, msg, retain=True)
        # text_off
        elif message.topic == switch_topic_head + "_text_off/set":
            state_topic = switch_topic_head + "_text_off/state"
            if msg == "ON":
                self.__controller.set_show_text()
                client.publish(state_topic, "OFF", retain=True)
        # text_refresh
        elif message.topic == switch_topic_head + "_text_refresh/set":
            state_topic = switch_topic_head + "_text_refresh/state"
            if msg == "ON":
                client.publish(state_topic, "OFF", retain=True)
                self.__controller.refresh_show_text()

        ##### values ########
        # change subdirectory
        elif message.topic == self.__device_id + "/subdirectory":
            self.__logger.info("Recieved subdirectory: %s", msg)
            self.__controller.subdirectory = msg
        # date_from
        elif message.topic == self.__device_id + "/date_from":
            self.__logger.info("Recieved date_from: %s", msg)
            self.__controller.date_from = msg
        # date_to
        elif message.topic == self.__device_id + "/date_to":
            self.__logger.info("Recieved date_to: %s", msg)
            self.__controller.date_to = msg
        # fade_time
        elif message.topic == self.__device_id + "/fade_time":
            self.__logger.info("Recieved fade_time: %s", msg)
            self.__controller.fade_time = float(msg)
        # time_delay
        elif message.topic == self.__device_id + "/time_delay":
            self.__logger.info("Recieved time_delay: %s", msg)
            self.__controller.time_delay = float(msg)
        # brightness
        elif message.topic == self.__device_id + "/brightness":
            self.__logger.info("Recieved brightness: %s", msg)
            self.__viewer.set_brightness(float(msg))


    def publish_state(self, image, image_attr):
        topic_head =  "homeassistant/sensor/" + self.__device_id
        switch_topic_head = "homeassistant/switch/" + self.__device_id
        state_topic = topic_head + "/state"
        state_payload = {}
        # directory sensor
        actual_dir, dir_list = self.__controller.get_directory_list()
        state_payload["dir"] = actual_dir
        dir_attr = {}
        dir_attr['directories'] = dir_list
        # image counter sensor
        state_payload["image_counter"] = str(self.__controller.get_number_of_files()) 
        # image sensor
        _, tail = os.path.split(image)
        state_payload["image"] = tail
        # date_from
        state_payload["date_from"] = int(self.__controller.date_from)
        # date_to
        state_payload["date_to"] = int(self.__controller.date_to)
        # time_delay
        state_payload["time_delay"] = self.__controller.time_delay
        # fade_time
        state_payload["fade_time"] = self.__controller.fade_time

        # send last will and testament
        available_topic = switch_topic_head + "/available"
        self.__client.publish(available_topic, "online", qos=0, retain=True)

        #pulish sensors
        attributes_topic = topic_head + "_image/attributes"
        self.__client.publish(attributes_topic, json.dumps(image_attr), qos=0, retain=False)
        attributes_topic = topic_head + "_dir/attributes"
        self.__client.publish(attributes_topic, json.dumps(dir_attr), qos=0, retain=False)
        self.__logger.info("Send state: %s", state_payload)
        self.__client.publish(state_topic, json.dumps(state_payload), qos=0, retain=False)