#!/usr/bin/env python

import argparse
import collections
import json
import sys

class SchemaSpyDriver(object):
    """Wrapper to the Java-based SchemaSpy tool, adding validation, post-
    generation HTML cleanup, simple configuration management, and other
    niceties.

    """
    CONNECTION_SPEC_FORMAT = "jdbc:{subprotocol}://{subname}/{subsubname}"

    def __init__(self, config_file_name):
        """Initializes the driver.

        :param config_file_name: Testing
        :type config_file_name: str

        """
        self.config_file_name = config_file_name
        self.config = json.load(file(config_file_name))

    # TODO: Memoize
    def database_config(self, database_name):
        for database_config in self.config.get("databases", []):
            if database_config["name"] == database_name:
                return collections.defaultdict(lambda: None, database_config)
        return None

    # TODO: Memoize
    def driver_config(self, driver_name):
        for driver_config in self.config.get("drivers", []):
            if driver_config["name"] == driver_name:
                return collections.defaultdict(lambda: None, driver_config)
        return None

    def generate_schemaspy_graphs(self, database_name=None):
        raise NotImplementedError()

    def connection_spec(self, database_name):
        database_config = self.database_config(database_name)
        if not database_config:
            raise RuntimeError(
                    "Configuration for database {} not found in {}".format(
                        database_name, 
                        self.config_file_name
                        )
                    )
        subname = database_config["hostname"]
        if database_config["port"]:
           subname += ":" + str(database_config["port"])
        driver_name = database_config["driver-name"]
        spec = self.CONNECTION_SPEC_FORMAT.format(
            subprotocol = self.driver_config(driver_name)["subprotocol"],
            subname = subname,
            subsubname = database_config["subsubname"]
            )
        if database_config["driver-options"]:
           spec = spec + "?" + "&".join(
               ["=".join([k,v]) for k,v in database_config["driver-options"].items()]
               )
        return spec

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', '-d',
            action='store',
            help='the database configuration for which to generate a schema graph'
            )
    parser.add_argument('--schema', '-s',
            action='store',
            help='a specific schema to model'
            )
    parser.add_argument('--username', '-u',
            action='store',
            help='the username used to connect to the database engine'
            )
    parser.add_argument('--config-file', '-c',
            action='store',
            help='use this configuration file (default: %(default)s)',
            default='schemaspy.json'
            )
    parser.add_argument('--output-directory', '-o',
            action='store',
            help='the directory into which to write the resulting HTML files',
            )

    parser.add_argument('--validate-only', '-V',
            action='store_true',
            default=False,
            help='perform configuration file validation only'
            )

    args = parser.parse_args(argv[1:])
    driver = SchemaSpyDriver(args.config_file)

    # TODO: Execute the actual SchemaSpy Java class calls.


if __name__ == '__main__':
    main(sys.argv)
