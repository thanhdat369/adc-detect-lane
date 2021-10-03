class CarStateDTO:
    def __init__(self,motor_value=0,servo_value=0):
        self.motor_value = motor_value
        self.servo_value = servo_value
    
    def set_motor_value(self,motor_value):
        self.motor_value = motor_value
    
    def set_servo_value(self,servo_value):
        self.servo_value = servo_value
    
    def get_motor_value(self,):
        return self.motor_value
    
    def get_servo_value(self,):
        return self.servo_value

    def getState(self,):
        return self.motor_value,self.servo_value

