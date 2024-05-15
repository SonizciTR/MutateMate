
import json


class JsonBag():
    def __init__(self, json_data : json, running_namespace : str) -> None:
        self.assign_values(json_data)
        self.api_namespace = running_namespace
        self.raw = json_data
        pass
    
    def to_json(self):
        return {
            'kind': self.kind,
            'name': self.name,
            "namespace": self.namespace,
            "workbench_description": self.workbench_description,
            "api_namespace": self.api_namespace
        }

    def assign_values(self, json_data):
        tmp_obj = json_data["request"]["object"]
        
        self.kind = tmp_obj["kind"]
        self.name = tmp_obj.get("metadata").get("name")
        self.namespace = tmp_obj.get("metadata").get("namespace")
        self.workbench_description = tmp_obj.get("metadata").get("annotations").get("openshift.io/description")