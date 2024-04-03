
import json


class MutatingHelperService:
    def __init__(self) -> None:
        pass

    def add_secret_for_notebook(self, key_name : str, real_value : str):
        return {"op": "add", "path": "/spec/template/spec/containers/0/env/-", "value": {"name": key_name, "value": real_value}}
    
    def add_secret_for_pipeline(self, task_index : int, key_name : str, real_value : str):
        return {"op": "add", "path": f"/spec/pipelineSpec/tasks/{task_index}/taskSpec/steps/0/env/-", "value": {"name": key_name, "value": real_value}}
    
    def add_resource_for_pipeline(self, task_index : int, cpu_limit : str, ram_limit : str, gpu_limit : str) -> []:
        payload = []
        #this is for real thing we want:
        payload.append(
        {
            "op": "add", "path": f"/spec/pipelineSpec/tasks/{task_index}/taskSpec/steps/0/computeResources" , 
                "value": { "limits": { "nvidia.com/gpu": gpu_limit, "cpu": cpu_limit, "memory": ram_limit }
            }
        })

        #this thing is a workaround. We don't want to assing request but it is default setting
        min_gpu = gpu_limit
        if( int(min_gpu) > 0): min_gpu = 1
        payload.append(
        {
            "op": "add", "path": f"/spec/pipelineSpec/tasks/{task_index}/taskSpec/steps/0/computeResources" , 
                "value": { "requests": { "nvidia.com/gpu": min_gpu, "cpu": "1m", "memory": "1Mi" }
            }
        }) 

        return payload
    
    def add_our_label(self, old_labels : dict):
        #[{"op": "add", "path": "/metadata/labels", "value": {"thy.editedby": "MutateMate" }}]

        pay_lbl = []

        for itm_key, itm_value in old_labels.items():
            pay_lbl.append({"op": "add", "path": "/metadata/labels", "value": {itm_key: itm_value }})
        
        pay_lbl.append({"op": "add", "path": "/metadata/labels", "value": {"thy.editedby": "MutateMate" }})
        return pay_lbl