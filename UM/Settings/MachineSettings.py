# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import collections
import configparser
import json
import os.path

from UM.i18n import i18nCatalog
from UM.Resources import Resources
from UM.Settings.Setting import Setting
from UM.Settings.SettingsCategory import SettingsCategory
from UM.Settings.Validators.ResultCodes import ResultCodes
from UM.Signal import Signal, SignalEmitter


MODES_VISIBILITY = [
    # basic
    'layer_height,layer_height_0,wall_thickness',
    # intermediate
    'layer_height,layer_height_0,wall_thickness,top_bottom_thickness,wall_overlap_avoid_enabled,top_bottom_pattern,skin_outline_count,xy_offset,material_print_temperature,material_diameter,material_flow,retraction_enable,speed_print,speed_travel,speed_layer_0,speed_slowdown_layers,fill_sparse_density,fill_overlap,fill_sparse_thickness,cool_fan_enabled,cool_fan_full_at_height,cool_min_layer_time,cool_min_layer_time_fan_speed_max,cool_min_speed,cool_lift_head,support_enable,support_type,support_angle,support_xy_distance,support_z_distance,support_bottom_stair_step_height,support_join_distance,support_area_smoothing,support_use_towers,support_minimal_diameter,support_tower_diameter,support_tower_roof_angle,support_pattern,support_connect_zigzags,support_fill_rate,adhesion_type,skirt_line_count,skirt_gap,skirt_minimal_length,brim_line_count,raft_margin,raft_line_spacing,raft_base_thickness,raft_base_linewidth,raft_base_speed,raft_interface_thickness,raft_interface_linewidth,raft_airgap,raft_surface_layers,magic_spiralize,wireframe_enabled,wireframe_printspeed,wireframe_flow,wireframe_top_delay,wireframe_bottom_delay,wireframe_flat_delay,wireframe_up_half_speed,wireframe_top_jump,wireframe_fall_down,wireframe_drag_along,wireframe_strategy,wireframe_straight_before_down,wireframe_roof_fall_down,wireframe_roof_drag_along,wireframe_roof_outer_delay,wireframe_height,wireframe_roof_inset,wireframe_nozzle_clearance',
    # advanced
    'layer_height,layer_height_0,wall_line_count,wall_line_width,top_thickness,bottom_thickness,wall_overlap_avoid_enabled,top_bottom_pattern,skin_outline_count,xy_offset,material_print_temperature,material_diameter,material_flow,retraction_enable,retraction_speed,retraction_amount,retraction_min_travel,retraction_combing,retraction_minimal_extrusion,retraction_hop,speed_infill,speed_wall,speed_topbottom,speed_support,speed_travel,skirt_speed,speed_slowdown_layers,fill_pattern,infill_line_distance,fill_overlap,fill_sparse_combine,cool_fan_speed,cool_fan_full_layer,cool_min_layer_time,cool_min_layer_time_fan_speed_max,cool_min_speed,cool_lift_head,support_enable,support_type,support_angle,support_xy_distance,support_top_distance,support_bottom_distance,support_bottom_stair_step_height,support_join_distance,support_area_smoothing,support_use_towers,support_minimal_diameter,support_tower_diameter,support_tower_roof_angle,support_pattern,support_connect_zigzags,support_line_distance,adhesion_type,skirt_line_count,skirt_gap,skirt_minimal_length,brim_line_count,raft_margin,raft_line_spacing,raft_base_thickness,raft_base_linewidth,raft_base_speed,raft_interface_thickness,raft_interface_linewidth,raft_airgap,raft_surface_layers,magic_spiralize,wireframe_enabled,wireframe_printspeed_bottom,wireframe_printspeed_up,wireframe_printspeed_down,wireframe_printspeed_flat,wireframe_flow_connection,wireframe_flow_flat,wireframe_top_delay,wireframe_bottom_delay,wireframe_flat_delay,wireframe_up_half_speed,wireframe_top_jump,wireframe_fall_down,wireframe_drag_along,wireframe_strategy,wireframe_straight_before_down,wireframe_roof_fall_down,wireframe_roof_drag_along,wireframe_roof_outer_delay,wireframe_height,wireframe_roof_inset,wireframe_nozzle_clearance',
    # expert
    'layer_height,layer_height_0,wall_line_count,wall_line_width_0,wall_line_width_x,skirt_line_width,skin_line_width,infill_line_width,support_line_width,top_layers,bottom_layers,wall_overlap_avoid_enabled,top_bottom_pattern,skin_outline_count,xy_offset,material_print_temperature,material_diameter,material_flow,retraction_enable,retraction_retract_speed,retraction_prime_speed,retraction_amount,retraction_min_travel,retraction_combing,retraction_minimal_extrusion,retraction_hop,speed_infill,speed_wall_0,speed_wall_x,speed_topbottom,speed_support,speed_travel,skirt_speed,speed_slowdown_layers,fill_pattern,infill_line_distance,fill_overlap,fill_sparse_combine,cool_fan_speed_min,cool_fan_speed_max,cool_fan_full_layer,cool_min_layer_time,cool_min_layer_time_fan_speed_max,cool_min_speed,cool_lift_head,support_enable,support_type,support_angle,support_xy_distance,support_top_distance,support_bottom_distance,support_bottom_stair_step_height,support_join_distance,support_area_smoothing,support_use_towers,support_minimal_diameter,support_tower_diameter,support_tower_roof_angle,support_pattern,support_connect_zigzags,support_line_distance,adhesion_type,skirt_line_count,skirt_gap,skirt_minimal_length,brim_line_count,raft_margin,raft_line_spacing,raft_base_thickness,raft_base_linewidth,raft_base_speed,raft_interface_thickness,raft_interface_linewidth,raft_airgap,raft_surface_layers,magic_spiralize,wireframe_enabled,wireframe_printspeed_bottom,wireframe_printspeed_up,wireframe_printspeed_down,wireframe_printspeed_flat,wireframe_flow_connection,wireframe_flow_flat,wireframe_top_delay,wireframe_bottom_delay,wireframe_flat_delay,wireframe_up_half_speed,wireframe_top_jump,wireframe_fall_down,wireframe_drag_along,wireframe_strategy,wireframe_straight_before_down,wireframe_roof_fall_down,wireframe_roof_drag_along,wireframe_roof_outer_delay,wireframe_height,wireframe_roof_inset,wireframe_nozzle_clearance'
]


class MachineSettings(SignalEmitter):
    def __init__(self):
        super().__init__()
        self._categories = []
        self._platform_mesh = None
        self._platform_texture = None
        self._name = "Unknown Machine",
        self._type_name = "Unknown"
        self._type_id = "unknown"
        self._icon = "unknown.png",
        self._machine_settings = []   ## Settings that don't have a category are 'fixed' (eg; they can not be changed by the user, unless they change the json)
        self._i18n_catalog = None

    ##  Load settings from JSON file. Used to load tree structure & default values etc from file.
    #   \param file_name String
    def loadSettingsFromFile(self, file_name):
        with open(file_name, "rt", -1, "utf-8") as f:
            data = json.load(f, object_pairs_hook=collections.OrderedDict)

        self._i18n_catalog = i18nCatalog(os.path.basename(file_name))

        if "id" in data:
            self._type_id = data["id"]

        if "platform" in data:
            self._platform_mesh = data["platform"]

        if "platform_texture" in data:
            self._platform_texture = data["platform_texture"]

        if "name" in data:
            self._type_name = data["name"]

        if "icon" in data:
            self._icon = data["icon"]

        if "inherits" in data:
            inherits_from = MachineSettings()
            inherits_from.loadSettingsFromFile(os.path.dirname(file_name) + "/" + data["inherits"])
            self._machine_settings = inherits_from._machine_settings
            self._categories = inherits_from._categories

        if "machine_settings" in data:
            for key, value in data["machine_settings"].items():
                setting = self.getSettingByKey(key)
                if not setting:
                    setting = Setting(key, self._i18n_catalog)
                    self.addSetting(setting)
                setting.fillByDict(value)

        if "categories" in data:
            for key, value in data["categories"].items():
                category = self.getSettingsCategory(key)
                if not category:
                    category = SettingsCategory(key, self._i18n_catalog, self)
                    self.addSettingsCategory(category)
                category.fillByDict(value)

        for setting in self.getAllSettings():
            setting.valueChanged.connect(self.settingChanged)

        self.settingsLoaded.emit() #Emit signal that all settings are loaded (some setting stuff can only be done when all settings are loaded (eg; the conditional stuff)
    settingsLoaded = Signal()

    ##  Load values of settings from file.
    def loadValuesFromFile(self, file_name):
        config = configparser.ConfigParser()
        config.read(file_name)

        if not self._categories:
            self.loadSettingsFromFile(Resources.getPath(Resources.SettingsLocation, config["General"]["type"] + ".json"))

        self._name = config.get("General", "name", fallback = "Unknown Machine")

        visibility = config.get("General", "visibility", fallback = None)
        if visibility:
            values = visibility.split(",")
            for setting in self.getAllSettings():
                if setting.getKey() in values:
                    setting.setVisible(True)
                else:
                    setting.setVisible(False)

        for name, section in config.items():
            for key in section:
                setting = self.getSettingByKey(key)
                if setting is not None:
                    setting.setValue(section[key])

    ##  Save setting values to file
    def saveValuesToFile(self, file_name):
        config = configparser.ConfigParser()

        config.add_section("General")
        config["General"]["type"] = self._type_id
        config["General"]["name"] = self._name
        config["General"]["visibility"] = self._getVisibleSettings()

        for category in self._categories:
            configData = {}
            for setting in category.getAllSettings():
                if setting.isVisible() and setting.isActive():
                    configData[setting.getKey()] = setting.getValue()
            config[category.getKey()] = configData

        with open(file_name, "w") as f:
            config.write(f)


    def getTypeName(self):
        return self._type_name

    def getTypeID(self):
        return self._type_id

    ##  Add a category of settings
    def addSettingsCategory(self, category):
        self._categories.append(category)

    ##  Get setting category by key
    #   \param key Category key to get.
    #   \return category or None if key was not found.
    def getSettingsCategory(self, key):
        for category in self._categories:
            if category.getKey() == key:
                return category
        return None

    ##  Get all categories.
    #   \returns list of categories
    def getAllCategories(self):
        return self._categories

    ##  Get all settings of this machine
    #   \param kwargs Keyword arguments.
    #                 Possible values are:
    #                 * include_machine: boolean, true if machine settings should be included. Default false.
    #   \return list of settings
    def getAllSettings(self, **kwargs):
        all_settings = []
        if kwargs.get("include_machine", False):
            all_settings.extend(self._machine_settings)

        for category in self._categories:
            all_settings.extend(category.getAllSettings())
        return all_settings

    ##  Get setting by key.
    #   \param key Key to select setting by (string)
    #   \return Setting or none if no setting was found.
    def getSettingByKey(self, key):
        for category in self._categories:
            setting = category.getSettingByKey(key)
            if setting is not None:
                return setting
        for setting in self._machine_settings:
            setting = setting.getSettingByKey(key)
            if setting is not None:
                return setting
        return None #No setting found

    ##  Add (machine) setting to machine.
    def addSetting(self, setting):
        self._machine_settings.append(setting)
        setting.valueChanged.connect(self.settingChanged)

    ##  Set the value of a setting by key.
    #   \param key Key of setting to change.
    #   \param value value to set.
    def setSettingValueByKey(self, key, value):
        setting = self.getSettingByKey(key)
        if setting is not None:
            setting.setValue(value)

    ##  Get the value of setting by key.
    #   \param key Key of the setting to get value from
    #   \return value (or none)
    def getSettingValueByKey(self, key):
        setting = self.getSettingByKey(key)
        if setting is not None:
            return setting.getValue()
        return None

    settingChanged = Signal()

    ##  Get the machine mesh (in most cases platform)
    #   Todo: Might need to rename this to get machine mesh?
    def getPlatformMesh(self):
        return self._platform_mesh

    def getPlatformTexture(self):
        return self._platform_texture

    ##  Return the machine name.
    def getName(self):
        return self._name

    ##  Set the machine name
    #
    #   \param name The name of the machine.
    def setName(self, name):
        self._name = name

    ##  Returns the machine"s icon.
    def getIcon(self):
        return self._icon

    ##  Return whether there is any setting that is in an "Error" state.
    def hasErrorValue(self):
        settings = self.getAllSettings()
        for setting in settings:
            result = setting.validate()
            if result == ResultCodes.max_value_error or result == ResultCodes.min_value_error:
                return True

        return False

    ##  Return whether there is any setting that is in a "Warning" state.
    def hasWarningValue(self):
        settings = self.getAllSettings()
        for setting in settings:
            result = setting.validate()
            if result == ResultCodes.max_value_warning or result == ResultCodes.min_value_warning:
                return True

        return False

    def _getVisibleSettings(self):
        visible = []
        settings = self.getAllSettings()
        for setting in settings:
            if setting.isVisible():
                visible.append(setting.getKey())

        return ",".join(visible)
