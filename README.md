# Quick Start
1. `pip install git+https://github.com/mberk06/useful.git`
2. Run one of the exmaple usages below

# Files
## useful/api_client.py 
This api client is a wrapper around the `requests` library and provides the following functionality. To implement, you should follow steps 1-4 in the comments below.

Here are the core advantages of using this over the basic requests library:
* Session Management: by leveraging a context manager, request sessions will be properly closed. 
* Auth Management: by simply passing a token in a SecretStr, you don't have to think about auth after that.
* Error Handling: there is built-in logic to identify retryable exceptions based on HTTP error codes.
* Retrying Mechanism: retry logic is built in. Max retries is `5` and there is exponential backoff.

### Example Usage 
```python
from pydantic import SecretStr
from useful import Client

# Step 1: add your host name
def get_host():
    return "YOUR_DATABRICKS_WORKSPACE_URL"

# Step 2: update this to a PAT (ideally in the secrets API)
def get_token():
    return SecretStr(dbutils.secrets.get(scope="berk-scope", key="pat"))

class DatabricksClient(Client):
    def __init__(self, host: str, token: SecretStr):
        super().__init__(host, token)

    # Step 3: add use-case-specific methods here
    def get_warehouse_list(self) -> dict:
        return self._execute(
            http_command="GET",
            endpoint="/api/2.0/sql/warehouses",
        )
    
# Step 4: call them via a session manager
with DatabricksClient(get_host(), get_token()) as databricks_client:
    warehouse_list = databricks_client.get_warehouse_list()
    print(warehouse_list)
```
