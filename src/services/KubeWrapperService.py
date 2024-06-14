import re
import base64
from kubernetes import client, config

from services.JsonBag import JsonBag

class KubeWrapperService:
    def __init__(self, kube_base_url : str, kube_access_token : str) -> None:
        self.base_url = kube_base_url
        self.access_token = kube_access_token
        
        self.set_client(kube_base_url, kube_access_token)
        
        pass

    def set_client(self, kube_url, access_token):
        if (kube_url is not None) and (len(kube_url) > 0):
            configuration = client.Configuration()
            configuration.api_key["authorization"] = access_token
            configuration.api_key_prefix['authorization'] = 'Bearer'
            configuration.host = kube_url
            configuration.verify_ssl = False

            self.custom_api = client.CustomObjectsApi(client.ApiClient(configuration))
            self.core_api =  client.CoreV1Api(client.ApiClient(configuration))
        else:
            config.load_incluster_config()

            self.core_api =  client.CoreV1Api()
            self.custom_api = client.CustomObjectsApi()
        
        pass

    # CPU, RAM, GPU all values related part:
    
    def get_cpu_value(self) -> str:
        return "1"

    def get_ram_value(self) -> str:
        return "1G"

    def get_gpu_value(self) -> str:
        return "1"

    def get_all_resources(self) -> str:
        return self.get_cpu_value(), self.get_ram_value(), self.get_gpu_value()
    
    ### Notebook Info Retreival =>

    def get_notebook_task_count(self, request_data : JsonBag):
        tmp_obj =  request_data.raw["request"]["object"]
        tmp_tasks = tmp_obj.get("spec").get("pipelineSpec").get("tasks")
        
        if(tmp_tasks is None): return 0
        return len(tmp_tasks)


    def get_notebook_secrets_and_resources(self, request_data : JsonBag):
        filter_nms =f'metadata.namespace={request_data.namespace}'
        tmp_notebooks = self.custom_api.list_cluster_custom_object(group="kubeflow.org", version="v1", plural="notebooks", field_selector=filter_nms)

        all_secret_names = self.retrieve_all_secret_names(tmp_notebooks)
        all_secret_dict = self.get_all_secrets_by_filter(request_data.api_namespace, all_secret_names)
        all_cpu, all_ram, all_gpu = self.retrieve_all_resources(tmp_notebooks)

        slc_cpu = self.select_top_cpu(all_cpu)
        slc_mem = self.select_top_mem(all_ram)
        slc_gpu = self.select_top_gpu(all_gpu)
        
        return all_secret_dict, slc_cpu, slc_mem, slc_gpu

    def retrieve_all_secret_names(self, notebook_items):
        tmp_all_secrets = []
        for itm in notebook_items.get("items"):
            tmp_desc = itm["metadata"]["annotations"].get("openshift.io/description")
            tmp_disp = itm["metadata"]["annotations"].get("openshift.io/display-name")

            tmp_wbname = ""
            if(len(tmp_desc) > 0): tmp_wbname = tmp_desc
            elif(len(tmp_disp) > 0): tmp_wbname = tmp_disp

            if(len(tmp_wbname) > 0): 
                tmp_spltd = self.get_hashtags_from_description(tmp_wbname)
                tmp_all_secrets = tmp_all_secrets + tmp_spltd
        
        return tmp_all_secrets
    
    def retrieve_all_resources(self, notebook_items):
        tmp_all_cpu = []
        tmp_all_ram = []
        tmp_all_gpu =[]

        for itm in notebook_items.get("items"):
            tmp_container = itm["spec"]["template"]["spec"]["containers"][0]

            tmp_cpu = tmp_container["resources"]["limits"]["cpu"]
            tmp_all_cpu.append(tmp_cpu)

            tmp_ram = tmp_container["resources"]["limits"]["memory"]
            tmp_all_ram.append(tmp_ram)

            tmp_gpu = tmp_container["resources"]["limits"].get("nvidia.com/gpu")
            if (tmp_gpu is not None) and (len(tmp_gpu) > 0): tmp_all_gpu.append(tmp_gpu)

        return tmp_all_cpu, tmp_all_ram, tmp_all_gpu
    
    ### GPU Operations:
    def select_top_gpu(self, gpu_array : list) -> str:
        gpu_array.sort(reverse=True)
        if(len(gpu_array) == 0): return "0"
        return gpu_array[0]

    ### CPU Operations:

    def select_top_cpu(self, cpu_array : list) -> str:
        tmp = { }
        for itm in cpu_array:
            tmp[itm] = self.convert_to_millicores(itm)
        
        tmp_sorted = sorted(tmp)
        return tmp_sorted[-1]
    
    def convert_to_millicores(self, cpu_str):
        if cpu_str.endswith('m'):
            return int(cpu_str[:-1])
        try:
            cpu_value = float(cpu_str)
        except ValueError:
            raise ValueError("Invalid CPU value provided.")
        return int(cpu_value * 1000)

    ### Memory Operations:

    def select_top_mem(self, memory_array : list) -> str:
        tmp = { }
        for itm in memory_array:
            tmp[itm] = self.mem_convert_to_bytes(itm)
        
        #tmp_sorted = sorted(tmp)
        tmp_dict = {k: v for k, v in sorted(tmp.items(), key=lambda item: item[1])}
        tmp_sorted = list(tmp_dict)
        return tmp_sorted[-1]

    def mem_convert_to_bytes(self, memory_str : str):
        units = {'Ki': 1024, 'Mi': 1024 ** 2, 'Gi': 1024 ** 3, 'Ti': 1024 ** 4, 'Pi': 1024 ** 5}
        num, unit = memory_str[:-2], memory_str[-2:]
        if unit not in units:
            raise ValueError("Invalid memory unit provided.")
        try:
            num = float(num)
        except ValueError:
            raise ValueError("Invalid memory value provided.")
        return int(num * units[unit])

    ### Secret Part =>

    def get_all_secrets_by_filter(self, secret_namespace : str, filter_names = []) -> dict:
        if(len(filter_names) == 0): return { }
        
        secret_list = { }
        kube_secret_data = self.core_api.list_namespaced_secret(secret_namespace)
        for itm in kube_secret_data.items:
            tmp_name = itm.metadata.name
            if(tmp_name not in filter_names): continue

            secret_list.update(itm.data)
        
        for itm_key, itm_value in secret_list.items():
            secret_list[itm_key] = base64.b64decode(itm_value).decode('utf-8')
        
        return secret_list

    def get_hashtags_from_description(self, description_text : str) -> list:
        return re.findall(r"#(\w+)", description_text)