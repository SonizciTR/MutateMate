import os
import base64
import copy
import json

from flask import Flask, request, jsonify
from dotenv import load_dotenv

from services.MutatingHelperService import MutatingHelperService

load_dotenv()

from services.JsonBag import JsonBag
from services.KubeWrapperService import KubeWrapperService
from services.NotebookMutaterService import NotebookMutaterService
from services.PipelineRunMutaterService import PipelineRunMutaterService

app = Flask(__name__)

cnst_pipeline = "PipelineRun"
cnst_notebook = "Notebook"

cnst_kube_url = os.getenv("BASE_URL")
cnst_kube_access_token = os.getenv("ACCESS_TOKEN")
cnst_kube_current_namespace = os.getenv("kubeprojectname")
is_emergency = os.getenv("is_emergency", "False").lower() in ('true', '1', 't')

crd_name_list = [ cnst_pipeline, cnst_notebook ]

notebook_mutater = NotebookMutaterService()
pipeline_mutater = PipelineRunMutaterService()
mutate_helper = MutatingHelperService()

def wrt(unq_id : str, msg_to_print : str):
    print(f"[{unq_id}] >>> {msg_to_print}")

@app.route('/mutate', methods=['POST'])
def mutate_pod():
    tmp_uid = request.json.get("request").get("uid")
    wrt(tmp_uid, "********************** Mutate **********************")
    
    wrt(tmp_uid, json.dumps(request.json))

    #For Emergency. By pass everything.
    if(is_emergency): 
        wrt(tmp_uid, "By pass active, sending request untouched.")
        return send_response(request.json)
    #

    try:
        return main_flow(tmp_uid, request)
    except Exception as e:
        wrt(tmp_uid, f"Error happened. Sending request untouched. Detail=> {e}")

    return send_response(tmp_uid, request.json)

def main_flow(unq_id: str, request):
    req_data = JsonBag(request.json, cnst_kube_current_namespace)

    payload = []
    
    wrt(f"Request consumed => {req_data.to_json()}")

    #################

    if req_data.kind not in crd_name_list : return send_response(request.json)

    kube_service = KubeWrapperService(cnst_kube_url, cnst_kube_access_token)

    payload_extra = []

    if req_data.kind == cnst_notebook: 
        payload = [{"op": "add", "path": "/metadata/labels", "value": {"thy.editedby": "MutateMate" }}]
        payload_extra = notebook_mutater.mutate(req_data, kube_service, cnst_kube_current_namespace)

    if req_data.kind == cnst_pipeline: 
        #payload = [{"op": "add", "path": "/metadata/thysection", "value": {"thy.editedby": "MutateMate" }}]
        payload_extra = pipeline_mutater.mutate(req_data, kube_service)

    last_payload = payload + payload_extra
    wrt(unq_id, f"Payload last => {last_payload}")

    return send_response(unq_id, request.json, last_payload)

def send_response(unq_id: str, req_json, payload : list = None):
    #https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/#response
    response = req_json.copy()
    uid = req_json['request']['uid']

    response.pop('request', None)

    response["response"] = {
            "uid": uid,
            "allowed": True
    }

    if (payload is not None) and (len(payload) > 0):
        tmp_ser = base64.b64encode(json.dumps(payload).encode('utf-8')).decode()
        response["response"]["patchType"] = "JSONPatch"
        response["response"]["patch"] = tmp_ser
    
    
    wrt(unq_id, response)

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)