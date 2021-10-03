import json
from config.configDTO_from_json import *
class ConfigDTO:
    def __init__(self,json_file_path):
        self.__process_json_file()
        
    def __process_json_file(self,):
        with open('config/config.json','r') as f:
            all_config = AllConfig.from_json(f.read())
            self.hardware_config = HardwareConfig.from_dict(all_config.hardware_config)
            self.comunicate_config = ComunicateConfig.from_dict(all_config.comunicate_config)
            self.detect_lane_config = DetectLaneConfig.from_dict(all_config.detect_lane_config)
            self.servo_config = ServoConfig.from_dict(all_config.servo_config)
            self.speed_config = SpeedConfig.from_dict(all_config.speed_config)