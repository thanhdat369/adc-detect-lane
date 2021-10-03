import json
from collections import namedtuple

class BaseConfigDTO:
    def __init__(self,):
        pass 

    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)

    @classmethod
    def from_dict(cls,dictionary):
        return cls(*namedtuple(cls.__name__,dictionary.keys())(*dictionary.values()))