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


def main():
    config_manager = ConfigManager('config.ini')

    # Writing a variable
    config_manager.write_variable('Section1', 'ArrayVariable', [1, 2, 3, 4, 5])
    config_manager.write_variable('Section1', 'IntVariable', 123)
    config_manager.write_variable('Section1', 'FloatVariable', 123.456)
    config_manager.write_variable('Section1', 'StringVariable', 'Hello')

    # Reading a config value
    array_value = config_manager.read_variable('Section1', 'ArrayVariable')  # [1, 2, 3, 4, 5]
    int_value = int(config_manager.read_variable('Section1', 'IntVariable'))  # 123
    float_value = float(config_manager.read_variable('Section1', 'FloatVariable'))  # 123.456
    string_value = config_manager.read_variable('Section1', 'StringVariable')  # 'Hello'

    print(type(int_value), int_value)
    print(type(float_value), float_value)
    print(type(string_value), string_value)
    print(type(array_value), array_value)


if __name__ == "__main__":
    main()
