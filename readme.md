# Mutate Mate

## _Kubernetes Mutating Webhook Iplementation for Secrets and Resource Management(CPU, RAM, GPU)_

At our company we are using a tool for Data Science operations. This tool has flaws. To fix that we thought using Mutating Web Hooks is a great option.

If you are using Opendatahub and Elyra Pipelines or some tools build on that, you are having this issue.

This API's kubernetes project will have multiple secret definitons in that project.
At the webhook call, first we will look for project defitions. Definitions has key words with hashtags (like "lore ipsum #secret1 #secret2"). These will determine which secrets will ve injected to Notebook or Pipeline CRDs.
As a second step, if the call is for Elyra Pipelines; API will get the limitations for project and apply the same settings to Elyra Pipelines every step.

This way secrets will be auto assigned and will be at single namespace.
Elyra Pipelines is resource and secrets will be installed automatically with no manuel operation.

If you have same problem, I hope this will solve your problem too.

## Thanks

This project is possible with @ckavili's help. Thank you
