import os
import json

import importlib.util
from pathlib import Path
import inspect

from .base_config import BaseConfig

def save_config(stats_path, config_dir="edpac/config"):
    """
    Loops over all *_config.py files in config_dir and saves
    their class attributes as JSON in stats_path.
    """
    # Ensure the target directory exists
    stats_dir = Path(stats_path)
    stats_dir.mkdir(parents=True, exist_ok=True)


    # 1. Get the absolute path of constants.py
    current_file = Path(__file__).resolve()
    print(current_file)

    # 2. Go up the folder tree to find the project root
    # (In your case: constants.py -> config/ -> edpac/ -> src/ -> ROOT)
    # Adjust the number of .parent calls to match your actual structure
    PROJECT_ROOT = current_file.parent
    print(PROJECT_ROOT)

    config_dir = os.path.join(PROJECT_ROOT)

    config_path = Path(config_dir)
    print(config_path)
    print(os.getcwd())

    print(list(config_path.glob("*_config.py")))

    # 1. Loop over files ending in _config.py
    for config_file in config_path.glob("*_config.py"):
        print(config_file.name)
        if config_file.name == "base_config.py":
            print("base_config, skipping")
            continue

        print("** Processing ", config_file)
        module_name = config_file.stem

        # 2. Dynamically import the module
        spec = importlib.util.spec_from_file_location(module_name, config_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 3. Find classes in the module
        for name, obj in inspect.getmembers(module, inspect.isclass):


            print(f"{name=}, {obj=}")

            # We only want classes defined in that file,
            # and (optionally) inheriting from BaseConfig
            if issubclass(obj, BaseConfig) and obj is not BaseConfig:
            #if obj.__module__ == module_name:
                json_filename = f"{module_name}_{name}.json".lower()
                target_file = stats_dir / json_filename

                # 4. Save to JSON
                # If you use BaseConfig, call .to_dict().
                # Otherwise, use a fallback vars() filter.
                if hasattr(obj, 'to_dict'):
                    data = obj.to_dict()
                else:
                    data = {k: v for k, v in vars(obj).items()
                            if not k.startswith('__') and not callable(v)}

                with open(target_file, 'w') as f:
                    json.dump(data, f, indent=4)

                print(f"[Config] Saved {name} from {config_file.name} to {json_filename}")
