# Mutate Mate

## _Kubernetes Mutating Webhook Iplementation for Secrets and Resource Management(CPU, RAM, GPU)_

At our company we are using a tool for Data Science operations. This tool has flaws. To fix that we thought using Mutating Web Hooks is a great option.

If you are using Opendatahub and Elyra Pipelines or some tools build on that, you are having this issue.

This API's kubernetes project will have multiple secret definitons in that project.
At the webhook call, first we will look for project defitions. Definitions has key words with hashtags (like "lore ipsum #secret1 #secret2"). These will determine which secrets will be injected to Notebook or Pipeline CRDs.
As a second step, if the call is for Elyra Pipelines; API will get the limitations for project and apply the same settings to Elyra Pipelines every step.

This way secrets will be auto assigned and will be at single namespace.
Elyra Pipelines is resource and secrets will be installed automatically with no manuel operation.

If you have same problem, I hope this will solve your problem too.

## Thanks

This project is possible with @ckavili help. Thank you

### ProTip: Access Token

To get the access token for local debug; goto mutatemateapi pod and at the terminal write this command:

cat /run/secrets/kubernetes.io/serviceaccount/token

### caBundle Value :

Mutating webhook needs caBundle value of that cluster. To find the correct value, goto:

Home => API Explorer => Filter: MutatingWebhookConfiguration => Tab: Instances => find one contains: openshift => Open Yaml tab and find caBundle value from there

Then add change your "webhook.definition.yaml" file's cabundle value or if you already installed then goto:
Home => API Explorer => Filter: MutatingWebhookConfiguration => Tab: Instances => find one contains your helm installation name and change the cabundle value.
After this start a rollout for deployment.

Becareful sometimes cabundle differ with each custom object definition. If there is an error like : "[WARNING] Invalid request from ip=10.128.0.26: [SSL: SSLV3_ALERT_BAD_CERTIFICATE] sslv3 alert bad certificate (\_ssl.c:2637)", try other caBundles

###JSON Patch:

This is the commands that makes the changes. Basic information:
https://jsonpatch.com/

### Finding Right apiGroups, apiVersions, resources:

** apiGroups, apiVersions **

At your project's namespace goto API explorer and find the right resources. You can validate by "Resource details" => "Instances" tab. You should see your working instances.
Then enter the instance and open the YAML. You will see something like this:

apiVersion: argoproj.io/v1alpha1
kind: Workflow
....

"argoproj.io" is apiGroups and "v1alpha1" is apiVersions

** resources **

For the same example above, you can get "resources" from "kind". But you shoukd convert it to lowercase and make plural.
For this example, correct value is : "workflows"

Resource details
