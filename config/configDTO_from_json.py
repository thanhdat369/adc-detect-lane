import json
from collections import namedtuple

from config.baseConfigDTO import BaseConfigDTO

class ComunicateConfig(BaseConfigDTO):
    def __init__(self, signalr_url,issue_api_url):
        self.signalr_url = signalr_url
        self.issue_api_url = issue_api_url


class DetectLaneConfig(BaseConfigDTO):
    def __init__(self, height_center_point, width_center_point, low_h, high_h,threshold_lane_px):
        self.height_center_point = height_center_point
        self.width_center_point = width_center_point
        self.low_h = low_h
        self.high_h = high_h
        self.threshold_lane_px = threshold_lane_px
        


class HardwareConfig(BaseConfigDTO):
    def __init__(self, camera_index, motor_port, servo_port, trigger_port, echo_port):
        self.camera_index = camera_index
        self.motor_port = motor_port
        self.servo_port = servo_port
        self.trigger_port = trigger_port
        self.echo_port = echo_port


class ServoConfig(BaseConfigDTO):
    def __init__(self, center_servo, range_value):
        self.center_servo = center_servo
        self.range_value = range_value
        self.max_left = center_servo + range_value
        self.max_right = center_servo - range_value


class SpeedConfig(BaseConfigDTO):
    def __init__(self, speed_up_speed_val, slow_down_speed_val, slow_down_speed_turn, normal_speed_val, pause_speed_val, backward_speed_val, motor_prepair_value):
        self.speed_up_speed_val = speed_up_speed_val
        self.slow_down_speed_val = slow_down_speed_val
        self.slow_down_speed_turn = slow_down_speed_turn
        self.normal_speed_val = normal_speed_val
        self.pause_speed_val = pause_speed_val
        self.backward_speed_val = backward_speed_val
        self.motor_prepair_value = motor_prepair_value

class AllConfig:
    def __init__(self, hardware_config, detect_lane_config, speed_config, servo_config, comunicate_config):
        self.hardware_config = hardware_config
        self.detect_lane_config = detect_lane_config
        self.speed_config = speed_config
        self.servo_config = servo_config
        self.comunicate_config = comunicate_config
    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)

    
