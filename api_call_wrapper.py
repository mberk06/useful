# This code wraps API calls, specifically for the Databricks API. It extends to other APIs thare are authenticated via a token in the header.

# source: https://github.com/databricks/compute_optimizer/blob/main/compute_optimizer/engine/resource_provisioner/dbr_resource_provisioner.py
import requests
import os
from pydantic import SecretStr

class APIWrapper:
  def __init__(self, host: str, token: SecretStr):
    self.host = host.rstrip("/") + "/"
    self._token = token

  @property
  def token(self):
    return self._token.get_secret_value()

  def _cmd(self, endpoint: str, http_cmd: str, headers: dict = {}, json: dict = {}):
    """
    Helper to run commands against the Databricks API.
    """
    headers.update({"Authorization": f"Bearer {self.token}"})

    def _wrapper(f):
      return f(
        url=os.path.join(self.host, endpoint.lstrip("/")),
        headers=headers,
        json=json,
      )

    if http_cmd == "GET":
      return _wrapper(requests.get) 
    elif http_cmd == "PUT":
      return _wrapper(requests.put)
    elif http_cmd == "POST":
      return _wrapper(requests.post)
    elif http_cmd == "DELETE":
      return _wrapper(requests.delete)
    
  def get_warehouse_connection_details(self, warehouse_id: str) -> requests.Response:
    """
    Example call to get a Databricks SQL warehouse connection information. 
    """
    out = self._cmd(
      http_cmd="GET",
      endpoint=os.path.join(DBSQL_SERVICE_PATH, "warehouses", warehouse_id),
    )
    out.raise_for_status()
    return out
 
# Example usage
api_wrapper = APIWrapper(
 host='XXX',
 token='XXX'
)
warehouse_information = api_wrapper.get_warehouse_connection_details('123').json()
print(warehouse_information)
