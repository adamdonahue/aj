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
    config_file = os.getenv('BROOM_CONFIG_FILE')
    if config_file and os.path.exists(config_file):
        with open(config_file) as f:
            config = json.load(f)
            if not config:
                return
#    if not config:
#        raise RuntimeError("Could not find database configuration.")
#    db = BroomDBClient.connect(
#            'postgresql+psycopg2://%s:%s@%s:5432/%s' % (
#                config.get('db_user'),
#                config.get('db_pass'),
#                config.get('db_host'),
#                config.get('db_name')
#                )
#            )
    db = BroomDBClient.connect(
            'sqlite:///:memory:'
            )
    return db

db = connect()



