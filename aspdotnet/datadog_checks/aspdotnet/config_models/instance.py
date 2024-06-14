# (C) Datadog, Inc. 2021-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

# This file is autogenerated.
# To change this file you should edit assets/configuration/spec.yaml and then run the following commands:
#     ddev -x validate config -s <INTEGRATION_NAME>
#     ddev -x validate models -s <INTEGRATION_NAME>

from __future__ import annotations

from types import MappingProxyType
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing_extensions import Literal

from datadog_checks.base.utils.functions import identity
from datadog_checks.base.utils.models import validation

from . import defaults, validators


class Counters(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='allow',
        frozen=True,
    )
    aggregate: Optional[Union[bool, Literal['only']]] = None
    average: Optional[bool] = None
    metric_name: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None


class InstanceCounts(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True,
    )
    monitored: Optional[str] = None
    total: Optional[str] = None
    unique: Optional[str] = None


class ExtraMetrics(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True,
    )
    counters: tuple[MappingProxyType[str, Union[str, Counters]], ...]
    exclude: Optional[tuple[str, ...]] = None
    include: Optional[tuple[str, ...]] = None
    instance_counts: Optional[InstanceCounts] = None
    name: str
    tag_name: Optional[str] = None
    use_localized_counters: Optional[bool] = None


class MetricPatterns(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True,
    )
    exclude: Optional[tuple[str, ...]] = None
    include: Optional[tuple[str, ...]] = None


class Metrics(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True,
    )
    counters: tuple[MappingProxyType[str, Union[str, Counters]], ...]
    exclude: Optional[tuple[str, ...]] = None
    include: Optional[tuple[str, ...]] = None
    instance_counts: Optional[InstanceCounts] = None
    name: str
    tag_name: Optional[str] = None
    use_localized_counters: Optional[bool] = None


class InstanceConfig(BaseModel):
    model_config = ConfigDict(
        validate_default=True,
        arbitrary_types_allowed=True,
        frozen=True,
    )
    additional_metrics: Optional[tuple[tuple[str, ...], ...]] = None
    counter_data_types: Optional[tuple[str, ...]] = None
    disable_generic_tags: Optional[bool] = None
    empty_default_hostname: Optional[bool] = None
    enable_health_service_check: Optional[bool] = None
    extra_metrics: Optional[MappingProxyType[str, ExtraMetrics]] = None
    host: Optional[str] = None
    metric_patterns: Optional[MetricPatterns] = None
    metrics: Optional[MappingProxyType[str, Metrics]] = None
    min_collection_interval: Optional[float] = None
    namespace: Optional[str] = Field(None, pattern='\\w*')
    password: Optional[str] = None
    server: Optional[str] = None
    server_tag: Optional[str] = None
    service: Optional[str] = None
    tags: Optional[tuple[str, ...]] = None
    use_legacy_check_version: Optional[bool] = None
    username: Optional[str] = None

    @model_validator(mode='before')
    def _initial_validation(cls, values):
        return validation.core.initialize_config(getattr(validators, 'initialize_instance', identity)(values))

    @field_validator('*', mode='before')
    def _validate(cls, value, info):
        field = cls.model_fields[info.field_name]
        field_name = field.alias or info.field_name
        if field_name in info.context['configured_fields']:
            value = getattr(validators, f'instance_{info.field_name}', identity)(value, field=field)
        else:
            value = getattr(defaults, f'instance_{info.field_name}', lambda: value)()

        return validation.utils.make_immutable(value)

    @model_validator(mode='after')
    def _final_validation(cls, model):
        return validation.core.check_model(getattr(validators, 'check_instance', identity)(model))
