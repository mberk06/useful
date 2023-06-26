from api_client import Client
from pydantic import SecretStr
import requests


class AddSecretToDatabricksAPI(Client):
    def __init__(self, host: str, token: SecretStr):
        super().__init__(host, token)

    def _create_scope_if_not_exists(self, scope: str):
        # create scope
        try:
            self._execute(
                http_command="POST",
                endpoint="/api/2.0/secrets/scopes/create",
                json={"scope": scope},
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400 and "RESOURCE_ALREADY_EXISTS" in str(e):
                print("Scope already exists - it will not be overwritten.")

    def _secret_exists(self, scope: str, key: str) -> bool:
        secrets_in_scope = self._execute(
            http_command="GET", endpoint="/api/2.0/secrets/list", json={"scope": scope}
        )

        return key in {s["key"] for s in secrets_in_scope.get("secrets", [])}

    def _put_secret(self, scope: str, key: str, value: SecretStr):
        self._execute(
            http_command="POST",
            endpoint="/api/2.0/secrets/put",
            json={"scope": scope, "key": key, "string_value": value.get_secret_value()},
        )

    def put_secret_safe(
        self, scope: str, key: str, value: SecretStr, overwrite: bool = True
    ):
        """
        Add a secret to the secret scope. If overwrite is false and the secret
        already exists, an error will be thrown. Also, the secret scope will
        automatically be created if it doesn't exist.
        """

        self._create_scope_if_not_exists(scope=scope)

        if not overwrite and self._secret_exists(scope, key):
            raise Exception(
                "Your secret already exists but overwrite = False. The secret will not be overwritten."
            )

        self._put_secret(scope, key, value)
