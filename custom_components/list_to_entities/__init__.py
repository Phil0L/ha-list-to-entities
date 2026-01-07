"""The Todolist to entities integration."""

from __future__ import annotations

from asyncio import sleep

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_ENTITY_ID
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .sensor import TodoListEntity, TodolistItem, async_get_todolist_items


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Todolist to entities from a config entry."""
    # TODO Optionally store an object for your platforms to access
    # entry.runtime_data = ...

    while not hass.services.has_service("todo", "get_items"):
       await sleep(1)

    await hass.config_entries.async_forward_entry_setups(entry, (Platform.SENSOR,))

    @callback
    def _state_changed(event):
        entry.async_create_task(hass,
            _async_update_entry(hass, event, entry))

    @callback
    def _state_will_change(event):
        async def _delayed(_):
            _state_changed(event)
        async_call_later(hass, 0.5, _delayed)

    @callback
    def _is_todo_event(data) -> bool:
        return data.get('domain') == 'todo' and data.get('service_data').get(CONF_ENTITY_ID)[0] == wrapper_entity_id

    wrapper_entity_id = entry.options[CONF_ENTITY_ID]

    # State change (item added, deleted, marked)
    async_track_state_change_event(hass, wrapper_entity_id, _state_changed)

    # Todo bus change (item edited)
    hass.bus.async_listen("call_service", _state_will_change, _is_todo_event)

    return True

async def _async_update_entry(hass, event, entry) -> None:
    await sleep(1)
    registry = er.async_get(hass)
    wrapper_entity_id = event.data.get(CONF_ENTITY_ID) or event.data.get('service_data').get(CONF_ENTITY_ID)[0]
    wrapper_state = hass.states.get(wrapper_entity_id)
    name = wrapper_state.name if wrapper_state else "Todolist to entities"
    todo_list = await async_get_todolist_items(hass, wrapper_entity_id)
    existing_entities = [entity for entity in registry.entities.values() if entity.config_entry_id == entry.entry_id]

    for item in todo_list.items:
        entity = TodoListEntity(wrapper_entity_id, item)
        unique_id = entity._attr_unique_id
        if unique_id in [e.unique_id for e in existing_entities]:
            _update_entity(hass, wrapper_entity_id, item.uid, item)
        else:
            await _add_entity(hass, wrapper_entity_id, item.uid, item)
            #await async_reload_entry(hass, entry)
            #return
    for sensor in existing_entities:
        uid = sensor.unique_id.split('_')[-1]
        if uid not in [i.uid for i in todo_list.items]:
            _remove_entity(hass, wrapper_entity_id, uid)
            #await async_reload_entry(hass, entry)
            #return

    # await hass.config_entries.async_unload_platforms(entry, (Platform.SENSOR,))
    # await async_setup_entry(hass, entry)

def _update_entity(hass: HomeAssistant, wrapper_entity_id: str, uid: str, data: TodolistItem) -> None:
    if data is None:
        return
    sensor_entity = hass.data[DOMAIN][wrapper_entity_id][uid]
    registry = er.async_get(hass)
    registry.async_update_entity(sensor_entity.entity_id, name=data.summary)
    sensor_entity.update_todolist_data(data=data)


async def _add_entity(hass: HomeAssistant, wrapper_entity_id: str, uid: str, data: TodolistItem) -> None:
    if data is None:
        return
    async_add_entities = hass.data[DOMAIN][wrapper_entity_id]['async_add_entities']
    platform = hass.data[DOMAIN][wrapper_entity_id]["platform"]
    entity = TodoListEntity(wrapper_entity_id, data)
    hass.data[DOMAIN][wrapper_entity_id][uid] = entity
    await platform.async_add_entities([entity])

def _remove_entity(hass: HomeAssistant, wrapper_entity_id: str, uid: str) -> None:
    sensor_entity = hass.data[DOMAIN][wrapper_entity_id][uid]
    registry = er.async_get(hass)
    registry.async_remove(sensor_entity.entity_id)
    sensor_entity.async_remove()
    del hass.data[DOMAIN][wrapper_entity_id][uid]


async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    def unload():
        hass.async_create_task(
            hass.config_entries.async_forward_entry_unload(
                config_entry, DOMAIN))

    def reload():
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setups(
                config_entry, DOMAIN))

    unload()
    config_entry.async_on_unload(reload)



async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, (Platform.SENSOR,))
