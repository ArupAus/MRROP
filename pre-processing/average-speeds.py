
# for all directories, find the csv files which are in these directories
# make a master csv file which has the latidue and longitudes, and the speed ONLY
# then, for all unique latitude and longitudes, iterate through and get the average speed for each point
# then, split the data into quintiles
# associate each point with a quintile and a colour
# give each point an id, and create a dictionary with the id as key and the value having the latitude and longitude 
#, the average speed, and the quintile (and corresponding colour) 
# create geojson file with that data
# write both the json and geojsons to file

import pandas as pd 
import os
import json
import sys
import math
from geojson import Feature, Point, FeatureCollection

def get_directories():
    return [x+"/" for x in os.listdir(".") if os.path.isdir(x) and ('Hwy' in x or 'Road' in x)] 

def get_csvs(dirs):
    csvs = []
    for d in dirs:
        csvs += [d + x for x in os.listdir(d) if '.csv' in x]
    return csvs

def combine_csvs(csvs, colnames=['lat', 'lon', 'speed']):
    init_dict = {}
    for col in colnames:
        init_dict[col] = []
    all_dbs = pd.DataFrame(init_dict)
    for csv in csvs:
        db = pd.read_csv(csv)[colnames]
        if 'lat' in set(db) and 'lon' in set(db):
            all_dbs = pd.concat([all_dbs, db])
    all_dbs['lat'] = [round(x, 4) for x in all_dbs['lat']]
    all_dbs['lon'] = [round(x, 4) for x in all_dbs['lon']]
    return all_dbs

def write_csv(csv, fn='Speeds/master.csv'):
    csv.to_csv(fn, index=False)

def get_point_speeds():
    data = pd.read_csv('Speeds/master.csv')
    colnames = list(set(data))
    points = {}
    idx = 0
    for row in data.index:
        sys.stdout.write("%.2f%% Completed...   \r" % (float(row) * 100 / len(data)))
        sys.stdout.flush()
        lat = data['lat'][row]
        lon = data['lon'][row]
        speed = data['speed'][row]
        point_id = check_if_duplicate(points, lat, lon)
        if point_id is None:
            points[idx] = {}
            points[idx]['lat'] = lat
            points[idx]['lon'] = lon 
            points[idx]['speeds'] = []
            _id = idx  
            idx += 1
        else:
            _id = point_id 
        points[_id]['speeds'].append(speed)
    sys.stdout.write("Completed...                                \n")
    return points

def check_if_duplicate(data, lat, lon):
    point_id = None
    for _id, value in data.iteritems():
        if lat == value['lat'] and lon == value['lon']:
            point_id = _id  
    return point_id 

def write_speeds(data, fn='Speeds/master.json'):
    with open(fn, 'wb') as f:
        json.dump(data, f, indent=2)

def get_average_speeds(data):
    averages = []
    for j, (_id, value) in enumerate(data.iteritems()):
        average = float(sum(value['speeds'])) / len(value['speeds'])
        averages.append(average)
        data[j]['average_speed'] = average 
    return data, averages

def sort_averages(averages):
    averages = [x for x in averages if not math.isnan(x)]
    averages.sort()
    return averages

def get_quartiles(data, averages):
    for j, (_id, value) in enumerate(data.iteritems()):
        average = value['average_speed']
        index = averages.index(average)
        perc = float(index) * 100 / len(averages)
        data[_id]['quartile'] = 3
        data[_id]['colour'] = "#7c0000"
        if perc <= 25.0:
            data[_id]['quartile'] = 0
            data[_id]['colour'] = '#fcbe14'
            continue
        if perc <= 50.0:
            data[_id]['quartile'] = 1
            data[_id]['colour'] = '#bc7110'
            continue
        if perc <= 75.0:
            data[_id]['quartile'] = 2
            data[_id]['colour'] = '#bc4110'
            continue 
    quartiles = [0.0]
    quartiles.append(averages[int(math.floor(len(averages) * 0.25))])
    quartiles.append(averages[int(math.floor(len(averages) * 0.5))])
    quartiles.append(averages[len(averages)-1])
    return data, quartiles
        
def write_quartiles(quartiles):
    f = open('Speeds/quartiles.txt', 'w')
    f.writelines(map(str, quartiles))
    f.close()

def remove_nans(data):
    no_nans = {}
    for _id, v in data.iteritems():
        if not math.isnan(v['average_speed']):
            no_nans[_id] = v
    return no_nans      

def rename_csvs(csvs):
    for csv in csvs:
        newname = '-'.join(csv.split(' '))      
        os.rename(csv, newname)  

def make_geojson():
    with open('Speeds/master.json', 'rb') as f:
        data = json.load(f) 
    features = []
    for k, v in data.iteritems():
        point = Point((v['lat'], v['lon']))
        features.append(Feature(geometry=point, properties=v))
    featureColl = FeatureCollection(features)
    return featureColl

def write_geojson(geojson):
    with open('Speeds/master.geojson', 'wb') as f:
        json.dump(geojson, f, indent=2)

def main():
    # get all directories in the root directory
    directories = get_directories()
    csvs = get_csvs(directories)
    rename_csvs(csvs)
    csvs = get_csvs(directories)
    csv = combine_csvs(csvs)
    write_csv(csv)
    data = get_point_speeds()
    data, averages = get_average_speeds(data)
    data = remove_nans(data)
    averages = sort_averages(averages)
    data, quartiles = get_quartiles(data, averages)
    write_speeds(data)
    write_quartiles(quartiles)
    geojson = make_geojson()
    write_geojson(geojson)

if __name__ == '__main__' :
    main()
