# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry

##  Central class for reading and writing the workspace to file
#
#   This class is created by Application and handles reading and writing workspace files
class WorkspaceFileHandler(object):
    def __init__(self):
        super().__init__()
        self._workspace_readers = []
        self._workspace_writers = []

        PluginRegistry.addType("workspace_reader", self.addReader)
        PluginRegistry.addType("workspace_writer", self.addWriter)
        
    # Try to read the workspace data from a file. Based on the extension in the file a correct workspace reader is selected.
    # \param file_name The name of the workspace file to load.
    # \param storage_device The StorageDevice where the file can be found.
    # \returns Scene node (potentially containing multiple other secene nodes / meshes) if it was able to read the file, None otherwise.
    def read(self, file_name, storage_device):
        try:
            for reader in self._workspace_readers:
                result = reader.read(file_name, storage_device)
                if(result is not None):
                    return result

        except OSError as e:
            Logger.log("e", e)

        Logger.log("w", "Unable to read file %s", file_name)
        return None #unable to read
    
    # Try to write the workspace to file. Based on the extension in the file_name a correct workspace writer is selected.
    # \param file_name The name of the file to write.
    # \param storage_device The StorageDevice where the file should be written to.
    # \param node
    # \returns True if it was able to create the file, otherwise False
    def write(self, file_name, storage_device):
        for writer in self._workspace_writers:
            if writer.write(file_name,storage_device):
                return True
        return False
    
    # Get list of all supported filetypes for writing.
    # \returns List of strings with all supported filetypes.
    def getSupportedFileTypesWrite(self):
        supported_types = []
        for writer in self._mesh_writer:
            supported_types.append(writer.getSupportedExtension())
        return supported_types
    
    # Get list of all supported filetypes for reading.
    # \returns List of strings with all supported filetypes.
    def getSupportedFileTypesRead(self):
        supported_types = []
        for reader in self._mesh_readers:
            supported_types.append(reader.getSupportedExtension())
        return supported_types
        
    def addWriter(self, writer):
        self._workspace_writers.append(writer)
        
    def addReader(self, reader):
        self._workspace_readers.append(reader)