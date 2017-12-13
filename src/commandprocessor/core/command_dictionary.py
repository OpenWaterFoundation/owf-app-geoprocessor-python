from commandprocessor.commands import CreateLayerList, EditLayerList, ExportLayerList, QgisClip, \
    QgisExtractByAttributes, QgisSimplifyGeometries, ViewLayerListProperties, ViewLayerProperties

command_dictionary = {"CreateLayerList": CreateLayerList.CreateLayerList,
                      "QgisClip": QgisClip.QgisClip,
                      "ExportLayerList": ExportLayerList.ExportLayerList,
                      "QgisSimplifyGeometries": QgisSimplifyGeometries.QgisSimplifyGeometries,
                      "QgisExtractByAttributes": QgisExtractByAttributes.QgisExtractByAttributes,
                      "EditLayerList": EditLayerList.EditLayerList,
                      "ViewLayerProperties": ViewLayerProperties.ViewLayerProperties,
                      "ViewLayerListProperties": ViewLayerListProperties.ViewLayerListProperties}
