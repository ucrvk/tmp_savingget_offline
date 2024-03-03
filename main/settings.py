from json import dump, load
from filehandle import dafaultDirectory
from typing import Union

defaultJson = {
    "gameDirectory": {
        "saving": dafaultDirectory[0],
        "game": dafaultDirectory[1],
    },
}
defaultDlc = {
    "dlcs": [
        "dlc_balkan_w.scs",
        "dlc_feldbinder.scs",
        "dlc_krone.scs",
        "dlc_iberia.scs",
        "dlc_north.scs",
        "dlc_balt.scs",
        "dlc_fr.scs",
        "dlc_it.scs",
        "dlc_east.scs",
        "dlc_balkan_e.scs"
    ]
}


def settingLoad() -> Union[dict, Exception]:
    """
    Loads the settings.json file and returns a dictionary
    """
    try:
        with open("settings.json", "r") as f:
            return load(f)
    except FileNotFoundError:
        with open("settings.json", "w") as f:
            dump(defaultJson, f, indent=4)
            return defaultJson
    except Exception as e:
        return e


def Dlcload() -> Union[dict, Exception]:
    try:
        with open("dlc.json", "r") as f:
            return load(f)
    except FileNotFoundError:
        return defaultDlc["dlcs"]
    except Exception as e:
        return e


def settingSave(settings: dict) -> Union[bool, Exception]:
    """
    Saves the settings.json file
    """
    try:
        with open("settings.json", "w") as f:
            dump(settings, f, indent=4)
        return True
    except Exception as e:
        return e


def emptyDirectoryDectec(dectetJson: dict) -> bool:
    """
    Checks if the directory is empty
    """
    if (
        dectetJson["gameDirectory"]["saving"] == ""
        or dectetJson["gameDirectory"]["game"] == ""
    ):
        return True
    else:
        return False
