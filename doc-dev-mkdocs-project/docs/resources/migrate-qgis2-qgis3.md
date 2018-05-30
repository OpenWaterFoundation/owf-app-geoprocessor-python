# Notes on Migration of the GeoProcessor from QGIS2 to QGIS3

This documentation notes the changes that were made to the GeoProcessor to migrate it from the QGIS2 environment to the QGIS3 environment. 

## Helpful Resources

[QGIS API Documentation: Backwards Incompatible Changes](https://qgis.org/api/api_break.html)

## How to import additional Python packages

1. Open `OsGeo4W` shell
2. Enter `set PYTHONHOME=C:\OSGeo4W64\apps\Python36`
3. Enter `py -m pip install pandas`
4. Enter `py -m pip install requests[security]`
5. Enter `py -m pip install openpyxl`

## Log of Changes made to Commands to Have all GP Tests Pass

The log of changes is organized by command. 

### AddGeoLayerAttribute

**Error:** 

`orig_attribute_field_names = [attr_field.name() for attr_field in qgsvectorlayer.pendingFields()]` <br>
`AttributeError: 'QgsVectorLayer' object has no attribute 'pendingFields'`

**Explanation:** 

`pendingFields()` is now `fields()`

See [GitHub Pull Request: Drop old pending* aliases from QgsVectorLayer](https://github.com/qgis/QGIS/pull/6050).

**Error:**

`attr_index = qgsvectorlayer.fieldNameIndex(attribute_name)`<br>
`AttributeError: 'QgsVectorLayer' object has no attribute 'fieldNameIndex'`

**Explanation:** 

`fieldNameIndex` has been renamed to `lookupField`<br>
`layer.fieldNameIndex(name)` now is `layer.fields().lookupField(name)`

See [QGIS API Documentation: Backwards Incompatible Changes](https://qgis.org/api/api_break.html).

**Additional Commands that had this error:**

RemoveGeoLayerAttributes, RenameGeoLayerAttributes


### ClipGeoLayer

**Errors:**

`clipped_output = general.runalg("qgis:clip",`<br>
`AttributeError: module 'plugins.processing.tools.general' has no attribute 'runalg'`


`_core.QgsProcessingException: Error: Algorithm qgis:clip not found`

**Explanation:**

No longer use the `general.run()` function. Instead use the `self.command.qgis_processor.runAlgorithm` function. Set up the qgis processor when initializing the GeoProcessor. Must add the `QgsNativeAlgorithms()` provider. Output products are no longer a string pointing to the output vector layer location (in memory) but is the output `QgsVectorLayer` object. 

See [StackExchange - QGIS 3.0 Error when calling processing.runalg()](https://gis.stackexchange.com/questions/274764/qgis-3-0-error-when-calling-processing-runalg).<br>
See [StackExchange - Using QGIS3 Processing algorithms from standalone PyQGIS scripts (outside of GUI)](https://gis.stackexchange.com/questions/279874/using-qgis3-processing-algorithms-from-standalone-pyqgis-scripts-outside-of-gui/279937)

**Additional Commands that had this error:**

SetGeoLayerCRS, IntersectGeoLayer, SimplifyGeoLayerGeometry, MergeGeoLayers

### CopyGeoLayer

**Error:**

`qgs_expression.prepare(qgsvectorlayer.fields())`<br>
`TypeError: QgsExpression.prepare(): argument 1 has unexpected type `QgsFields`

**Explanation:**

`prepare( const QgsFields &fields )` has been removed. Use `prepare( const QgsExpressionContext *context )` instead.

See [QGIS API Documentation: Backwards Incompatible Changes](https://qgis.org/api/api_break.html).<br>
See [StackExchange - PyQGIS gives TypeError: QgsExpression.prepare(): argument 1 has unexpected type 'QgsFields'?](https://gis.stackexchange.com/questions/244068/pyqgis-gives-typeerror-qgsexpression-prepare-argument-1-has-unexpected-type/244088#244088)

### CreateGeoLayerFromGeometry

**Error:**

`for qgis_geometry_type, wkt_geometry_types in QGIS_WKT_geom_conversion_dic.iteritems():`<br>
`AttributeError: 'dict' object has no attribute 'iteritems'`

**Explanation:**

`dict.iteritems()` is now `dict.items()`

See [StackOverflow - iteritems in Python](https://stackoverflow.com/questions/13998492/iteritems-in-python)


### For

**Error:**

`if include_properties[i] == prop_name_list[j]:`<br>`TypeError: 'dict_keys' object does not support indexing`

**Explanation:**

Must make `.keys()` list an actual list by incorporating `list(dic.keys())`.

See [Stack Overflow - TypeEror: 'dict_keys' object does not support indexing](https://stackoverflow.com/questions/17322668/typeerror-dict-keys-object-does-not-support-indexing).

### ListFiles

**Error:**

No Python error. Files are listed in different order than the expected results but all files exist. 

**Explanation and Fix:**

Return a sorted (alphabetical) list of files. Then the order will always be the same and the tests should produce the correct outputs. Recreated all the expected results to adapt the alphabetically sorted lists. 

### ReadGeoLayerFromShapefile

**Error:**

No Python error. Layers (with one feature) read in from shapefile format and then exported as GeoJSON are represented as `MultiLineString`/`MultiPolygon` when they should be read in as `LineString`/`Polygon`. This error does not happen when a single feature GeoJSON is read into QGIS and did not happen in the QGIS2 environment. I think this might be a bug (see [Stack Exchange - QGIS 3 interprets polylines as multipolylines?](https://gis.stackexchange.com/questions/274403/qgis-3-interprets-polylines-as-multipolylines)). 

**Explanation:**

This error is a bug within QGIS3 and there is no say on when it will be resolved. The bug does not break the functionality of the commands but does cause many of the tests to fail given the different terminology. To move forward, the expected results for the following tests were recreated. Once this bug is fixed, the tests will fail again, and the expected results will once again need to be recreated. 

- `test-MergeGeoLayers-Lines-AttributeMap.gp`
- `test-MergeGeoLayers-Lines-NoAttributeMap.gp`
- `test-ReadGeoLayerFromShapefile-Line.gp`
- `test-ReadGeoLayerFromShapefile-Polygon.gp`
- `test-ClipGeoLayer-linesAsInput-Memory.gp`
- `test-ClipGeoLayer-linesAsInput.gp`
- `test-ClipGeoLayer-polygonsAsInput.gp` 
- `test-ReadGeoLayersFromFolder.gp`
- `test-IntersectGeoLayer-lines-linesAsIntersect.gp`
- `test-IntersectGeoLayer-lines-polygonAsIntersect-ExcludeIntersectAttributes.gp`
- `test-IntersectGeoLayer-lines-polygonAsIntersect-IncludeIntersectAttributes.gp`
- `test-IntersectGeoLayer-lines-polygonAsIntersect-outputGeoLayerID.gp`
- `test-IntersectGeoLayer-lines-polygonAsIntersect.gp`
- `test-IntersectGeoLayer-points-linesAsIntersect.gp`
- `test-IntersectGeoLayer-points-pointsAsIntersect.gp`
- `test-IntersectGeoLayer-polygons-polygonAsIntersect.gp`

### ReadGeoLayerFromFGDB

**Error:**

`i, n = 0, len(pat)`<br>`TypeError: object of type 'NoneType' has no len()`

**Explanation:**

Not an error caused from python version migration. Bug in GeoProcessor code. Passes None to the `string_util.glob2re()` function which then tries to get the length of None (not possible). I would think that this test, `test-ReadGeoLayersFromFGDB.gp`, would fail in the *QGIS2* version as well. 

To fix, added a check to makes sure the pattern value is not None. Assigns the default pattern value if the list of patterns is *ALL* None values. 

### ReadTableFromDelimitedFile

**Error:**

Not an error caused from python version migration. Bug in GeoProcessor code. The result files do not match the expected results. 

**Explanation:**

`WriteIndexColumn` was added as a parameter to the `WriteTableFromDelimitedFile` after the tests for the `ReadTableFromDelimitedFile` were created. By default, the `WriteIndexColumn` is set to True. Before, the index column was not included at all. The expected results of the `ReadTableFromDelimitedFile` do not include the index column while the results do include an index column. 

To fix, rewrite `ReadTableFromDelimitedFile` tests to exclude the index columns.  
