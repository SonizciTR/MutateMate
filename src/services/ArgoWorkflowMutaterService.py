
import json

from services.BaseService import BaseService
from services.JsonBag import JsonBag
from services.KubeWrapperService import KubeWrapperService
from services.MutatingHelperService import MutatingHelperService


class ArgoWorkflowMutaterService(BaseService):
    def __init__(self) -> None:
        pass

    def mutate(self, data_req : JsonBag, kube_service : KubeWrapperService) -> json:
        pr_payload = []

        mwh_service = MutatingHelperService()
        #task_count = kube_service.get_notebook_task_count(data_req)
        kube_secrets, kube_cpu, kube_ram, kube_gpu = kube_service.get_notebook_secrets_and_resources(data_req)

        #Secret commands:
        for itm_key, itm_value in kube_secrets.items():
            if(self.is_env_exist(data_req, itm_key, itm_value)): continue
            pr_payload.append(mwh_service.add_secret_for_argo_workflow(itm_key, itm_value))
        
        #resource commands:
        tmp_specs = self.safe_get(data_req.raw, ["request", "object", "spec", "templates"])
        for indx, itm_spec in enumerate(tmp_specs):
            tmp_lmt = self.safe_get(itm_spec, ["container","resources"])
            
            if(tmp_lmt is None): continue

            pr_payload.append(mwh_service.replace_resource_for_argo_workflow(indx, kube_cpu, kube_ram, kube_gpu))
            
        return pr_payload
    
    def is_env_exist(self, data_req : JsonBag, env_key : str, env_value : str):
        tmp_specs = self.safe_get(data_req.raw, ["request", "object", "spec", "templates"])

        for itm_template in tmp_specs:
            tmp_envs = self.safe_get(itm_template, ["container", "env"])
            if(tmp_envs is None): continue

            for itm_env in tmp_envs:
                tmp_key  = itm_env.get("name")
                tmp_value = self.safe_get(itm_env, ["valueFrom","fieldRef","fieldPath"])
                if(tmp_key == env_key) and (tmp_value == env_value): return True

        return False