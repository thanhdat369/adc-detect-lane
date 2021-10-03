import time
import RPi.GPIO as GPIO
import argparse


class Distance_Ultrasonic:
    def __init__(self,trigger_pin,echo_pin):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.__initialize_gpio()
        self.__initialize_sensor()
        self.temperature = 20
        self.speed_of_sound = 33100 + (0.6 * self.temperature)

        print("Ultrasonic Measurement")
        print("Speed of sound is", self.speed_of_sound/100, "m/s at ",self.temperature, "degrees celsius")
        
    def __initialize_gpio(self,):
        """
        This function sets up the GPIO pins on the Raspberry Pi
        that are connected to the trigger and echo pins on the
        sensor.
        """
        # set GPIO mode to GPIO references rather than pin numbers
        GPIO.setmode(GPIO.BCM)
        # Set pins as output and input
        GPIO.setup(self.trigger_pin, GPIO.OUT)  # Trigger
        GPIO.setup(self.echo_pin, GPIO.IN)      # Echo

    def __initialize_sensor(self,):
        """
        This function initializes the ultrasonic distance
        sensor.
        """
        # Set trigger to False (Low)
        GPIO.output(self.trigger_pin, False)
        # Allow module to settle
        time.sleep(0.5)

    def take_sensor_measurement(self,):

        """
        This function returns the elapsed time between
        the pulse and the echo.
        """

        # Send 10us pulse to trigger
        GPIO.output(self.trigger_pin, True)

        # Wait 10us
        time.sleep(0.00001)

        # Stop pulse
        GPIO.output(self.trigger_pin, False)

        start_time = time.time()

        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()

        while GPIO.input(self.echo_pin) == 1:
            stop_time = time.time()

        # Calculate pulse length
        elapsed_time = stop_time - start_time

        return elapsed_time


    def get_average_measurement(self, num_measurements,delay):
        """
        This function returns the average measurement of distance from the
        specified number of measurements.
        """

        measurement = 0.0
        for n in range(num_measurements):
            measurement += self.take_sensor_measurement()
            time.sleep(delay)
        average_measurement = measurement / num_measurements
        return average_measurement

    def stop(self):
        GPIO.cleanup()
    def get_distance(self,measurements,time_between_indiv_measurements,time_between_avg_measurements):
        """
        This function monitors the ultrasonic distance sensor and displays
        the measurements on the console.
        # Cach su dung
        # number of measurements for averaging
        # individual delay in seconds between taking individual thoi gian nay moi lan do trung binh (rep)
        # averaged la thoi gian nghi giua moi hiep (set)
        # monitor_ultrasonic_sensor(GPIO_TRIGGER,GPIO_ECHO,measurements,individual,averaged)
        """

        # Calculate the speed of sound in cm/s at room temperature.
        distance = - 1

        try:
            elapsed = self.get_average_measurement(measurements, time_between_indiv_measurements)
            # Distance pulse travelled in that time is time multiplied by the
            # speed of sound (cm/s).
            distance = elapsed * self.speed_of_sound
            # RETURN DISTANCE AT THIS
            # That was the distance there and back so halve the value.
            distance = distance / 2
            time.sleep(time_between_avg_measurements)
            return distance
        except KeyboardInterrupt:
            # User pressed CTRL-C.
            print("\nKeyboard Interrupt!")
            # Reset GPIO settings.
            GPIO.cleanup()
        except Exception as e:
            # User pressed CTRL-C.
            print("ERROR", e)
            # Reset GPIO settings.
            GPIO.cleanup()