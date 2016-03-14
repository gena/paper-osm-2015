rem @echo off


set hydro_basins_name=hybas_au_lev03_v1c
set base=..\..\data\OpenStreetMaps\australia-oceania-latest
set basin=5030073410
set poly=..\..\data\hybas_au_lev03_v1c_5030073410.poly

set pbf=%base%.osm.pbf

set base_name=%base%-%basin%
set current_basin="-B=%poly%"
rem set base_name=%base%
rem set current_basin=

set o5m=%base_name%.o5m
set osm_water=%base_name%-water.osm
set pbf_water=%base_name%-water.osm.pbf
set db_water=%base_name%-water.db
 
cd ..\..\output

rem convert basin SHP to POLY
rem python ..\..\src\ogr2poly.py ..\..\data\HydroBASINS\without_lakes\%hydro_basins_name%.shp -f HYBAS_ID -b 0.05 -s 0.01


rem filter by basin
..\..\bin\osmconvert %pbf% --complex-ways %current_basin% -o=%o5m%

rem or: include all region
rem ..\..\bin\osmconvert %pbf% --complex-ways -o=%o5m%


rem filter water
..\..\bin\osmfilter %o5m% --parameter-file=..\..\config\water.osmfilter.params > "%osm_water%" 
 
rem convert back to PBF
..\..\bin\osmconvert "%osm_water%" -o="%pbf_water%"

rem convert to SpatiaLite
copy /Y ..\..\config\osmconf.ini .\osmconf.ini
del /Q "%db_water%"

ogr2ogr -f SQLite -dsco OGR_SQLITE_SYNCHRONOUS=OFF -dsco SPATIALITE=YES "%db_water%" "%pbf_water%"

rem convert to KML
ogr2ogr -sql "select * from lines" -f "KML" "%base_name%-water-lines.kml" "%db_water%"
ogr2ogr -sql "select * from multipolygons" -f "KML" "%base_name%-water-multipolygons.kml" "%db_water%"

rem convert to SHP
ogr2ogr -sql "select * from lines" -f "ESRI Shapefile" "%base_name%-water-lines.shp" "%db_water%"
ogr2ogr -sql "select * from multipolygons" -f "ESRI Shapefile" "%base_name%-water-multipolygons.shp" "%db_water%"

