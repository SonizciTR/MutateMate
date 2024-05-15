import json

class BaseService:
    def __init__(self) -> None:
        pass

    def safe_get(self, data : json, keys : list):
        at_top = data.get(keys[0])
        if(len(keys) == 1): return at_top
        if(at_top == None): return at_top

        return self.safe_get(at_top, keys[1:])