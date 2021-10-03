from config.configDTO import ConfigDTO

all_config = ConfigDTO("config/config.json")
CAMERA_INDEX = all_config.hardware_config.camera_index

#set_default_config
SPEED_UP_VAL = all_config.speed_config.speed_up_speed_val
SLOW_DOWN_VAL = all_config.speed_config.slow_down_speed_val
NORMAL_SPEED_VAL = all_config.speed_config.normal_speed_val
PAUSE_SPEED_VAL = all_config.speed_config.pause_speed_val

TIMEOUT = 150 