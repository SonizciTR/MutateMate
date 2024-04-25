
import collections
import json

from services.JsonBag import JsonBag
from services.KubeWrapperService import KubeWrapperService
from services.MutatingHelperService import MutatingHelperService


class NotebookMutaterService:
    def __init__(self) -> None:
        pass

    def mutate(self, request_data : JsonBag, kube_service : KubeWrapperService, secret_namespace : str) -> list:
        hashtags = kube_service.get_hashtags_from_description(request_data.workbench_description)
        secrets_targeted = kube_service.get_all_secrets_by_filter(secret_namespace, hashtags)

        if(len(secrets_targeted) == 0): return []
        
        mwh_service = MutatingHelperService()
        nb_payload = []
        
        for itm_key, itm_value in secrets_targeted.items():
            #Auto shutdown notebook trigger continously send update request. So every time this part adds same key values. To stop this I added these:
            tmp_rslt = self.is_key_already_exist(request_data.raw, itm_key)
            if(tmp_rslt): 
                print(f"This key already exist => [{itm_key}]. Replacing it.")
                nb_payload.append(mwh_service.replace_secret_for_notebook(itm_key, itm_value))
            else:
                nb_payload.append(mwh_service.add_secret_for_notebook(itm_key, itm_value))
            #
            

        return nb_payload
    
    def is_key_already_exist(self, request_whole_data: json, key_looking : str)-> bool: 
        tmp_array = self.safe_get(request_whole_data, ["request", "object", "spec", "template", "spec", "containers"])
        
        if(tmp_array is None): return False
        
        if(not isinstance(tmp_array, collections.abc.Sequence)): return False
        
        tmp_first = tmp_array[0]
        tmp_envs_lst = tmp_first.get("env")

        if(not isinstance(tmp_envs_lst, collections.abc.Sequence) or len(tmp_envs_lst) == 0): return False
        
        for itm_env in tmp_envs_lst:
            tmp_val_key = itm_env.get("name", None)
            tmp_val_value = itm_env.get("value", None)

            if(tmp_val_key == key_looking): return True
                
        return False
    
    def safe_get(self, data : json, keys : list):
        at_top = data.get(keys[0])
        if(len(keys) == 1): return at_top
        if(at_top == None): return at_top

        return self.safe_get(at_top, keys[1:])
    
    