# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Qt.ListModel import ListModel
from UM.Application import Application

from PyQt5.QtCore import Qt, pyqtSlot


class MachinesModel(ListModel):
    NameRole = Qt.UserRole + 1
    ActiveRole = Qt.UserRole + 2

    def __init__(self):
        super().__init__()

        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.ActiveRole, "active")

        Application.getInstance().machinesChanged.connect(self._onMachinesChanged)
        Application.getInstance().activeMachineChanged.connect(self._onActiveMachineChanged)
        self._onMachinesChanged()

    @pyqtSlot()
    def reload(self):
        app = Application.getInstance()
        app.setActiveMachine(app.getActiveMachine())

    @pyqtSlot(int)
    def setActive(self, index):
        app = Application.getInstance()
        app.setActiveMachine(app.getMachines()[index])

    @pyqtSlot(int)
    def removeMachine(self, index):
        app = Application.getInstance()
        app.removeMachine(app.getMachines()[index])
        app.setActiveMachine(app.getMachines()[0])

    def _onMachinesChanged(self):
        self.clear()
        for machine in Application.getInstance().getMachines():
            self.appendItem({ "id": id(machine), "name": machine.getName(), "active": Application.getInstance().getActiveMachine() == machine })

    def _onActiveMachineChanged(self):
        activeMachine = Application.getInstance().getActiveMachine()
        for index in range(len(self.items)):
            self.setProperty(index, "active", id(activeMachine) == self.items[index]["id"])
