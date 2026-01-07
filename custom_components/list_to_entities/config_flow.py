"""Config flow for the Todolist to entities integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol

from homeassistant.components.todo import DOMAIN as TODO_DOMAIN
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
)

from .const import DOMAIN

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=TODO_DOMAIN)
        ),
    }
)

CONFIG_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "user": SchemaFlowFormStep(OPTIONS_SCHEMA)
}


class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow for Todolist to entities."""

    config_flow = CONFIG_FLOW
    # TODO remove the options_flow if the integration does not have an options flow
    # options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""
        if CONF_ENTITY_ID not in options:
            return ""
        wrapper_entity_id = options[CONF_ENTITY_ID]
        state = self.hass.states.get(wrapper_entity_id)
        name = state.name if state else ""
        return name
