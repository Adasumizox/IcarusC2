# IkarusC2
## Establishing covert c2 connections using azure services

### Azure Key Vault:

Key vault is azure cloud service for securly storing and accessing secrets. <br>
We can use Azure key vault library to access secrets/keys/certificates [key vault library](https://learn.microsoft.com/en-us/python/api/overview/azure/key-vault?view=azure-python) <br>
There is multiple ways to authenticate to [azure key vault](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python) <br>
In this project enviromental variable are used to authenticate

How to run:

Provide eviromental variables
- AZURE_TENANT_ID
- AZURE_CLIENT_ID
- AZURE_CLIENT_SECRET

Example: `export AZURE_TENANT_ID='xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' && export AZURE_CLIENT_ID='xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' && export AZURE_CLIENT_SECRET='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' && python3 keyvaultc2_agent.py --vault VAULT_NAME`

### Azure Boards:

Azure boards is azure cloud service for working with Kanban boards, backlog, team dashboards and custom reporting. <br>
To interact with Azure Boards we can use [Rest API](https://learn.microsoft.com/en-us/rest/api/azure/devops/work/?view=azure-devops-rest-7.1)
<br>
To authenticate we can use Personal Access Token

Example: `python3 boardc2_agent.py -t PAT -o ORG_NAME -p PROJECT_NAME -i ID [-T TYPE]`

### Service Bus:

Service Bus is a fully managed enterprise message broker with message queues. <br>
We can use [Service Bus library](https://learn.microsoft.com/en-us/python/api/overview/azure/service-bus?view=azure-python&preserve-view=true) to publish/subscribe to messaging queues <br>
We can authenticate via connection string

Example: `python3 busc2_agent.py -c CONNECTION_STRING -gq GET_QUEUE -sq SEND_QUEUE`

Example: `python3 busc2_server.py -c CONNECTION_STRING -gq SEND_QUEUE -sq GET_QUEUE [--read] [--send COMMAND]`