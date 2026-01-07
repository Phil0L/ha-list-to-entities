# Todolist to entities for Home Assistant

A Home Assistant integration to turn any todo list into seperate sensor entities for each todo list item.
This is very useful for dashboard cards like [Lovelace-auto-entities](https://github.com/thomasloven/lovelace-auto-entities) and many other use cases.

## Features

- **UI Configuration** - No YAML required, easy setup through Home Assistant UI
- **Simple usage** - The entities are automatically created, updated and deleted accordingly.

### System Requirements

- **Local To-do integration**: This requires the todo integration to be installed

## Installation

### Method 1: HACS (Recommended)

1. **Install HACS** (if not already installed):
   - Open Home Assistant and go to **Settings** → **Add-ons, Backups & Supervisor** → **Add-on Store**
   - Search for "HACS" and install it following the official [HACS installation guide](https://hacs.xyz/docs/setup/download)

2. **Add Custom Repository**:
   - In HACS, go to **Settings** → **Custom repositories**
   - Add this repository: `https://https://github.com/Phil0L/ha-list-to-entities`
   - Select **Integration** as the category

3. **Install the Integration**:
   - Go to **HACS** → **Integrations**
   - Search for "To-do Entities"
   - Click **Download** and restart Home Assistant when prompted

4. **Configure the Integration**:
   - Go to **Settings** → **Devices & services** → **Add Integration**
   - Search for "To-do Entities" and select it
   - Follow the configuration steps below

### Method 2: Manual Installation

1. **Download the Integration**:
   - Clone or download this repository to any temporary folder on your machine, then copy only the component folder into Home Assistant:

   ```bash
   # On your workstation or HA host shell
   git clone https://github.com/Phil0L/ha-list-to-entities.git
   cp -R list_to_entities/custom_components/escpos_printer /config/custom_components/
   ```

2. **Restart Home Assistant**:
   - Go to **Settings** → **System** → **Restart** to load the new integration

3. **Configure the Integration**:
   - Follow the configuration steps in the next section


### Configuration

1. **Add the Integration**:
   - Go to **Settings** → **Devices & services** → **Add Integration**
   - Search for "To-do Entities" and click it

2. **Configure Todolist**:
   - **Todolist**: Select the todolist you want to create entities for

### Building

This integration follows Home Assistant's integration structure. See the [Home Assistant Developer Documentation](https://developers.home-assistant.io/docs/creating_integration_file_structure) for details.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.