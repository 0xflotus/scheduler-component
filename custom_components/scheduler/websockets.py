import voluptuous as vol
import logging

from homeassistant.components import websocket_api
from homeassistant.core import callback
from homeassistant.components.http.data_validator import RequestDataValidator
from homeassistant.helpers import config_validation as cv
from homeassistant.components.http import HomeAssistantView

from .const import (
    DOMAIN,
    SCHEDULE_SCHEMA,
)


_LOGGER = logging.getLogger(__name__)
EVENT = "schedules_updated"


class SchedulesAddView(HomeAssistantView):
    """Login to Home Assistant cloud."""

    url = "/api/schedules/add"
    name = "api:schedules:add"

    @RequestDataValidator(
        SCHEDULE_SCHEMA
    )
    def post(self, request, data):
        """Handle config update request."""
        hass = request.app["hass"]
        coordinator = hass.data[DOMAIN]
        coordinator.async_create_schedule(data)
        request.app["hass"].bus.async_fire(EVENT)
        return self.json({"success": True})


class SchedulesEditView(HomeAssistantView):
    """Login to Home Assistant cloud."""

    url = "/api/schedules/edit"
    name = "api:schedules:edit"

    @RequestDataValidator(
        SCHEDULE_SCHEMA.extend({
            vol.Required("schedule_id"): cv.string
        })
    )
    async def post(self, request, data):
        """Handle config update request."""
        hass = request.app["hass"]
        coordinator = hass.data[DOMAIN]
        coordinator.async_edit_schedule(data)
        request.app["hass"].bus.async_fire(EVENT)
        return self.json({"success": True})


class SchedulesRemoveView(HomeAssistantView):
    """Login to Home Assistant cloud."""

    url = "/api/schedules/remove"
    name = "api:schedules:remove"

    @RequestDataValidator(
        vol.Schema({
            vol.Required("schedule_id"): cv.string
        })
    )
    async def post(self, request, data):
        """Handle config update request."""
        hass = request.app["hass"]
        coordinator = hass.data[DOMAIN]
        coordinator.async_remove_schedule(data["schedule_id"])
        request.app["hass"].bus.async_fire(EVENT)
        return self.json({"success": True})


@callback
def websocket_get_schedules(hass, connection, msg):
    """Publish schedules list data."""
    coordinator = hass.data[DOMAIN]
    schedules = coordinator.store.async_get_schedules()
    connection.send_result(msg["id"], schedules)


async def async_register_websockets(hass):

    hass.http.register_view(SchedulesAddView)
    hass.http.register_view(SchedulesEditView)
    hass.http.register_view(SchedulesRemoveView)

    hass.components.websocket_api.async_register_command(
        "schedules",
        websocket_get_schedules,
        websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): "schedules"}
        ),
    )
