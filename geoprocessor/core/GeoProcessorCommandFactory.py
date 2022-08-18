# GeoProcessorCommandFactory - class to instantiate a command from is string representation
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2020 Open Water Foundation
# 
# GeoProcessor is free software:  you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     GeoProcessor is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with GeoProcessor.  If not, see <https://www.gnu.org/licenses/>.
# ________________________________________________________________NoticeEnd___

import logging

import geoprocessor.util.command_util as command_util

# Cannot import AbstractCommand for type hint because it results in a circular dependency
# from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.commands.datastore.CloseDataStore import CloseDataStore
from geoprocessor.commands.datastore.OpenDataStore import OpenDataStore
from geoprocessor.commands.datastore.RunSql import RunSql

from geoprocessor.commands.logging.Message import Message
from geoprocessor.commands.logging.StartLog import StartLog

from geoprocessor.commands.map.AddGeoLayerViewToGeoMap import AddGeoLayerViewToGeoMap
from geoprocessor.commands.map.AddGeoLayerViewGroupToGeoMap import AddGeoLayerViewGroupToGeoMap
from geoprocessor.commands.map.AddGeoMapToGeoMapProject import AddGeoMapToGeoMapProject
from geoprocessor.commands.map.CreateGeoMap import CreateGeoMap
from geoprocessor.commands.map.CreateGeoMapProject import CreateGeoMapProject
from geoprocessor.commands.map.SetGeoLayerViewCategorizedSymbol import SetGeoLayerViewCategorizedSymbol
from geoprocessor.commands.map.SetGeoLayerViewEventHandler import SetGeoLayerViewEventHandler
from geoprocessor.commands.map.SetGeoLayerViewGraduatedSymbol import SetGeoLayerViewGraduatedSymbol
from geoprocessor.commands.map.SetGeoLayerViewSingleSymbol import SetGeoLayerViewSingleSymbol
# from geoprocessor.commands.map.WriteGeoMapToJSON import WriteGeoMapToJSON
from geoprocessor.commands.map.WriteGeoMapProjectToJSON import WriteGeoMapProjectToJSON

from geoprocessor.commands.raster.ChangeRasterGeoLayerCRS import ChangeRasterGeoLayerCRS
from geoprocessor.commands.raster.CreateRasterGeoLayer import CreateRasterGeoLayer
from geoprocessor.commands.raster.RasterizeGeoLayer import RasterizeGeoLayer
from geoprocessor.commands.raster.RearrangeRasterGeoLayerBands import RearrangeRasterGeoLayerBands
from geoprocessor.commands.raster.ReadRasterGeoLayerFromFile import ReadRasterGeoLayerFromFile
from geoprocessor.commands.raster.ReadRasterGeoLayerFromWebMapService import ReadRasterGeoLayerFromWebMapService
from geoprocessor.commands.raster.ReadRasterGeoLayerFromTileMapService import ReadRasterGeoLayerFromTileMapService
from geoprocessor.commands.raster.WriteRasterGeoLayerToFile import WriteRasterGeoLayerToFile

from geoprocessor.commands.running.EndFor import EndFor
from geoprocessor.commands.running.EndIf import EndIf
from geoprocessor.commands.running.Exit import Exit
from geoprocessor.commands.running.For import For
from geoprocessor.commands.running.If import If
from geoprocessor.commands.running.RunCommands import RunCommands
from geoprocessor.commands.running.RunGdalProgram import RunGdalProgram
from geoprocessor.commands.running.RunOgrProgram import RunOgrProgram
from geoprocessor.commands.running.RunProgram import RunProgram
from geoprocessor.commands.running.QgisAlgorithmHelp import QgisAlgorithmHelp
from geoprocessor.commands.running.SetProperty import SetProperty
from geoprocessor.commands.running.SetPropertyFromGeoLayer import SetPropertyFromGeoLayer
from geoprocessor.commands.running.WritePropertiesToFile import WritePropertiesToFile

from geoprocessor.commands.table.ReadTableFromDataStore import ReadTableFromDataStore
from geoprocessor.commands.table.ReadTableFromDelimitedFile import ReadTableFromDelimitedFile
from geoprocessor.commands.table.ReadTableFromExcel import ReadTableFromExcel
from geoprocessor.commands.table.WriteTableToDelimitedFile import WriteTableToDelimitedFile
from geoprocessor.commands.table.WriteTableToDataStore import WriteTableToDataStore
from geoprocessor.commands.table.WriteTableToExcel import WriteTableToExcel

from geoprocessor.commands.testing.CompareFiles import CompareFiles
from geoprocessor.commands.testing.CreateRegressionTestCommandFile import CreateRegressionTestCommandFile
from geoprocessor.commands.testing.StartRegressionTestResultsReport import StartRegressionTestResultsReport

from geoprocessor.commands.util.Blank import Blank
from geoprocessor.commands.util.Comment import Comment
from geoprocessor.commands.util.CommentBlockEnd import CommentBlockEnd
from geoprocessor.commands.util.CommentBlockStart import CommentBlockStart
from geoprocessor.commands.util.CopyFile import CopyFile
from geoprocessor.commands.util.CreateFolder import CreateFolder
from geoprocessor.commands.util.FTPGet import FTPGet
from geoprocessor.commands.util.ListFiles import ListFiles
from geoprocessor.commands.util.RemoveFile import RemoveFile
from geoprocessor.commands.util.UnknownCommand import UnknownCommand
from geoprocessor.commands.util.UnzipFile import UnzipFile
from geoprocessor.commands.util.WebGet import WebGet
from geoprocessor.commands.util.WriteCommandSummaryToFile import WriteCommandSummaryToFile

from geoprocessor.commands.vector.AddGeoLayerAttribute import AddGeoLayerAttribute
from geoprocessor.commands.vector.ChangeGeoLayerGeometry import ChangeGeoLayerGeometry
from geoprocessor.commands.vector.ClipGeoLayer import ClipGeoLayer
from geoprocessor.commands.vector.CopyGeoLayer import CopyGeoLayer
from geoprocessor.commands.vector.CreateGeoLayerFromGeometry import CreateGeoLayerFromGeometry
from geoprocessor.commands.vector.FixGeoLayer import FixGeoLayer
from geoprocessor.commands.vector.FreeGeoLayers import FreeGeoLayers
from geoprocessor.commands.vector.IntersectGeoLayer import IntersectGeoLayer
from geoprocessor.commands.vector.MergeGeoLayers import MergeGeoLayers
from geoprocessor.commands.vector.ReadGeoLayerFromDelimitedFile import ReadGeoLayerFromDelimitedFile
from geoprocessor.commands.vector.ReadGeoLayerFromGeoJSON import ReadGeoLayerFromGeoJSON
from geoprocessor.commands.vector.ReadGeoLayerFromKML import ReadGeoLayerFromKML
from geoprocessor.commands.vector.ReadGeoLayerFromShapefile import ReadGeoLayerFromShapefile
from geoprocessor.commands.vector.ReadGeoLayerFromWebFeatureService import ReadGeoLayerFromWebFeatureService
from geoprocessor.commands.vector.ReadGeoLayersFromFGDB import ReadGeoLayersFromFGDB
from geoprocessor.commands.vector.ReadGeoLayersFromGeoPackage import ReadGeoLayersFromGeoPackage
from geoprocessor.commands.vector.ReadGeoLayersFromFolder import ReadGeoLayersFromFolder
from geoprocessor.commands.vector.RemoveGeoLayerAttributes import RemoveGeoLayerAttributes
from geoprocessor.commands.vector.RemoveGeoLayerFeatures import RemoveGeoLayerFeatures
from geoprocessor.commands.vector.RenameGeoLayerAttribute import RenameGeoLayerAttribute
from geoprocessor.commands.vector.SetGeoLayerAttribute import SetGeoLayerAttribute
from geoprocessor.commands.vector.SetGeoLayerCRS import SetGeoLayerCRS
from geoprocessor.commands.vector.SetGeoLayerProperty import SetGeoLayerProperty
from geoprocessor.commands.vector.SimplifyGeoLayerGeometry import SimplifyGeoLayerGeometry
from geoprocessor.commands.vector.SplitGeoLayerByAttribute import SplitGeoLayerByAttribute
from geoprocessor.commands.vector.WriteGeoLayerPropertiesToFile import WriteGeoLayerPropertiesToFile
from geoprocessor.commands.vector.WriteGeoLayerToDelimitedFile import WriteGeoLayerToDelimitedFile
from geoprocessor.commands.vector.WriteGeoLayerToGeoJSON import WriteGeoLayerToGeoJSON
from geoprocessor.commands.vector.WriteGeoLayerToKML import WriteGeoLayerToKML
from geoprocessor.commands.vector.WriteGeoLayerToShapefile import WriteGeoLayerToShapefile


class GeoProcessorCommandFactory(object):
    """
    Factory to create command instances by examining command string.
    Only instantiates the command instance but does not parse the command string.
    The command string is parsed within the command class instance.
    """

    # TODO smalers 2018-07-27 evaluate whether the following is needed
    # The dictionary of all available commands, in alphabetical order.
    # key: the name of the command (converted to all UPPERCASE)
    # value: the constructor (__init__) function to create an instance of the command
    # This dictionary serves two purposes:
    # 1) It provides a registry of all commands known to the geoprocessor (via this factory class)
    # 2) It provides the list of constructor functions to call, to simplify logic
    registered_commands = {
        "ADDGEOLAYERATTRIBUTE": AddGeoLayerAttribute(),
        "ADDGEOLAYERVIEWGROUPTOGEOMAP": AddGeoLayerViewGroupToGeoMap(),
        "ADDGEOLAYERVIEWTOGEOMAP": AddGeoLayerViewToGeoMap(),
        "ADDGEOMAPTOGEOMAPPROJECT": AddGeoMapToGeoMapProject(),
        "BLANK": Blank(),  # Actually has no name, is whitespace only
        "CHANGEGEOLAYERGEOMETRY": ChangeGeoLayerGeometry(),
        "CHANGERASTERGEOLAYERCRS": ChangeRasterGeoLayerCRS(),
        "CLIPGEOLAYER": ClipGeoLayer(),
        "CLOSEDATASTORE": CloseDataStore(),
        "COMMENT": Comment(),
        "COMMENTBLOCKEND": CommentBlockEnd(),
        "COMMENTBLOCKSTART": CommentBlockStart(),
        "COMPAREFILES": CompareFiles(),
        "COPYFILE": CopyFile(),
        "COPYGEOLAYER": CopyGeoLayer(),
        "COPYGEOMAP": CreateGeoMap(),
        "COPYGEOMAPPROJECT": CreateGeoMapProject(),
        "CREATEFOLDER": CreateFolder(),
        "CREATEGEOLAYERFROMGEOMETRY": CreateGeoLayerFromGeometry(),
        "CREATERASTERGEOLAYER": CreateRasterGeoLayer(),
        "CREATEREGRESSIONTESTCOMMANDFILE": CreateRegressionTestCommandFile(),
        "ENDFOR": EndFor(),
        "ENDIF": EndIf(),
        "EXIT": Exit(),
        "FIXGEOLAYER": FixGeoLayer(),
        "FOR": For(),
        "FREEGEOLAYERS": FreeGeoLayers(),
        "FTPGET": FTPGet(),
        "IF": If(),
        "INTERSECTGEOLAYER": IntersectGeoLayer(),
        "LISTFILES": ListFiles(),
        "MERGEGEOLAYERS": MergeGeoLayers(),
        "MESSAGE": Message(),
        "OPENDATASTORE": OpenDataStore(),
        "QGISALGORITHMHELP": QgisAlgorithmHelp(),
        "RASTERIZEGEOLAYER": RasterizeGeoLayer(),
        "READGEOLAYERFROMDELIMITEDFILE": ReadGeoLayerFromDelimitedFile(),
        "READGEOLAYERFROMGEOJSON": ReadGeoLayerFromGeoJSON(),
        "READGEOLAYERFROMKML": ReadGeoLayerFromKML(),
        "READGEOLAYERFROMSHAPEFILE": ReadGeoLayerFromShapefile(),
        "READGEOLAYERFROMWEBFEATURESERVICE": ReadGeoLayerFromWebFeatureService(),
        "READGEOLAYERSFROMFGDB": ReadGeoLayersFromFGDB(),
        "READGEOLAYERSFROMGEOPACKAGE": ReadGeoLayersFromGeoPackage(),
        "READGEOLAYERSFROMFOLDER": ReadGeoLayersFromFolder(),
        "READRASTERGEOLAYERFROMFILE": ReadRasterGeoLayerFromFile(),
        "READRASTERGEOLAYERFROMTILEMAPSERVICE": ReadRasterGeoLayerFromTileMapService(),
        "READRASTERGEOLAYERFROMWEBMAPSERVICE": ReadRasterGeoLayerFromWebMapService(),
        "READTABLEFROMDATASTORE": ReadTableFromDataStore(),
        "READTABLEFROMDELIMITEDFILE": ReadTableFromDelimitedFile(),
        "READTABLEFROMEXCEL": ReadTableFromExcel(),
        "REARRANGERASTERGEOLAYERBANDS": RearrangeRasterGeoLayerBands(),
        "REMOVEFILE": RemoveFile(),
        "REMOVEGEOLAYERATTRIBUTES": RemoveGeoLayerAttributes(),
        "RENAMEGEOLAYERATTRIBUTE": RenameGeoLayerAttribute(),
        "REMOVEGEOLAYERFEATURES": RemoveGeoLayerFeatures(),
        "RUNCOMMANDS": RunCommands(),
        "RUNGDALPROGRAM": RunGdalProgram(),
        "RUNOGRPROGRAM": RunOgrProgram(),
        "RUNPROGRAM": RunProgram(),
        "RUNSQL": RunSql(),
        "SETGEOLAYERATTRIBUTE": SetGeoLayerAttribute(),
        "SETGEOLAYERCRS": SetGeoLayerCRS(),
        "SETGEOLAYERPROPERTY": SetGeoLayerProperty(),
        "SETGEOLAYERVIEWCATEGORIZEDSYMBOL": SetGeoLayerViewCategorizedSymbol(),
        "SETGEOLAYERVIEWGRADUATEDSYMBOL": SetGeoLayerViewGraduatedSymbol(),
        "SETGEOLAYERVIEWEVENTHANDLER": SetGeoLayerViewEventHandler(),
        "SETGEOLAYERVIEWSINGLESYMBOL": SetGeoLayerViewSingleSymbol(),
        "SETPROPERTY": SetProperty(),
        "SETPROPERTYFROMGEOLAYER": SetPropertyFromGeoLayer(),
        "SIMPLIFYGEOLAYERGEOMETRY": SimplifyGeoLayerGeometry(),
        "SPLITGEOLAYERBYATTRIBUTE": SplitGeoLayerByAttribute(),
        "STARTLOG": StartLog(),
        "STARTREGRESSIONTESTRESULTSREPORT": StartRegressionTestResultsReport(),
        "UNZIPFILE": UnzipFile(),
        "WEBGET": WebGet(),
        "WRITECOMMANDSUMMARYTOFILE": WriteCommandSummaryToFile(),
        "WRITEGEOLAYERPROPERTIESTOFILE": WriteGeoLayerPropertiesToFile(),
        "WRITEGEOLAYERTODELIMITEDFILE": WriteGeoLayerToDelimitedFile(),
        "WRITEGEOLAYERTOGEOJSON": WriteGeoLayerToGeoJSON(),
        "WRITEGEOLAYERTOKML": WriteGeoLayerToKML(),
        "WRITEGEOLAYERTOSHAPEFILE": WriteGeoLayerToShapefile(),
        "WRITERASTERGEOLAYERTOFILE": WriteRasterGeoLayerToFile(),
        "WRITETABLETODELIMITEDFILE": WriteTableToDelimitedFile(),
        "WRITETABLETODATASTORE": WriteTableToDataStore(),
        "WRITETABLETOEXCEL": WriteTableToExcel(),
        "WRITEPROPERTIESTOFILE": WritePropertiesToFile()
    }

    def __init__(self) -> None:
        pass

    def __is_command_valid(self, command_name: str) -> bool:
        """
        Checks if the command is a valid registered command by examining the command name.
        A valid command can be further processed to create a command instance.

        Args:
            command_name: the name of the command

        Returns:
            True if the command is registered as recognized, False if not.
        """

        registered_command_names = list(self.registered_commands.keys())
        if command_name.upper() in registered_command_names:
            return True
        else:
            return False

    def new_command(self, command_string: str,
                    create_unknown_command_if_not_recognized: bool = True):
        """
        Creates the object of a command class called from a command line of the command file.

        Args:
            command_string (str): the command string or just the command name
            create_unknown_command_if_not_recognized (bool) If TRUE, create an UnknownCommand when the input
            command is not recognized, if FALSE, throw an error.

        Returns:
            A command instance of class type that matches the command name.
            The command is not parsed.

        Raises:
            ValueError if the command is not recognized and create_unknown_command_if_not_recognized=False.
        """

        logger = logging.getLogger(__name__)

        # Get command name from the first part of the command.
        command_string_trimmed = command_string.strip()
        paren_pos = command_string_trimmed.find('(')

        # If the command is any variation of a comment return the
        # appropriate unique command editor
        if command_string_trimmed == "":
            # Empty line
            return Blank()
        elif command_string_trimmed.startswith('#'):
            return Comment()
        elif command_string_trimmed.startswith('/*'):
            return CommentBlockStart()
        elif command_string_trimmed.startswith('*/'):
            return CommentBlockEnd()

        # Assume command of syntax CommandName(Param1="...",Param2="...")
        else:
            if paren_pos >= 0:
                # Get command name from command string CommandName(...)
                # - command name is before the first open parenthesis
                command_name = command_util.parse_command_name_from_command_string(command_string_trimmed)
            else:
                # Get command name from command string:  CommandName
                # - command name is the string
                # - TODO smalers 2020-03-11 evaluate whether to allow this or generate an error
                command_name = command_string_trimmed

            # Initialize the command class object if it is a valid command.
            command_name_upper = command_name.upper()
            init_from_dictionary_constructor = False
            if init_from_dictionary_constructor:
                # TODO smalers 2017-12-28 Figure out if the dictionary constructor can be called.
                # The following is a clever way to initialize instances using a constructor function
                # from the command dictionary.
                # However, it does not seem to work.  For example, if multiple Message commands
                # are initialized, the AbstractCommand.command_parameters dictionary for all Message
                # command instances will have the values corresponding to the last Message command.
                if self.__is_command_valid(command_name):
                    command = self.registered_commands[command_name_upper]
                    return command
            else:
                # Constructing the following way always seems to work properly
                # - Alphabetize the commands.

                # A commands
                if command_name_upper == "ADDGEOLAYERATTRIBUTE":
                    return AddGeoLayerAttribute()
                elif command_name_upper == "ADDGEOLAYERVIEWGROUPTOGEOMAP":
                    return AddGeoLayerViewGroupToGeoMap()
                elif command_name_upper == "ADDGEOLAYERVIEWTOGEOMAP":
                    return AddGeoLayerViewToGeoMap()
                elif command_name_upper == "ADDGEOMAPTOGEOMAPPROJECT":
                    return AddGeoMapToGeoMapProject()

                # B commands
                elif command_name_upper == "BLANK":
                    return Blank()

                # C commands
                elif command_name_upper == "CHANGEGEOLAYERGEOMETRY":
                    return ChangeGeoLayerGeometry()
                elif command_name_upper == "CHANGERASTERGEOLAYERCRS":
                    return ChangeRasterGeoLayerCRS()
                elif command_name_upper == "CLIPGEOLAYER":
                    return ClipGeoLayer()
                # Comment, CommentBlockStart, and CommentBlockEnd are checked for above
                # - might be able to treat similar to other commands but need to confirm out parsing is done
                elif command_name_upper == "CLOSEDATASTORE":
                    return CloseDataStore()
                elif command_name_upper == "COMPAREFILES":
                    return CompareFiles()
                elif command_name_upper == "COPYFILE":
                    return CopyFile()
                elif command_name_upper == "COPYGEOLAYER":
                    return CopyGeoLayer()
                elif command_name_upper == "CREATEFOLDER":
                    return CreateFolder()
                elif command_name_upper == "CREATEGEOLAYERFROMGEOMETRY":
                    return CreateGeoLayerFromGeometry()
                elif command_name_upper == "CREATEGEOMAP":
                    return CreateGeoMap()
                elif command_name_upper == "CREATEGEOMAPPROJECT":
                    return CreateGeoMapProject()
                elif command_name_upper == "CREATERASTERGEOLAYER":
                    return CreateRasterGeoLayer()
                elif command_name_upper == "CREATEREGRESSIONTESTCOMMANDFILE":
                    return CreateRegressionTestCommandFile()

                # E commands
                elif command_name_upper == "ENDFOR":
                    return EndFor()
                elif command_name_upper == "ENDIF":
                    return EndIf()
                elif command_name_upper == "EXIT":
                    return Exit()

                # F commands
                elif command_name_upper == "FIXGEOLAYER":
                    return FixGeoLayer()
                elif command_name_upper == "FOR":
                    return For()
                elif command_name_upper == "FREEGEOLAYERS":
                    return FreeGeoLayers()
                elif command_name_upper == "FTPGET":
                    return FTPGet()

                # I commands
                elif command_name_upper == "IF":
                    return If()
                elif command_name_upper == "INTERSECTGEOLAYER":
                    return IntersectGeoLayer()

                # L commands
                elif command_name_upper == "LISTFILES":
                    return ListFiles()

                # M commands
                elif command_name_upper == "MERGEGEOLAYERS":
                    return MergeGeoLayers()
                elif command_name_upper == "MESSAGE":
                    return Message()

                # O commands
                elif command_name_upper == "OPENDATASTORE":
                    return OpenDataStore()

                # Q commands
                elif command_name_upper == "QGISALGORITHMHELP":
                    return QgisAlgorithmHelp()

                # R commands
                elif command_name_upper == "RASTERIZEGEOLAYER":
                    return RasterizeGeoLayer()
                elif command_name_upper == "READGEOLAYERFROMDELIMITEDFILE":
                    return ReadGeoLayerFromDelimitedFile()
                elif command_name_upper == "READGEOLAYERFROMGEOJSON":
                    return ReadGeoLayerFromGeoJSON()
                elif command_name_upper == "READGEOLAYERFROMKML":
                    return ReadGeoLayerFromKML()
                elif command_name_upper == "READGEOLAYERFROMSHAPEFILE":
                    return ReadGeoLayerFromShapefile()
                elif command_name_upper == "READGEOLAYERFROMWEBFEATURESERVICE":
                    return ReadGeoLayerFromWebFeatureService()
                elif command_name_upper == "READGEOLAYERSFROMFGDB":
                    return ReadGeoLayersFromFGDB()
                elif command_name_upper == "READGEOLAYERSFROMGEOPACKAGE":
                    return ReadGeoLayersFromGeoPackage()
                elif command_name_upper == "READGEOLAYERSFROMFOLDER":
                    return ReadGeoLayersFromFolder()
                elif command_name_upper == "READRASTERGEOLAYERFROMFILE":
                    return ReadRasterGeoLayerFromFile()
                elif command_name_upper == "READRASTERGEOLAYERFROMTILEMAPSERVICE":
                    return ReadRasterGeoLayerFromTileMapService()
                elif command_name_upper == "READRASTERGEOLAYERFROMWEBMAPSERVICE":
                    return ReadRasterGeoLayerFromWebMapService()
                elif command_name_upper == "READTABLEFROMDATASTORE":
                    return ReadTableFromDataStore()
                elif command_name_upper == "READTABLEFROMDELIMITEDFILE":
                    return ReadTableFromDelimitedFile()
                elif command_name_upper == "READTABLEFROMEXCEL":
                    return ReadTableFromExcel()
                elif command_name_upper == "REARRANGERASTERGEOLAYERBANDS":
                    return RearrangeRasterGeoLayerBands()
                elif command_name_upper == "REMOVEFILE":
                    return RemoveFile()
                elif command_name_upper == "REMOVEGEOLAYERATTRIBUTES":
                    return RemoveGeoLayerAttributes()
                elif command_name_upper == "REMOVEGEOLAYERFEATURES":
                    return RemoveGeoLayerFeatures()
                elif command_name_upper == "RENAMEGEOLAYERATTRIBUTE":
                    return RenameGeoLayerAttribute()
                elif command_name_upper == "RUNCOMMANDS":
                    return RunCommands()
                elif command_name_upper == "RUNGDALPROGRAM":
                    return RunGdalProgram()
                elif command_name_upper == "RUNOGRPROGRAM":
                    return RunOgrProgram()
                elif command_name_upper == "RUNPROGRAM":
                    return RunProgram()
                elif command_name_upper == "RUNSQL":
                    return RunSql()

                # S commands
                elif command_name_upper == "SETGEOLAYERATTRIBUTE":
                    return SetGeoLayerAttribute()
                elif command_name_upper == "SETGEOLAYERCRS":
                    return SetGeoLayerCRS()
                elif command_name_upper == "SETGEOLAYERPROPERTY":
                    return SetGeoLayerProperty()
                elif command_name_upper == "SETGEOLAYERVIEWCATEGORIZEDSYMBOL":
                    return SetGeoLayerViewCategorizedSymbol()
                elif command_name_upper == "SETGEOLAYERVIEWEVENTHANDLER":
                    return SetGeoLayerViewEventHandler()
                elif command_name_upper == "SETGEOLAYERVIEWGRADUATEDSYMBOL":
                    return SetGeoLayerViewGraduatedSymbol()
                elif command_name_upper == "SETGEOLAYERVIEWSINGLESYMBOL":
                    return SetGeoLayerViewSingleSymbol()
                elif command_name_upper == "SETPROPERTY":
                    return SetProperty()
                elif command_name_upper == "SETPROPERTYFROMGEOLAYER":
                    return SetPropertyFromGeoLayer()
                elif command_name_upper == "SIMPLIFYGEOLAYERGEOMETRY":
                    return SimplifyGeoLayerGeometry()
                elif command_name_upper == "SPLITGEOLAYERBYATTRIBUTE":
                    return SplitGeoLayerByAttribute()
                elif command_name_upper == "STARTLOG":
                    return StartLog()
                elif command_name_upper == "STARTREGRESSIONTESTRESULTSREPORT":
                    return StartRegressionTestResultsReport()

                # U commands
                elif command_name_upper == "UNZIPFILE":
                    return UnzipFile()

                # W commands
                elif command_name_upper == "WEBGET":
                    return WebGet()
                elif command_name_upper == "WRITECOMMANDSUMMARYTOFILE":
                    return WriteCommandSummaryToFile()
                elif command_name_upper == "WRITEGEOLAYERPROPERTIESTOFILE":
                    return WriteGeoLayerPropertiesToFile()
                elif command_name_upper == "WRITEGEOLAYERTODELIMITEDFILE":
                    return WriteGeoLayerToDelimitedFile()
                elif command_name_upper == "WRITEGEOLAYERTOGEOJSON":
                    return WriteGeoLayerToGeoJSON()
                elif command_name_upper == "WRITEGEOLAYERTOKML":
                    return WriteGeoLayerToKML()
                elif command_name_upper == "WRITEGEOLAYERTOSHAPEFILE":
                    return WriteGeoLayerToShapefile()
                # elif command_name_upper == "WRITEGEOMAPTOJSON":
                #     return WriteGeoMapToJSON()
                elif command_name_upper == "WRITEGEOMAPPROJECTTOJSON":
                    return WriteGeoMapProjectToJSON()
                elif command_name_upper == "WRITEPROPERTIESTOFILE":
                    return WritePropertiesToFile()
                elif command_name_upper == "WRITERASTERGEOLAYERTOFILE":
                    return WriteRasterGeoLayerToFile()
                elif command_name_upper == "WRITETABLETODELIMITEDFILE":
                    return WriteTableToDelimitedFile()
                elif command_name_upper == "WRITETABLETODATASTORE":
                    return WriteTableToDataStore()
                elif command_name_upper == "WRITETABLETOEXCEL":
                    return WriteTableToExcel()

            # If here the command name was not matched.
            # Don't know the command so create an UnknownCommand or throw an exception.
            if create_unknown_command_if_not_recognized:
                logger.warning("Command line is unknown command. Adding UnknownCommand: " + command_string_trimmed)
                return UnknownCommand()
            else:
                logger.warning("Command line is unknown syntax.")
                raise ValueError('Unrecognized command "' + command_string + '"')

        # The syntax is not recognized so create an UnknownCommand or throw an exception.
        # else:
        #    if create_unknown_command_if_not_recognized:
        #        logger.warning("Command line is unknown syntax. Adding UnknownCommand: " + command_string_trimmed)
        #        return UnknownCommand()
        #    else:
        #        logger.warning("Command line is unknown syntax.")
        #        raise ValueError('Unrecognized command "' + command_string + '"')
