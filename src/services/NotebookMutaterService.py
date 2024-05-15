
import collections
import json

from services.BaseService import BaseService
from services.JsonBag import JsonBag
from services.KubeWrapperService import KubeWrapperService
from services.MutatingHelperService import MutatingHelperService


class NotebookMutaterService(BaseService):
    def __init__(self) -> None:
        pass

    def mutate(self, request_data : JsonBag, kube_service : KubeWrapperService, secret_namespace : str) -> list:
        nb_payload = []
        mwh_service = MutatingHelperService()

        hashtags = kube_service.get_hashtags_from_description(request_data.workbench_description)
        secrets_targeted = kube_service.get_all_secrets_by_filter(secret_namespace, hashtags)

        # #if there is already added value but removed the we should remove them:
        # existing_envs = self.get_all_env_keys(request_data.raw)
        # for itm_exs_key, itm_exs_value in existing_envs.items():
        #     if(itm_exs_key in secrets_targeted):
        #         continue
        #     nb_payload.append(mwh_service.remove_secret_for_notebook(itm_exs_key, itm_exs_value))
        # #

        if(len(secrets_targeted) == 0): return []
        
        for itm_key, itm_value in secrets_targeted.items():
            #Auto shutdown notebook trigger continously send update request. So every time this part adds same key values. To stop this I added these:
            tmp_rslt = self.is_key_already_exist(request_data.raw, itm_key)
            if(tmp_rslt): 
                #Replace not working:
                #print(f"This key already exist => [{itm_key}]. Replacing it.")
                #nb_payload.append(mwh_service.replace_secret_for_notebook(itm_key, itm_value))
                
                print(f"This key already exist => [{itm_key}]. Not adding.")
                continue
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
    
    def get_all_env_keys(self, request_whole_data: json) -> dict:
        tmp_array = self.safe_get(request_whole_data, ["request", "object", "spec", "template", "spec", "containers"])
        
        if(tmp_array is None): return None
        
        if(not isinstance(tmp_array, collections.abc.Sequence)): return None
        
        tmp_first = tmp_array[0]
        tmp_envs_lst = tmp_first.get("env")

        if(not isinstance(tmp_envs_lst, collections.abc.Sequence) or len(tmp_envs_lst) == 0): return None
        
        all_envs = { }
        for itm_env in tmp_envs_lst:
            tmp_val_key = itm_env.get("name", None)
            tmp_val_value = itm_env.get("value", None)
            
            if(tmp_val_key is None): continue
            
            all_envs[tmp_val_key] = tmp_val_value

        return all_envs
    
    
    
    