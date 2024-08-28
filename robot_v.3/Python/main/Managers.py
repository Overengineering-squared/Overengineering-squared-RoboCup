import configparser
import json
import time

import numpy as np


class ConfigManager:
    def __init__(self, config_file):
        self.__config_file = config_file
        self.__config = configparser.ConfigParser()
        self.__config.read(config_file)

    def write_variable(self, section, variable, value):
        if not self.__config.has_section(section):
            self.__config.add_section(section)
        if isinstance(value, list):
            value = json.dumps(value)
        self.__config.set(section, variable, str(value))
        with open(self.__config_file, 'w') as configfile:
            self.__config.write(configfile)

    def read_variable(self, section, variable):
        if self.__config.has_option(section, variable):
            value = self.__config.get(section, variable)
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        else:
            return None


class Timer:
    def __init__(self):
        self.__timer_arr = np.array([["none", 1, 0, 0]])

    def remove_timer(self, name):
        self.__timer_arr = self.__timer_arr[np.where(self.__timer_arr[:, 0] != name)]

    def set_timer(self, name, set_time):
        self.remove_timer(name)
        self.__timer_arr = np.append(self.__timer_arr, [[name, time.perf_counter(), set_time, False]], axis=0)

    def __update_timer(self):
        for i, timer in enumerate(self.__timer_arr):
            if not timer[0] == "none":
                self.__timer_arr[i, 3] = (time.perf_counter() - float(timer[1])) > float(timer[2])

    def get_timer(self, name):
        self.__update_timer()
        time_val = self.__timer_arr[np.where(self.__timer_arr[:, 0] == name), 3]

        if time_val.size > 0:
            return time_val[0][0] == "True"
        else:
            return False
