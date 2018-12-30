# gdal_util - utility functions to use with GDAL software
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2019 Open Water Foundation
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

from osgeo import gdal, ogr, osr
import geoprocessor.util.io_util as io_util
import os


def polygonize(raster_full_path, field_name, output_format, output_file, crs_code_int):
    # TODO egiles 2018-02-14 document
    # REF: https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html#polygonize-a-raster-band

    # Open the raster within the GDAL environment.
    src_ds = gdal.Open(raster_full_path)
    prj = src_ds.GetProjection()
    print(prj)

    srs = osr.SpatialReference(wkt=prj)
    if srs.IsProjected:
        print(srs.GetAttrValue('projcs'))
    print(srs.GetAttrValue('geogcs'))


    # Get the raster's bands.
    src_band = src_ds.GetRasterBand(3)

    # Get the appropriate driver and destination data source. Can either be Shapefile or GeoJSON.
    if output_format.upper() == "SHAPEFILE":
        drv = ogr.GetDriverByName("ESRI Shapefile")
        dst_ds = drv.CreateDataSource(os.path.join(io_util.get_path(output_file),io_util.get_filename(output_file) + ".shp"))
    elif output_format.upper() == "GEOJSON":
        drv = ogr.GetDriverByName("GeoJSON")
        dst_ds = drv.CreateDataSource(output_file)
    else:
        drv = None
        dst_ds = None
        print("{} is not a valid output_format. Choose either Shapefile or GeoJSON.")

    # Create the vector layer.
    input_spatial_ref = osr.SpatialReference()
    input_spatial_ref.ImportFromEPSG(crs_code_int)
    dst_layer = dst_ds.CreateLayer(output_file, input_spatial_ref)

    if field_name:

        # create a field
        idField = ogr.FieldDefn(field_name, ogr.OFTReal)
        dst_layer.CreateField(idField)

        # Run the polygonize command.
        gdal.Polygonize(src_band, None, dst_layer, 0, [], callback=None)

    else:

        # Run the polygonize command.
        gdal.Polygonize(src_band, None, dst_layer, -1, [], callback=None)

    # Get the layer projection.
    spatialRef = dst_layer.GetSpatialRef()

def reproject_a_layer(input_path, input_driver, output_path, output_crs_int):

    driver = ogr.GetDriverByName(input_driver)

    # input SpatialReference
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(2927)

    # output SpatialReference
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(4326)

    # create the CoordinateTransformation
    coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    # get the input layer
    inDataSet = driver.Open(r'c:\data\spatial\basemap.shp')
    inLayer = inDataSet.GetLayer()
    inSpatialRef = inLayer.GetSpatialRef()

    # create the output layer
    outputShapefile = r'c:\data\spatial\basemap_4326.shp'
    if os.path.exists(outputShapefile):
        driver.DeleteDataSource(outputShapefile)
    outDataSet = driver.CreateDataSource(outputShapefile)
    outLayer = outDataSet.CreateLayer("basemap_4326", geom_type=ogr.wkbMultiPolygon)

    # add fields
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)

    # get the output layer's feature definition
    outLayerDefn = outLayer.GetLayerDefn()

    # loop through the input features
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        # get the input geometry
        geom = inFeature.GetGeometryRef()
        # reproject the geometry
        geom.Transform(coordTrans)
        # create a new feature
        outFeature = ogr.Feature(outLayerDefn)
        # set the geometry and attribute
        outFeature.SetGeometry(geom)
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
        # add the feature to the shapefile
        outLayer.CreateFeature(outFeature)
        # dereference the features and get the next input feature
        outFeature = None
        inFeature = inLayer.GetNextFeature()

    # Save and close the shapefiles
    inDataSet = None
    outDataSet = None
