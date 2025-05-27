import json
import os
import minecraft_launcher_lib as mc
import uuid

mc_dir = mc.utils.get_minecraft_directory()
user_file = os.path.join(mc_dir, "user.json")

def load_user():
    if os.path.exists(user_file):
        try:
            with open(user_file, "r") as f:
                return json.load(f)
        except:
            pass
    return {"username": None, "uuid": None, "night_mode": False}


def save_user(username=None, uuid_val=None, night_mode=False, last_instance=None):
    if uuid_val is None:
        uuid_val = str(uuid.uuid4())

    data = {
        "username": username,
        "uuid": uuid_val,
        "night_mode": night_mode,
        "last_instance": last_instance
    }

    os.makedirs(mc_dir, exist_ok=True)

    with open(user_file, "w") as file:
        json.dump(data, file, indent=4)