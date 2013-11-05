import broom
import json
import os

from .client.nativeclient import BroomDBClient

class BroomConfig(BroomObject):

    @broom.field(broom.Settable)
    def ConfigFile(self):
        return

    @broom.field
    def _ConfigStored(self):
        if self.ConfigFile():
            return json.load(open(self.ConfigFile()))

    @broom.field(broom.Settable)
    def Config(self):
        return self._ConfigStored()

class BroomEnv(broom.BroomObject):

    # TODO: If any of these settings is changed, and we've
    #       already 'connected' to the associated database,
    #       then update the current default broom.db accordingly.

    @broom.field(broom.Settable)
    def BroomConfig(self):
        return BroomConfig()

    @broom.field
    def BroomDBServiceURI(self):
        """The URI of the BroomDB service to use."""
        return self.BroomConfig().Config().get("broom_db_service_uri")

    @broom.field
    def BroomDBHost(self):
        return self.BroomConfig().Config().get("broom_db", {}).get("db_host")

    @broom.field
    def BroomDBName(self):
        """The name of the database to connect to."""
        return self.BroomConfig().Config().get("broom_db", {}).get("db_name")

    @broom.field
    def BroomDBUser(self):
        """The name of the database to connect to."""
        return self.BroomConfig().Config().get("broom_db", {}).get("db_user")

    @broom.field
    def BroomDBPassword(self):
        """The name of the database to connect to."""
        return self.BroomConfig().Config().get("broom_db", {}).get("db_pass")

    @broom.field
    def BroomDBClient(self):
        return BroomDBClient.connect()
