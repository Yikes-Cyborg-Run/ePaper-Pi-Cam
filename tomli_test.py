import tomli
from pathlib import Path


def load_config(config_path):
    try:
        with open(config_path, "rb") as f:
            data = tomli.load(f)
        return(data)
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return None
    except tomli.TOMLDecodeError as e:
        print(f"Error: TOML parsing error: {e}")
        return None

config = load_config("config.toml")

white=config['whitebalance']

print(white)

"""
def load_config(file_path):
    try:
        with open(file_path, "r") as f:
            return tomli.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return None
    except tomli.TOMLDecodeError as e:
        print(f"Error: TOML parsing error: {e}")
        return None

config = load_config(Path("config.toml"))

if config:
    print(f"WB: {config['whitebalance']}")
else:
    print("no config")

"""