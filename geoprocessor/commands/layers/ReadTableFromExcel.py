import geoprocessor.util.qgis_util as qgis_util
from qgis.core import QgsApplication, QgsVectorJoinInfo, QgsMapLayerRegistry


QgsApplication.setPrefixPath(r"C:\OSGeo4W\apps\qgis", True)
qgs = QgsApplication([], False)
qgs.initQgis()


uri = r"C:\Users\intern1\trilynx-dev\system-map\Timeline\2018-03-23-ClientList\TriLynx-NovaStar-Client-YearEnd2017.xlsx"
client_table = qgis_util.read_qgsvectorlayer_from_excel_worksheet(uri)
config_table = qgis_util.read_qgsvectorlayer_from_excel_worksheet(uri, 1)
web_table = qgis_util.read_qgsvectorlayer_from_excel_worksheet(uri, 2)



for table in [client_table, config_table, web_table]:

    print [attr_field.name() for attr_field in table.pendingFields()]

# Add Selection Criteria from config table to client table
QgsMapLayerRegistry.instance().addMapLayers([client_table, config_table])
client_field = "Client Name"
config_field = "Client "
joinObject = QgsVectorJoinInfo()
joinObject.joinLayerId = config_table.id()
joinObject.joinFieldName = config_field
joinObject.targetFieldName = client_field
joinObject.memoryCache = True
client_table.addJoin(joinObject)

print [attr_field.name() for attr_field in client_table.pendingFields()]
