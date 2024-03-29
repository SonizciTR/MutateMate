
import json

from services.JsonBag import JsonBag
from services.KubeWrapperService import KubeWrapperService


class NotebookMutaterService:
    def __init__(self) -> None:
        pass

    def generate_mutation(self, request_data : JsonBag, kube_service : KubeWrapperService, secret_namespace : str) -> list:
        hashtags = kube_service.get_hashtags_from_description(request_data.workbench_description)
        secrets_targeted = kube_service.get_all_secrets_by_filter(secret_namespace, hashtags)

        if(len(secrets_targeted) == 0): return []
        
        nb_payload = []
        
        for itm_key, itm_value in secrets_targeted.items():
            nb_payload.append({"op": "add", "path": "/spec/template/spec/containers/0/env/-", "value": {"name": itm_key, "value": itm_value}})

        return nb_payload