# Quick Start
1. `pip install -q git+https://github.com/mberk06/useful.git`
2. Run one of the exmaple usages below

# Files
## useful/api_client.py 
This api client is a wrapper around the `requests` library and provides the following functionality. To implement, you should follow steps 1-4 in the comments below.

Here are the core advantages of using this over the basic requests library:
* **Session Management**: by leveraging a context manager, request sessions will be properly closed. 
* **Auth Management**: by simply passing a token in a SecretStr, you don't have to think about auth after that.
* **Error Handling**: there is built-in logic to identify retryable exceptions based on HTTP error codes.
* **Retrying Mechanism**: retry logic is built in. Max retries is `5` and there is exponential backoff.
* **Logging**: API calls, retries, and errors are logged.

```python
from pydantic import SecretStr
from useful import Client

class DatabricksClient(Client):
    def __init__(self, host: str, token: SecretStr):
        super().__init__(host, token)

    # Step 1: add use-case-specific methods here
    def get_warehouse_list(self) -> dict:
        return self._execute(
            http_command="GET",
            endpoint="/api/2.0/sql/warehouses",
        )
    
databricks_client = DatabricksClient(
    host="YOUR_DATABRICKS_WORKSPACE_URL", # Step 2: add databricks host
    token=SecretStr(dbutils.secrets.get(scope="berk-scope", key="pat")) # Step 3: add your PAT as a SecretStr
)

# Step 4: call the functions
warehouse_list = databricks_client.get_warehouse_list()
print(warehouse_list)
```

## useful/add_to_databricks_secrets.py 
This module lets you add a secret to a given workspace's secrets API. It's most secure to 
run this in a CLI on your local machine because notebooks auto-save and thereby will store your 
credentials, but you can technically run this anywhere.

```python
from pydantic import SecretStr
from useful import AddSecretToDatabricksAPI

databricks_client = AddSecretToDatabricksAPI(host="XXX", token=SecretStr("XXX"))
databricks_client.put_secret_safe(scope="berk", key="pat", value=SecretStr("XXX"))
```
