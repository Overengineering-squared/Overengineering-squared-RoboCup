import configparser
import json


class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def write_variable(self, section, variable, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        if isinstance(value, list):
            value = json.dumps(value)
        self.config.set(section, variable, str(value))
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def read_variable(self, section, variable):
        if self.config.has_option(section, variable):
            value = self.config.get(section, variable)
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        else:
            return None
