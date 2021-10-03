from collections import namedtuple
class DeviceDTO:
    def __init__(self, id, deviceId, configUrl, modelId, modelUrl):
        self.id = id
        self.deviceId = deviceId
        self.configUrl = configUrl
        self.modelId = modelId
        self.modelUrl = modelUrl
    
    def __str__(self):
        return f'{self.id} , {self.deviceId},modelID {self.modelId}'

    @classmethod
    def from_dict(cls,dictionary):
        return cls(*namedtuple(cls.__name__,dictionary.keys())(*dictionary.values()))