from datetime import datetime

def get_time_date():
    return datetime.now().strftime("%Y_%m_%d")

def get_time_hour_min():
    return datetime.now().strftime("%Y_%m_%d__%H_%M")

def get_time_full():
  return datetime.now().strftime("%Y_%m_%d__%H_%M_%S")

def get_time_for_log():
    return datetime.now()
