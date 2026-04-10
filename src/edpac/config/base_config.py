import json
import os

from enum import Enum


class BaseConfig:
    @classmethod
    def to_dict(cls):
        """Extracts attributes, converting Enums to strings for JSON safety."""
        data = {}
        for k, v in cls.__dict__.items():
            if k.startswith('__') or callable(v):
                continue

            # Handle Enum serialization
            if isinstance(v, Enum):
                data[k] = v.name  # or v.value depending on your preference
            else:
                data[k] = v
        return data
    @classmethod
    def save_json(cls, path):
        """Saves the configuration to a JSON file."""
        with open(path, 'w') as f:
            json.dump(cls.to_dict(), f, indent=4)
