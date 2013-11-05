"""Broom main library."""

from .graph import *
from .registry import types
from .client.nativeclient import BroomDBClient, BroomDBObjectNotFoundError
from .client.serializer import BroomObjectSerializer

types.preload()

# TODO: Move the configuration parts somewhere else.
def connect():
    import os
    import json
    configFile = os.getenv('BROOM_CONFIG_FILE')
    config = json.load(open(configFile)).get('broom_db')
    if not config:
        raise RuntimeError("Could not find database configuration.")
    db = BroomDBClient.connect(
            'postgresql+psycopg2://%s:%s@%s:5432/%s' % (
                config.get('db_user'),
                config.get('db_pass'),
                config.get('db_host'),
                config.get('db_name')
                )
            )
    return db

db = connect()



