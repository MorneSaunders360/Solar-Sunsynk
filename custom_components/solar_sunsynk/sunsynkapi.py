import asyncio

import aiohttp
import urllib3
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
import time
import base64
import hashlib
from datetime import datetime, timedelta

from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from tenacity import (
    retry,
    RetryError,
    wait_exponential,
    stop_after_attempt,
    retry_if_not_exception_type,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from datetime import datetime, timedelta
import logging

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://api.sunsynk.net"


class sunsynk_api:
    def __init__(self, username: str, password: str, hass: HomeAssistant):
        self.username: str = username
        self.password: str = password
        self.hass: HomeAssistant = hass

        self._token: str = ""
        self._token_expires: datetime = datetime.now()
        self._session: aiohttp.Session | None = None

        self._plants: list[dict] = []

    def __del__(self):
        if self._session:
            asyncio.run_coroutine_threadsafe(self._session.close(), self.hass.loop)

    @property
    def token(self) -> str:
        """Get the current authentication token.

        Returns:
            str: The current token if valid, empty string if expired or not set.
        """
        if self._token and self._token_expires > datetime.now():
            return self._token

        return ""

    @property
    async def session(self) -> aiohttp.ClientSession:
        """Get or create an authenticated aiohttp ClientSession.

        Returns:
            aiohttp.ClientSession: Session object with authentication headers set.

        Raises:
            Exception: If authentication fails during login.
        """
        if self._session and self.token:
            return self._session

        await self.authenticate(self.username, self.password)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}",
        }
        self._session = aiohttp.ClientSession(BASE_URL, headers=headers)
        return self._session

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_not_exception_type(HomeAssistantError),
    )
    async def fetch(self, url: str) -> dict[str, str]:
        """
        Perform a GET request, retrying up to three times with exponential backoff.

        Returns:
            dict[str, str]: A dictionary of JSON key / value pairs containing the
            results of the request.

        Raises:
            RetryError: If retries have been exceeded.
            Exception: If an exception occurred during the fetc.
        """
        try:
            async with (await self.session).get(url) as resp:
                resp.raise_for_status()
                resp = await resp.json()
                return resp

        except RetryError as e:
            msg = f"Error fetching data from {url}: {e}. Giving up after 3 retries..."
            _LOGGER.error(msg)
            raise HomeAssistantError(msg)
        except Exception as e:
            _LOGGER.warning(f"Error fetching data from {url}: {e}. Retrying...")
            raise e

    async def get_inverters_data(self, plant_id: str) -> dict[str, str]:
        return await self.fetch(
            f"/api/v1/plant/{plant_id}/inverters?page=1&limit=10&status=-1&sn=&id={plant_id}&type=-2"
        )

    async def get_inverter_data(self, inverter_sn: str) -> dict[str, str]:
        return await self.fetch(f"api/v1/inverter/{inverter_sn}")

    async def get_inverter_load_data(self, inverter_sn: str) -> dict[str, str]:
        return await self.fetch(
            f"api/v1/inverter/load/{inverter_sn}/realtime?sn={inverter_sn}&lan=en"
        )

    async def get_inverter_grid_data(self, inverter_sn: str) -> dict[str, str]:
        return await self.fetch(
            f"api/v1/inverter/grid/{inverter_sn}/realtime?sn={inverter_sn}&lan=en"
        )

    async def get_inverter_battery_data(self, inverter_sn: str) -> dict[str, str]:
        return await self.fetch(
            f"api/v1/inverter/battery/{inverter_sn}/realtime?sn={inverter_sn}&lan=en"
        )

    async def get_inverter_input_data(self, inverter_sn: str) -> dict[str, str]:
        return await self.fetch(f"api/v1/inverter/{inverter_sn}/realtime/input")

    async def get_inverter_output_data(self, inverter_sn: str) -> dict[str, str]:
        return await self.fetch(f"api/v1/inverter/{inverter_sn}/realtime/output")

    async def get_plant_data(self) -> dict[str, str]:
        return await self.fetch(f"api/v1/plants?page=1&limit=10")

    async def get_energy_flow_data(self, plant_id: str) -> dict[str, str]:
        return await self.fetch(f"api/v1/plant/energy/{plant_id}/flow")

    async def get_realtime_data(self, plant_id: str) -> dict[str, str]:
        return await self.fetch(f"api/v1/plant/{plant_id}/realtime?id={plant_id}")

    async def get_all_data(self) -> dict:
        all_data = {}

        for plant in (await self.get_plant_data())["data"]["infos"]:
            plant_id = plant["id"]
            for inverter in (await self.get_inverters_data(plant_id))["data"]["infos"]:
                inverter_id = inverter["sn"]
                inverter_data = {
                    "inverter_data": self.get_inverter_data(inverter_id),
                    "inverter_load_data": self.get_inverter_load_data(inverter_id),
                    "inverter_grid_data": self.get_inverter_grid_data(inverter_id),
                    "inverter_battery_data": self.get_inverter_battery_data(
                        inverter_id
                    ),
                    "inverter_input_data": self.get_inverter_input_data(inverter_id),
                    "inverter_output_data": self.get_inverter_output_data(inverter_id),
                    "inverter_settings_data": self.get_settings(inverter_id),
                }
                # Gather all results
                results = await asyncio.gather(
                    *inverter_data.values(), return_exceptions=True
                )

                # Strip out exceptions
                for k, v in zip(inverter_data, results):
                    inverter_data[k] = (
                        v.get("data") if not isinstance(v, Exception) else None
                    )

                plant_sn_id = f"sunsynk_{plant_id}_{inverter_id}"
                all_data[plant_sn_id] = inverter_data

        return all_data

    async def get_settings(self, inverter_sn: str) -> dict[str, str]:
        return await self.fetch(f"api/v1/common/setting/{inverter_sn}/read")

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3),
    )
    async def set_settings(
        self, inverter_sn: str, setting_data: dict[str, str]
    ) -> dict[str, str]:
        async with (await self.session).post(
            f"api/v1/common/setting/{inverter_sn}/set", json=setting_data
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_not_exception_type(HomeAssistantError),
    )
    async def authenticate(self, username: str, password: str) -> None:
        """Authenticate with the Sunsynk API and obtain access token.

        This method performs the login request to obtain a new authentication token.
        It updates the internal token and expiration time based on the response.

        Raises:
            Exception: If authentication fails or response indicates failure
            aiohttp.ClientError: If there are network/HTTP errors during the request
        """
        async with aiohttp.ClientSession(BASE_URL) as session:
            source: str = "elinter" if "pv.inteless.com" in BASE_URL else "sunsynk"

            public_key_nonce: str = str(int(time.time() * 1000))
            public_key_signature_input: str = (
                f"nonce={public_key_nonce}&source={source}POWER_VIEW"
            )
            public_key_signature: str = hashlib.md5(
                public_key_signature_input.encode("utf-8")
            ).hexdigest()

            params: dict[str, str] = {
                "source": source,
                "nonce": public_key_nonce,
                "sign": public_key_signature,
            }

            async with session.get("/anonymous/publicKey", params=params) as resp:
                resp.raise_for_status()
                public_key_json: dict[str, object] = await resp.json()
                public_key_string: str = str(public_key_json["data"])

            public_key_pem: str = (
                "-----BEGIN PUBLIC KEY-----\n"
                + public_key_string
                + "\n-----END PUBLIC KEY-----"
            )
            public_key = load_pem_public_key(public_key_pem.encode("utf-8"))

            encrypted_password_bytes: bytes = public_key.encrypt(
                password.encode("utf-8"),
                PKCS1v15(),
            )
            encrypted_password: str = base64.b64encode(
                encrypted_password_bytes
            ).decode("utf-8")

            token_nonce: str = str(int(time.time() * 1000))
            token_sign_string: str = (
                f"nonce={token_nonce}&source=sunsynk{public_key_string[:10]}"
            )
            token_sign: str = hashlib.md5(
                token_sign_string.encode("utf-8")
            ).hexdigest()

            data: dict[str, object] = {
                "client_id": "csp-web",
                "grant_type": "password",
                "password": encrypted_password,
                "source": source,
                "username": username,
                "nonce": token_nonce,
                "sign": token_sign,
            }

            async with session.post("/oauth/token/new", json=data) as resp:
                resp.raise_for_status()
                resp_json: dict[str, object] = await resp.json()

                msg: str = str(resp_json.get("msg"))
                if msg != "Success":
                    error_msg: str = f"Error during authentication: {msg}"
                    _LOGGER.error(error_msg)
                    raise HomeAssistantError(error_msg)

                resp_data: dict[str, object] = resp_json["data"]  # type: ignore[assignment]
                access_token: str = str(resp_data["access_token"])
                expires_in_raw: object = resp_data.get("expires_in", 0)
                expires_in: int = int(expires_in_raw) if expires_in_raw is not None else 0

                self._token = access_token
                self._token_expires = datetime.now() + timedelta(seconds=expires_in)

