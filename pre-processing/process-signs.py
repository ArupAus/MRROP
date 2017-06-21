import pandas as pd 
import json 
from geojson import Feature, Point, FeatureCollection
import numpy as np

def get_sheet_names(fn='signs-databases/xlsx/signs-database.xlsx'):
    db = pd.ExcelFile(fn)
    sheet_names = db.sheet_names
    del sheet_names[sheet_names.index('ESRI_MAPINFO_SHEET')]
    return sheet_names

def read_data(fn, sheet):
    return pd.read_excel(fn, sheet)

def get_data(sheet_names, fn='signs-databases/xlsx/signs-database.xlsx'):
    for sheet in sheet_names:
        data = read_data(fn, sheet)
        data = filter(data)
        data = make_json_obj(data)
        write_json(data, sheet)
        geojson_data = make_geojson_obj(data)
        write_geojson(geojson_data, sheet)

def write_geojson(data, sheet, fn='signs-databases/geojson/', app_fn='interactive-map/public/geojson/'):
    with open(fn+'-'.join(sheet.lower().split())+'.geojson', 'wb') as f:
        json.dump(data, f, indent=2)
    with open(app_fn+'-'.join(sheet.lower().split())+'.geojson', 'wb') as f:
        json.dump(data, f, indent=2)

def filter(db, cols=['LATITUDE', 'LONGITUDE', 'DATE_INSTALLED', 'LAT_LONG_SLK_DISTANCE', 'DESIGN_TYPE', 'IIT_COMMENT']):
    return db[cols]    

def make_json_obj(data, road_indicators=['RD', 'HWY', 'BROOK', 'ST', 'HWY', 'TCE', 'GALLERY', 'WAY', 'WESTERN']):
    colnames = list(set(data))
    # for each row 
    road_types = []
    intersections = []
    for i in data.index:
        # if iit comment is specifying an intersection, then make a dictionary, conver
        # the dictionary to a geojson object and add to array
        x = str(data['IIT_COMMENT'][i]).split()
        if len(x) > 1:
            if x[1] in road_indicators:
                intersection = {}
                for col in colnames:
                    intersection[col] = str(data[col][i]).encode('ascii', 'ignore')
                intersections.append(intersection)
    return intersections

def make_geojson_obj(data):
    featureColl = []
    for d in data:
        point = Point((float(d['LONGITUDE']), float(d['LATITUDE'])))
        del d['LONGITUDE']
        del d['LATITUDE']
        featureColl.append(Feature(geometry=point, properties=d))
    return FeatureCollection(featureColl)

def write_json(data, sheet, fn='signs-databases/json/'):
    with open(fn+'-'.join(sheet.lower().split())+'.json', 'wb') as f:
        json.dump(data, f, indent=2)

def main():
    # get the sheet names
    sheet_names = get_sheet_names()
    '''  `get_data()`
        for each sheet;
        - read in the data  "read_data(filename, sheetname)"
        - filter by relevant columns "filter(pandas_dataframe)"
        - convert to geojson "make_feature_collection()"
        - write to file "write_file(filename)"
    '''
    get_data(sheet_names)
    # convert json object to geojson file

if __name__ == '__main__':
    main()