import tomli

def load_config(file_path):
    """Loads a TOML configuration file."""
    try:
        with open(file_path, "rb") as f:
            return tomli.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return None
    except tomli.TOMLDecodeError as e:
        print(f"Error: TOML parsing error: {e}")
        return None

config = load_config(r"C:/Users/ckingsbury/OneDrive - City of Port Orange/Desktop/ePaperPiCam/ePaper-Pi-Cam/config.toml")

if config:
    print(f"WB: {config['whitebalance']}")
else:
    print("no config")    