import asyncio
import logging
from datetime import datetime, timedelta
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.solar_sunsynk.coordinator import SunsynkDataUpdateCoordinator
from custom_components.solar_sunsynk.helpers import _settings_match
from custom_components.solar_sunsynk.number import SunsynkNumber, _NumberDesc
from custom_components.solar_sunsynk.select import SunsynkSelect, _SelectDesc
from custom_components.solar_sunsynk.switch import SunsynkSwitch, _SwitchDesc
from custom_components.solar_sunsynk.text import SunsynkTimeText
from custom_components.solar_sunsynk.sunsynkapi import sunsynk_api
from custom_components.solar_sunsynk.sensor import SunsynkSensor, SENSOR_DESCRIPTIONS


@pytest.fixture
def settings() -> dict[str, Any]:
    return {
        "safetyType": "2", "battMode": "-1", "cap1": "30", "cap2": "40",
        **{f"cap{slot}": "50" for slot in range(3, 7)},
        **{f"sellTime{slot}": f"{(slot - 1) * 4:02d}:00" for slot in range(1, 7)},
    }


@pytest.fixture
def coordinator(settings: dict[str, Any]) -> SimpleNamespace:
    api: SimpleNamespace = SimpleNamespace(
        get_settings=AsyncMock(return_value={"success": True, "data": dict(settings)}),
        set_settings=AsyncMock(return_value={"success": True}),
    )
    return SimpleNamespace(
        data={"inverter": {"inverter_sn": "PRIVATE-SERIAL", "settings": settings}},
        last_update_success=True,
        settings_write_locks={},
        settings_keys={},
        api=api,
        async_request_refresh=AsyncMock(),
    )


@pytest.fixture
def number(coordinator: SimpleNamespace) -> SunsynkNumber:
    return SunsynkNumber(
        coordinator, SimpleNamespace(entry_id="entry"), "inverter",
        _NumberDesc("cap1", "Slot 1 Battery SOC", "System Mode", 0, 100),
    )


@pytest.mark.parametrize("inverter", [None, {}, {"settings": None}, {"settings": []}, {"settings": {}}])
def test_missing_inverter_or_settings_is_unavailable(
    number: SunsynkNumber, coordinator: SimpleNamespace, inverter: object
) -> None:
    coordinator.data = {} if inverter is None else {"inverter": inverter}
    assert number.available is False
    assert number.native_value is None


@pytest.mark.parametrize("value", [None, "invalid", "nan", "inf", {}])
def test_invalid_number_does_not_become_zero(
    number: SunsynkNumber, coordinator: SimpleNamespace, value: object
) -> None:
    coordinator.data["inverter"]["settings"]["cap1"] = value
    assert number.native_value is None


@pytest.mark.asyncio
@pytest.mark.parametrize("missing_key", ["cap1", "safetyType", "battMode"])
async def test_incomplete_cache_blocks_all_network_calls(
    number: SunsynkNumber, coordinator: SimpleNamespace, missing_key: str
) -> None:
    coordinator.data["inverter"]["settings"].pop(missing_key)
    with pytest.raises(HomeAssistantError, match="incomplete"):
        await number.async_set_native_value(55)
    coordinator.api.get_settings.assert_not_awaited()
    coordinator.api.set_settings.assert_not_awaited()


@pytest.mark.asyncio
async def test_failed_refresh_blocks_write(
    number: SunsynkNumber, coordinator: SimpleNamespace
) -> None:
    coordinator.last_update_success = False
    with pytest.raises(HomeAssistantError, match="refresh failed"):
        await number.async_set_native_value(55)
    coordinator.api.set_settings.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("response", [None, {"data": None}, {"data": {}}, {"data": {"safetyType": "2", "battMode": "-1", "cap1": "30"}}, {"success": False, "data": {"cap1": "30"}}])
async def test_incomplete_fresh_read_blocks_post(
    number: SunsynkNumber, coordinator: SimpleNamespace, response: object
) -> None:
    coordinator.api.get_settings.return_value = response
    with pytest.raises(HomeAssistantError):
        await number.async_set_native_value(55)
    coordinator.api.set_settings.assert_not_awaited()


@pytest.mark.asyncio
async def test_write_preserves_fresh_values_without_optimistic_state(
    number: SunsynkNumber, coordinator: SimpleNamespace, settings: dict[str, Any]
) -> None:
    fresh: dict[str, Any] = {**settings, "cap2": "65"}
    coordinator.api.get_settings.return_value = {"data": fresh}
    await number.async_set_native_value(55)
    payload: dict[str, Any] = coordinator.api.set_settings.await_args.args[1]
    assert payload == {**fresh, "cap1": "55", "sn": "PRIVATE-SERIAL"}
    assert fresh["cap1"] == "30"
    assert number.native_value == 30
    coordinator.async_request_refresh.assert_awaited_once()
    coordinator.data["inverter"]["settings"]["cap1"] = "55"
    assert number.native_value == 55


@pytest.mark.asyncio
async def test_failed_write_keeps_readback_and_redacts_error(
    number: SunsynkNumber, coordinator: SimpleNamespace, caplog: pytest.LogCaptureFixture
) -> None:
    coordinator.api.set_settings.side_effect = TimeoutError("PRIVATE-SERIAL secret-token")
    with caplog.at_level(logging.WARNING), pytest.raises(HomeAssistantError) as error:
        await number.async_set_native_value(55)
    assert number.native_value == 30
    assert "cap1" in caplog.text
    assert "PRIVATE-SERIAL" not in caplog.text + str(error.value)
    assert "secret-token" not in caplog.text + str(error.value)
    coordinator.async_request_refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_writes_for_same_inverter_are_serialized(
    number: SunsynkNumber, coordinator: SimpleNamespace
) -> None:
    entered: asyncio.Event = asyncio.Event()
    release: asyncio.Event = asyncio.Event()

    async def read_settings(serial: str) -> dict[str, Any]:
        entered.set()
        await release.wait()
        return {"data": dict(coordinator.data["inverter"]["settings"])}

    coordinator.api.get_settings.side_effect = read_settings
    first: asyncio.Task[None] = asyncio.create_task(number.async_set_native_value(55))
    await entered.wait()
    second: asyncio.Task[None] = asyncio.create_task(number.async_set_native_value(60))
    await asyncio.sleep(0)
    assert coordinator.api.get_settings.await_count == 1
    release.set()
    await asyncio.gather(first, second)
    assert coordinator.api.set_settings.await_count == 2


def test_other_settings_entities_tolerate_disappearing_data(coordinator: SimpleNamespace) -> None:
    config: SimpleNamespace = SimpleNamespace(entry_id="entry")
    switch: SunsynkSwitch = SunsynkSwitch(coordinator, config, "inverter", _SwitchDesc("time1on", "Charge", "System Mode"))
    select: SunsynkSelect = SunsynkSelect(coordinator, config, "inverter", _SelectDesc("battMode", "Type", "Battery", {"-1": "Lithium"}))
    text: SunsynkTimeText = SunsynkTimeText(coordinator, config, "inverter", "sellTime1", 1)
    coordinator.data = {}
    assert switch.is_on is None
    assert select.current_option is None
    assert text.native_value is None
    assert not any(entity.available for entity in [switch, select, text])


@pytest.mark.asyncio
@pytest.mark.parametrize("section", ["inverter_data", "inverter_load_data", "inverter_grid_data", "inverter_battery_data", "inverter_input_data"])
@pytest.mark.parametrize("missing_data", [None, {}])
async def test_settings_survive_missing_telemetry(
    settings: dict[str, Any], section: str, missing_data: object,
    caplog: pytest.LogCaptureFixture,
) -> None:
    raw: dict[str, Any] = {
        "inverter_data": {"model": "test"},
        "inverter_settings_data": settings,
        "inverter_load_data": {"dailyUsed": 1},
        "inverter_grid_data": {"pac": 1},
        "inverter_battery_data": {"soc": 50},
        "inverter_input_data": {"pac": 1},
    }
    raw[section] = missing_data
    api: SimpleNamespace = SimpleNamespace(get_all_data=AsyncMock(return_value={"sunsynk_PRIVATE-PLANT_PRIVATE-SERIAL": raw}))
    coordinator: SunsynkDataUpdateCoordinator = SunsynkDataUpdateCoordinator(SimpleNamespace(), api)
    result: dict[str, Any] = await coordinator.update_inverter_data()
    inverter: dict[str, Any] = result["sunsynk_PRIVATE-PLANT_PRIVATE-SERIAL"]
    assert inverter["settings"] == settings
    assert inverter["statistics_available"] is False
    assert "PRIVATE-PLANT" not in caplog.text
    assert "PRIVATE-SERIAL" not in caplog.text


@pytest.fixture
def api_response() -> tuple[sunsynk_api, MagicMock, MagicMock]:
    response: MagicMock = MagicMock()
    response.__aenter__ = AsyncMock(return_value=response)
    response.__aexit__ = AsyncMock(return_value=False)
    response.json = AsyncMock(return_value={"success": True})
    session: MagicMock = MagicMock()
    session.post.return_value = response
    api: sunsynk_api = sunsynk_api("private-account", "private-password", SimpleNamespace())
    api._session = session
    api._token = "private-token"
    api._token_expires = datetime.now() + timedelta(days=1)
    return api, session, response


@pytest.mark.asyncio
@pytest.mark.parametrize("result", [{"success": False, "msg": "PRIVATE-SERIAL"}, {}, None, {"success": "true"}])
async def test_api_rejection_or_malformed_response_is_reported(
    api_response: tuple[sunsynk_api, MagicMock, MagicMock], result: object,
    caplog: pytest.LogCaptureFixture,
) -> None:
    api, session, response = api_response
    response.json.return_value = result
    with pytest.raises(HomeAssistantError) as error:
        await api.set_settings("PRIVATE-SERIAL", {"cap1": "55"})
    assert "PRIVATE-SERIAL" not in caplog.text + str(error.value)
    session.post.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [TimeoutError("PRIVATE-SERIAL"), aiohttp.ClientResponseError(MagicMock(), (), status=403, message="PRIVATE-SERIAL")])
async def test_api_transport_failure_is_not_retried(
    api_response: tuple[sunsynk_api, MagicMock, MagicMock], error: Exception,
    caplog: pytest.LogCaptureFixture,
) -> None:
    api, session, response = api_response
    response.raise_for_status.side_effect = error
    with pytest.raises(HomeAssistantError) as raised:
        await api.set_settings("PRIVATE-SERIAL", {"cap1": "55"})
    session.post.assert_called_once()
    assert "PRIVATE-SERIAL" not in caplog.text + str(raised.value)


@pytest.mark.asyncio
async def test_api_success_returns_acknowledgement(
    api_response: tuple[sunsynk_api, MagicMock, MagicMock]
) -> None:
    api, session, response = api_response
    result: dict[str, object] = await api.set_settings("PRIVATE-SERIAL", {"cap1": "55"})
    assert result == {"success": True}
    session.post.assert_called_once()


@pytest.mark.asyncio
async def test_accepted_write_with_old_readback_is_logged(
    number: SunsynkNumber, coordinator: SimpleNamespace,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING):
        await number.async_set_native_value(55)
    assert "cloud readback has not confirmed" in caplog.text
    assert "cap1" in caplog.text
    assert "PRIVATE-SERIAL" not in caplog.text
    assert number.native_value == 30


@pytest.mark.asyncio
async def test_matching_readback_does_not_warn(
    number: SunsynkNumber, coordinator: SimpleNamespace,
    caplog: pytest.LogCaptureFixture,
) -> None:
    async def refresh() -> None:
        coordinator.data["inverter"]["settings"]["cap1"] = 55

    coordinator.async_request_refresh.side_effect = refresh
    with caplog.at_level(logging.WARNING):
        await number.async_set_native_value(55)
    assert number.native_value == 55
    assert "not confirmed" not in caplog.text


@pytest.mark.asyncio
async def test_previously_observed_key_missing_from_cache_blocks_write(
    number: SunsynkNumber, coordinator: SimpleNamespace
) -> None:
    coordinator.settings_keys["inverter"] = {"zeroExportPower"}
    with pytest.raises(HomeAssistantError, match="incomplete"):
        await number.async_set_native_value(55)
    coordinator.api.set_settings.assert_not_awaited()


@pytest.mark.asyncio
async def test_partial_schedule_blocks_write(
    number: SunsynkNumber, coordinator: SimpleNamespace
) -> None:
    coordinator.data["inverter"]["settings"].pop("sellTime6")
    with pytest.raises(HomeAssistantError, match="incomplete"):
        await number.async_set_native_value(55)
    coordinator.api.set_settings.assert_not_awaited()


@pytest.mark.asyncio
async def test_unobserved_optional_null_does_not_block_write(
    number: SunsynkNumber, coordinator: SimpleNamespace
) -> None:
    coordinator.data["inverter"]["settings"]["unsupportedOption"] = None
    await number.async_set_native_value(55)
    coordinator.api.set_settings.assert_awaited_once()


@pytest.mark.parametrize("actual,requested,expected", [(55, "55.0", True), (True, "1", True), (False, "0", True), (None, "0", False), ("12:00", "12:00", True), ("30", "55", False)])
def test_readback_comparison(actual: object, requested: object, expected: bool) -> None:
    assert _settings_match(actual, requested) is expected


@pytest.mark.asyncio
@pytest.mark.parametrize("timestamp", [None, "invalid", "2026-10-13T10:00:00"])
async def test_valid_telemetry_survives_missing_or_invalid_timestamp(
    settings: dict[str, Any], timestamp: object
) -> None:
    raw: dict[str, Any] = {
        "inverter_data": {"model": "test", "updateAt": timestamp},
        "inverter_settings_data": settings,
        "inverter_load_data": {"dailyUsed": 1},
        "inverter_grid_data": {"pac": 1},
        "inverter_battery_data": {"soc": 50},
        "inverter_input_data": {"pac": 1},
    }
    api: SimpleNamespace = SimpleNamespace(get_all_data=AsyncMock(return_value={"sunsynk_plant_serial": raw}))
    coordinator: SunsynkDataUpdateCoordinator = SunsynkDataUpdateCoordinator(SimpleNamespace(), api)
    coordinator.data = await coordinator.update_inverter_data()
    assert coordinator.data["sunsynk_plant_serial"]["statistics_available"] is True
    sensor: SunsynkSensor = SunsynkSensor(coordinator, SimpleNamespace(entry_id="entry"), "sunsynk_plant_serial", SENSOR_DESCRIPTIONS[0])
    assert sensor.available is True
    coordinator.data = {}
    assert sensor.available is False
    assert sensor.native_value is None


@pytest.mark.asyncio
@pytest.mark.parametrize("response", [None, [], {"data": None}, {"success": False, "data": {"model": "untrusted"}}])
async def test_malformed_endpoint_response_becomes_missing_data(
    api_response: tuple[sunsynk_api, MagicMock, MagicMock], response: object
) -> None:
    api, session, write_response = api_response
    api.get_plant_data = AsyncMock(return_value={"data": {"infos": [{"id": "plant"}]}})
    api.get_inverters_data = AsyncMock(return_value={"data": {"infos": [{"sn": "serial"}]}})
    api.fetch = AsyncMock(return_value=response)
    result: dict[str, Any] = await api.get_all_data()
    assert all(value is None for value in result["sunsynk_plant_serial"].values())
    session.post.assert_not_called()
