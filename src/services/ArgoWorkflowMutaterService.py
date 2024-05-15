
import json

from services.KubeWrapperService import KubeWrapperService
from services.MutatingHelperService import MutatingHelperService


class ArgoWorkflowMutaterService:
    def __init__(self) -> None:
        pass

    def mutate(self, data_req : json, kube_service : KubeWrapperService) -> json:
        pr_payload = []

        mwh_service = MutatingHelperService()
        #task_count = kube_service.get_notebook_task_count(data_req)
        kube_secrets, kube_cpu, kube_ram, kube_gpu = kube_service.get_notebook_secrets_and_resources(data_req)

        #Secret commands:
        for itm_key, itm_value in kube_secrets.items():
            pr_payload.append(mwh_service.add_secret_for_argo_workflow(itm_key, itm_value))

        return pr_payload