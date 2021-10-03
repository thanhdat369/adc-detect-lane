# from comunicate.get_uuid import get_uuid
from communicate.download_ultils import check_version, download_config, download_model, write_new_version_into_file
from communicate.communicate_ultils import get_uuid
from communicate.deviceDTO import DeviceDTO
import logging
import time
import timeit
from signalrcore.hub_connection_builder import HubConnectionBuilder

from communicate.mock_session import MockSession

class SignalR:
    def __init__(self,signalR_url):
        self.stopSignal = True
        # self.UUID = "5F-1A-F3-D8-E0-90"
        self.UUID = "dcaad2fd544f"
        # self.UUID = "CD-71-2E-88-10-F2"
        # self.UUID = get_uuid().strip()
        print(self.UUID)
        handler = logging.StreamHandler()
        handler.setLevel(logging.ERROR)
        self.hub_connection = HubConnectionBuilder().with_url(signalR_url,options={
                    }).configure_logging(logging.ERROR, socket_trace=True, handler=handler).with_automatic_reconnect({
                    "type": "interval",
                    "keep_alive_interval": 10,
                    "intervals": [1, 3, 5, 6, 7, 87, 3]
                }).build()
        self.__set_up_handle_func()
        self.hub_connection.start()
        time.sleep(0.5)
        

    def connect(self,):
        self.hub_connection.send("ConnectCar",[self.UUID])
        print(self.UUID)
        time.sleep(1)

    def stop(self,):
        self.hub_connection.stop()

    def changeStopSignal(self,isStop):
        print("Change")
        self.stopSignal = isStop

    def __set_up_handle_func(self,):
        self.hub_connection.on_open(lambda: print("connection opened and handshake received ready to send messages"))
        self.hub_connection.on_close(lambda: print("connection closed"))
        self.hub_connection.on_error(exit)
        self.hub_connection.on("WhenCarConnectedReturn", self.__handle_received_message_connected)
        self.hub_connection.on("WhenCarStart", self.__handle_received_message_start)
        self.hub_connection.on("WhenCarStop", self.__handle_received_message_stop)

    

    def __handle_received_message_connected(self,data):
        print("-----received message connected-------")
        #TODO
        #HANDLE MODEL CONFIG URL
        if(data[0] is None):
            # raise Exception("No data")
            print("No data, car have not register")
        else:
            MockSession.deviceDTO = DeviceDTO.from_dict(data[0])
            print(MockSession.deviceDTO)
            # download_config(MockSession.deviceDTO.configUrl)
            if check_version(MockSession.deviceDTO.modelId):
                print("newest version")
            else:
                print("update model")
                # write_new_version_into_file(MockSession.deviceDTO.modelId)
                # download_model(MockSession.deviceDTO.modelUrl)
                # time.sleep(0.5)
            

    def __handle_received_message_start(self,data):
        print("-----START-------")
        print('received: ', data)
        if(data is not None):
            id = str(data[0]).strip()
            if id == self.UUID.strip():
                print("Prepair to run")
                # startBySignalR = True
                # Co the viet mot ham phu de thay the cho global
                self.changeStopSignal(False)
                self.hub_connection.send("RunningCar",[self.UUID])

    def __handle_received_message_stop(self,data):
        print("-----STOP-------")
        #CHECK DATA == UUID
        if(data is not None):
            id = str(data[0]).strip()
            if id == self.UUID.strip():
                print("Prepair to run")
                self.changeStopSignal(True)
        self.hub_connection.send("StoppingCar",[self.UUID])



# signalR = SignalR('https://avc-api.azurewebsites.net/hub')

# signalR.start()
# stopBySignalR = True
# start_time = timeit.default_timer()

# while stopBySignalR:
#     stopBySignalR = signalR.stopSignal
#     print("Wating .",end = '\r')
#     if(timeit.default_timer()-start_time>10):
#         print("time out")
#         break
# print("EXIT")