# [hlink2] Custom Component Documentation

## Overview
`hlink2` is a custom ESPHome component that communicates with Hitachi AC units over UART using an undocumented protocol (called by convenience *hlink2*). It enables control and monitoring of indoor units (IDU) and outdoor units (ODU).

## Core Configuration
### Main Component Setup

```yaml
hlink2:
  id: hlink2ac
  uart_id: hitachi_bus
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | string | *required* | Component identifier for internal references |
| `uart_id` | string | *required* | ID of the UART bus communicating with the AC unit |

### Advanced Parameters

```yaml
parameters:
  task_timeout: 30ms                    # Component task timeout (keep under 50ms)
  uart_tx_chunck_size: 16               # Bytes sent at once over UART
  message_mnemonics_capacity: 13        # Max distinct mnemonics per message
  message_update_interval: 30s          # Default message polling interval
  message_update_timeout: 4s            # Message processing delay
```

## Custom Mnemonics

Define custom mnemonics to extend functionality:

```yaml
mnemonics:
  - name: Func1
    mode: [STS, CMD]           # Status/Command modes
    dest: IDU                  # Destination: IDU or ODU
```

## Supported Components

### Climate (HVAC Control)

```yaml
climate:
  - platform: hlink2
    name: "Hitachi AC"
    hvac_actions: true
    command:
      buzzer: true             # Enable buzzer on commands
      qos: high                # Quality of Service: low/medium/high
    status:
      update_interval: 5s      # Polling frequency
      qos: low
    visual:
      min_temperature: 16.0
      max_temperature: 32.0
      temperature_step:
        target_temperature: 0.5
        current_temperature: 0.5
```

### Sensor (Read-Only Values)

**Built-in Sensors:**
- `outdoor_temperature`
- `indoor_temperature`
- `indoor_humidity`
- `filter_usage`
- `energy`
- `power`
- `airflow`
- `indoor_exchanger`
- `outdoor_exchanger`

```yaml
sensor:
  - platform: hlink2
    outdoor_temperature:
      name: "outdoor_temperature"
      update_interval: 10s
      promote: true            # Group in lower-interval messages
      qos: low
  - platform: hlink2
    custom:
      name: "Custom sensor"
      mnemonic: IDU_Func1
      state_class: measurement
      update_interval: 10s
      promote: true
```

### Switch (On/Off Control)

**Built-in Switches:**
- `buzzer`
- `led_wifi`
- `led_timer`
- `preset_eco`

```yaml
switch:
  - platform: hlink2
    buzzer:
      name: "buzzer"
  - platform: hlink2
    custom:
      name: "Custom switch"
      mnemonic:
        name: Func1
        dest: IDU
      buzzer: true
```

### Button

```yaml
button:
  - platform: hlink2
    filter_reset:
      name: "reset_filter"
  - platform: hlink2
    custom:
      name: "Custom button"
      mnemonic: IDU_Func1
      value: 1                 # Value to send
      raw: true                # Send without quotes
      buzzer: true
      qos: high
```

### Select (Multiple Options)

```yaml
select:
  - platform: hlink2
    custom:
      name: "Custom select"
      mnemonic: IDU_Func1
      options:
        - '0'
        - '1'
        - 'any raw value'
      raw: true
      buzzer: true
      qos: medium
```

### Number (Numeric Control)

```yaml
number:
  - platform: hlink2
    target_temperature:
      name: "target_temperature"
  - platform: hlink2
    custom:
      name: "Custom number"
      mnemonic: IDU_Func1
      min_value: 0
      max_value: 10
      step: 1
      buzzer: true
      qos: medium
```

### Text & Text Sensor

```yaml
text:
  - platform: hlink2
    custom:
      name: "Func1"
      mnemonic: IDU_Func1
      mode: text               # esphome text mode
      raw: true
      buzzer: true
      qos: high

text_sensor:
  - platform: hlink2
    model:
      name: "model"
      update_interval: 1h
      promote: false
      qos: high
```

## Common Options

These options are shared across most hlink2 components:

| Option | Type | Values | Description |
|--------|------|--------|-------------|
| `buzzer` | bool | true/false | Enable buzzer feedback on commands |
| `qos` | string | low/medium/high | Retry behavior and timeout scaling |
| `update_interval` | time | e.g., 10s | How often to poll the value |
| `promote` | bool | true/false | Include mnemonic in lower-interval messages to reduce UART traffic |
| `raw` | bool | true/false | Send values without surrounding quotes |
| `mnemonic` | string or object | e.g., `IDU_Func1` or `{name: Func1, dest: IDU}` | Mnemonic identifier |

## Custom Message Action (Lambda)

Send custom messages via lambda:

```yaml
esphome:
  on_boot:
    - lambda: |-
        id(hlink2ac).action_custom_message(
          "CMD_IDU",                                    # Message type
          std::vector<std::string>{"Mode:33", "OnOf:1"}, # Mnemonics
          3                                             # Priority/retry count
        );
```

## Installation

```yaml
external_components:
  - source:
      type: git
      url: https://github.com/clsergent/hitachi_altwifi.git
    components: [hlink2]
    refresh: 0s              # Set to 0s to force recompilation
```

## Dependencies

- **UART**: Must be configured with the AC unit's connection parameters
- **API**: Required for `action_custom_message` functionality
- **Network & Logger**: Optional but recommended for debugging