# Quick Start
1. `pip install git+https://github.com/mberk06/useful.git`
2. Run one of the exmaple usages below

# Files
## useful/api_client.py 
This api client provides the following benefits, especially in a databricks environment:
* Token Management: It manages the API authentication via a token. It's up to the user to determine how they want to pass the token.
* Error Handling: It has built-in logic to identify retryable exceptions based on HTTP error codes.
* URL Validation: It validates that the URL for the API call is correctly formatted.
* Retrying Mechanism: It implements a retrying mechanism with exponential backoff to handle transient failures.
* Request Execution: It provides a method to execute an HTTP request to the server and handle the response.

### Example Usage 
```
from useful import Client

class DatabricksClient(Client):
    def __init__(self, host: str, token: SecretStr):
        super().__init__(host, token)

    def get_warehouse_list(self) -> dict:
        return self._execute(
            http_command="GET",
            endpoint="/api/2.0/sql/warehouses",
        )
    
    # More Databricks-specific methods can go here...

with DatabricksClient(
        host="YOUR_DATABRICKS_URL",
        token=SecretStr(dbutils.secrets.get(scope="berk-scope", key="pat")),
    ) as databricks_client:
    warehouse_list = databricks_client.get_warehouse_list()
    print(warehouse_list)
```