"""Sensor platform for Todolist to entities integration."""

from __future__ import annotations

from asyncio import sleep
from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.entity_platform import async_get_current_platform

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    """Initialize Todolist to entities config entry."""
    registry = er.async_get(hass)
    platform = async_get_current_platform()
    # Validate + resolve entity registry id to entity_id
    wrapper_entity_id = er.async_validate_entity_id(
        registry, config_entry.options[CONF_ENTITY_ID])

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(wrapper_entity_id, {})
    hass.data[DOMAIN][wrapper_entity_id]['async_add_entities'] = async_add_entities
    hass.data[DOMAIN][wrapper_entity_id]['platform'] = platform

    existing_entities = [entity for entity in registry.entities.values() if entity.config_entry_id == config_entry.entry_id]
    todo_list = await async_get_todolist_items(hass, wrapper_entity_id)

    for item in todo_list.items:
        entity = TodoListEntity(wrapper_entity_id, item)
        hass.data[DOMAIN][wrapper_entity_id][item.uid] = entity
        async_add_entities([entity])

    for sensor in existing_entities:
        uid = sensor.unique_id.split('_')[-1]
        if uid not in [i.uid for i in todo_list.items]:
            registry.async_remove(sensor.entity_id)


async def async_get_todolist_items(hass: HomeAssistant, wrapper_entity_id: str) -> TodoList:
    result = await hass.services.async_call(
        "todo",
        "get_items",
        target={"entity_id": wrapper_entity_id},
        blocking=True,
        return_response=True,
    )
    data = result.get(wrapper_entity_id) if result is not None else None
    if not isinstance(data, dict):
        data = None
    items = data.get("items", []) if data is not None else []
    if not isinstance(items, list):
        items = []
    return TodoList(items=[TodolistItem.create(i) for i in items])


class TodoListEntity(SensorEntity):
    """list_to_entities Sensor."""

    def __init__(self, wrapped_id: str, data: TodolistItem) -> None:
        """Initialize list_to_entities Sensor."""
        super().__init__()
        self._wrapped_entity_id = wrapped_id
        self._wrapped_id = wrapped_id.split(".")[1]
        self._data = data
        self._attr_name = data.summary
        self._attr_unique_id = f"{self._wrapped_id}_{self._data.uid}"
        self._attr_native_value = data.status
        self._attr_icon = "mdi:checkbox-marked" if data.status != "needs_action" else "mdi:checkbox-blank-outline"
        self._attr_extra_state_attributes = {
            k: v for k, v in {
                "uid": self._data.uid,
                "wrapped_id": self._wrapped_id,
                "summary": data.summary,
                "description": data.description,
                "due": data.due
            }.items() if v is not None
        }

    def update_todolist_data(self, data: TodolistItem):
        self._data = data
        self.async_schedule_update_ha_state(force_refresh=True)

    async def async_update(self):
        # self._attr_has_entity_name = True
        self._attr_name = self._data.summary
        self._attr_unique_id = f"{self._wrapped_id}_{self._data.uid}"
        self._attr_native_value = self._data.status
        self._attr_icon = "mdi:checkbox-marked" if self._data.status != "needs_action" else "mdi:checkbox-blank-outline"
        self._attr_extra_state_attributes = {
            k: v for k, v in {
                "uid": self._data.uid,
                "wrapped_id": self._wrapped_id,
                "description": self._data.description,
                "due": self._data.due
            }.items() if v is not None
        }


@dataclass
class TodolistItem:
    summary: str
    uid: str
    status: str
    description: str
    due: str

    @staticmethod
    def create(item) -> TodolistItem:
        return TodolistItem(
            item.get('summary'),
            item.get('uid'),
            item.get('status'),
            item.get('description'),
            item.get('due')
        )


@dataclass
class TodoList:
    items: list[TodolistItem]

