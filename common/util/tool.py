import os
import json

VALID_ENV_NAMES = ["prod", "test", "dev"]


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as infile:
            return json.load(infile)
    except Exception as exp:
        raise UnboundLocalError(f'{filepath} load file as json error! {exp}')


def is_valid_env(env_name):
    return env_name in VALID_ENV_NAMES


def get_env_name(env_field):
    env_name = os.getenv(env_field)
    if is_valid_env(env_name):
        return env_name
    else:
        raise ValueError(f"invalid env name: {env_name}")
