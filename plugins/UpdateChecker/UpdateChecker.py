# Copyright (c) 2015 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Extension import Extension
from UM.Logger import Logger
from UM.i18n import i18nCatalog
import urllib.request
import platform
from UM.Application import Application
import json
import codecs
import webbrowser
from threading import Thread
from UM.Message import Message

i18n_catalog = i18nCatalog("uranium")

## This extention checks for new versions of the application based on the application name and the version number.
#  The plugin is currently only usuable for applications maintained by Ultimaker. But it should be relatively easy
#  to change it to work for other applications.
class UpdateChecker(Extension):
    def __init__(self):
        super().__init__()
        self.addMenuItem(i18n_catalog.i18n("Check for Updates"), self.checkNewVersion)
        self._url = None

        thread = Thread(target = self.checkNewVersion)
        thread.daemon = True
        thread.start()

    ##  Callback for the message that is spawned when there is a new version.
    def actionTriggered(self, message, action):
        if action == "download":
            if self._url is not None:
                webbrowser.open(self._url)

    ##  Connect with software.ultimaker.com, load latest.json and check version info.
    #   If the version info is higher then the current version, spawn a message to
    #   allow the user to download it.
    def checkNewVersion(self):
        application_name = Application.getInstance().getApplicationName()
        Logger.log("i", "Checking for new version of %s" % application_name)

        try:
            latest_version_file = urllib.request.urlopen("http://deskboxbrazil.github.io/latest.json")
        except Exception as e:
            Logger.log("e", "Failed to check for new version. %s" %e)
            return

        try:
            reader = codecs.getreader("utf-8")
            data = json.load(reader(latest_version_file))
            try:
                local_version = list(map(int, Application.getInstance().getVersion().split(".")))
            except ValueError:
                Logger.log("w", "Could not determine application version from string %s, not checking for updates", Application.getInstance().getVersion())
                return

            if application_name in data:
                for key, value in data[application_name].items():
                    if "major" in value and "minor" in value and "revision" in value and "url" in value:
                        os = key
                        if platform.system() == os: #TODO: add architecture check
                            newest_version = [int(value["major"]), int(value["minor"]), int(value["revision"])]
                            if local_version < newest_version:
                                Logger.log("i", "Found a new version of the software. Spawning message")
                                message = Message(i18n_catalog.i18n("A new version is available!"))
                                message.addAction("download", "Download", "[no_icon]", "[no_description]")
                                self._url = value["url"]
                                message.actionTriggered.connect(self.actionTriggered)
                                message.show()
                                break
                    else:
                        Logger.log("e", "Could not find version information or download url for update.")
            else:
                Logger.log("e", "Did not find any version information for %s." % application_name)
        except Exception as e:
            Logger.log("e", "Exception in update checker: %s" % (e))
