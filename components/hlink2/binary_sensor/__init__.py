import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.components import binary_sensor
from esphome.const import (
    CONF_ID,
    CONF_NAME,
    CONF_LAMBDA,
    CONF_DEST,
    CONF_CUSTOM,
    CONF_UPDATE_INTERVAL,
    CONF_QOS,
    CONF_RAW,
    CONF_STATE,
    ENTITY_CATEGORY_DIAGNOSTIC,
    ICON_BUG,
    ICON_POWER,
)



from .. import hlink2_ns, Core, CONF_HLINK2_ID, CODEOWNERS
from ..mnemonics import Mnemonics, Mnemonic
from ..component import (
    config_schema,
    generate_MessageParameters,
    generate_mnemonic,
    generate_lambda,
    generate_arguments,
    schema_mnemonic,
    CONF_CLIMATE,
    CONF_FILTER_MAINTENANCE,
    CONF_MNEMONIC,
    CONF_PROMOTE,
    ICON_FILTER,
    ICON_HVAC,
    MNEMONIC_CLIMATE,
    MNEMONIC_FILTER_STATUS,
    MNEMONIC_ONOFF,
    SCHEMA_MNEMONIC_PARAMS,
    SCHEMA_MNEMONIC_CUSTOM,
    FINAL_VALIDATE_SCHEMA,
)


DEPENDENCIES = ['binary_sensor']
CODEOWNERS = CODEOWNERS

BinarySensor = hlink2_ns.class_('BinarySensor', binary_sensor.BinarySensor, cg.Component)


COMPONENTS_CONFIG = {
    CONF_STATE: binary_sensor.binary_sensor_schema(BinarySensor,
        icon=ICON_POWER,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ).extend(SCHEMA_MNEMONIC_PARAMS)
    .extend(schema_mnemonic(MNEMONIC_ONOFF)),

    CONF_CLIMATE: binary_sensor.binary_sensor_schema(BinarySensor,
        icon=ICON_HVAC,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ).extend(SCHEMA_MNEMONIC_PARAMS)
    .extend(schema_mnemonic(MNEMONIC_CLIMATE)),

    CONF_FILTER_MAINTENANCE: binary_sensor.binary_sensor_schema(BinarySensor,
        icon=ICON_FILTER,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ).extend(SCHEMA_MNEMONIC_PARAMS)
    .extend(schema_mnemonic(MNEMONIC_FILTER_STATUS)),

    CONF_CUSTOM: binary_sensor.binary_sensor_schema(
        BinarySensor,
        icon=ICON_BUG,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ).extend(SCHEMA_MNEMONIC_CUSTOM)
    .extend(SCHEMA_MNEMONIC_PARAMS),
}


CONFIG_SCHEMA = config_schema(
    CONF_HLINK2_ID,
    Core,
    BinarySensor,
    **COMPONENTS_CONFIG,
)


FINAL_VALIDATE_SCHEMA = FINAL_VALIDATE_SCHEMA


async def to_code(config):
    parent = await cg.get_variable(config[CONF_HLINK2_ID])

    for name, conf in config.items():
        if name in COMPONENTS_CONFIG:
            var = await binary_sensor.new_binary_sensor(conf)
            cg.add(var.set_parent(parent))
            await cg.register_component(var, conf)

            mnemonic_cg = generate_mnemonic(hlink2_ns, conf)
            params_cg = generate_MessageParameters(hlink2_ns, conf)
            
            if lambda_cg := generate_lambda(conf, mnemonic=str(mnemonic_cg), sensor=var):
                cg.add(var.set_mnemonic(*generate_arguments(mnemonic_cg, lambda_cg, params_cg, conf.get(CONF_PROMOTE))))
            else:
                cg.add(var.set_mnemonic_default(*generate_arguments(mnemonic_cg, params_cg, conf.get(CONF_PROMOTE))))

