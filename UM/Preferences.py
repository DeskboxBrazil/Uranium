# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, SignalEmitter
from UM.Logger import Logger
from UM.Resources import Resources

import os
import configparser

##      Preferences are application based settings that are saved for future use.
#       Typical preferences would be window size, standard machine, etc.
class Preferences(SignalEmitter):
    def __init__(self):
        super().__init__()

        self._file = None
        self._parser = None
        self._preferences = {}

    def addPreference(self, key, default_value):
        preference = self._findPreference(key)
        if preference:
            preference.setDefault(default_value)
            return

        group, key = self._splitKey(key)
        if group not in self._preferences:
            self._preferences[group] = {}

        self._preferences[group][key] = _Preference(key, default_value)

    def setValue(self, key, value):
        preference = self._findPreference(key)
        if preference:
            preference.setValue(value)
            self.preferenceChanged.emit(key)

    def getValue(self, key):
        preference = self._findPreference(key)
        if preference:
            return preference.getValue()
        return None

    def resetPreference(self, key):
        preference = self._findPreference(key)
        if preference:
            preference.setValue(preference.getDefault())
            self.preferenceChanged.emit(key)

    def readFromFile(self, file):
        self._loadFile(file)

        if not self._parser:
            return

        for group, group_entries in self._parser.items():
            if group == "DEFAULT":
                continue

            if group not in self._preferences:
                self._preferences[group] = {}

            for key, value in group_entries.items():
                if key not in self._preferences[group]:
                    self._preferences[group][key] = _Preference(key)

                self._preferences[group][key].setValue(value)
                self.preferenceChanged.emit("{0}/{1}".format(group, key))

    def writeToFile(self, file):
        parser = configparser.ConfigParser()
        for group, group_entries in self._preferences.items():
            parser[group] = {}
            for key, pref in group_entries.items():
                if pref.getValue() != pref.getDefault():
                    parser[group][key] = str(pref.getValue())

        parser["general"]["version"] = "2"

        with open(file, "wt") as f:
            parser.write(f)

    preferenceChanged = Signal()

    @classmethod
    def getInstance(cls):
        if not cls._instance:
            cls._instance = Preferences()

        return cls._instance

    def _splitKey(self, key):
        group = "general"
        key = key

        if "/" in key:
            parts = key.split("/")
            group = parts[0]
            key = parts[1]

        return (group, key)

    def _findPreference(self, key):
        group, key = self._splitKey(key)

        if group in self._preferences:
            if key in self._preferences[group]:
                return self._preferences[group][key]

        return None

    def _loadFile(self, file):
        if self._file and self._file == file:
            return self._parser

        self._parser = configparser.ConfigParser()
        self._parser.read(file)

        if self._parser["general"]["version"] != "2":
            Logger.log("w", "Old config file found, ignoring")
            self._parser = None
            return

        del self._parser["general"]["version"]

    _instance = None

class _Preference:
    def __init__(self, name, default = None, value = None):
        self._name = name
        self._default = default
        self._value = default if value == None else value

    def getName(self):
        return self._name

    def getValue(self):
        return self._value

    def getDefault(self):
        return self._default

    def setDefault(self, default):
        self._default = default

    def setValue(self, value):
        self._value = value
