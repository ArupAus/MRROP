
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
from shapely.geometry import Point, shape
from geojson import Feature, FeatureCollection, Polygon,dump,loads

def getSegments():
    ranges = {}
    starts = pd.read_csv('.\GIS\SLK_Start.csv')
    ends = pd.read_csv('.\GIS\SLK_End.csv')
    for index,start in starts.iterrows():
        end = ends.loc[ends['M_Link_ID'] == start['M_Link_ID']]
        end_lat = end['Lat'].values[0]
        end_long = end['Long'].values[0]
        ranges[index] =  {'index': start["M_Link_ID"], 'start_lat': start['Lat'], 'start_long': start['Long'], 'end_lat': end_lat, 'end_long': end_long}

    df = pd.DataFrame(ranges)
    df.to_json('.\GIS\SLK_json.json')

def averageSegments(out_perth, into_perth, road_name, output):
    ranges = pd.read_json('.\GIS\SLK_json.json', orient='index')
    slks = pd.read_json('.\GIS\SLK_'+road_name+'.geojson')
    features = []
    there = pd.read_csv(out_perth)
    returning = pd.read_csv(into_perth)
    ranges['from_perth_sum'] = 0
    ranges['from_perth_total'] = 0 
    ranges['to_perth_sum'] = 0
    ranges['to_perth_total'] = 0

    
    for slk_index, polygon in enumerate(slks.features):
        
        for index2, point in there.iterrows():
            shape_p = shape(polygon['geometry'])
            point_p = Point(point.lon, point.lat)
            
            if shape_p.contains(point_p):
                index = ranges[ranges['index']==polygon['properties']['M_Link_ID']].index.tolist()[0]
                
                therepointSum(polygon, point, ranges, index,features)

        for index3, point in returning.iterrows():
            shape_p = shape(polygon['geometry'])
            point_p = Point(point.lon, point.lat)
            
            if shape_p.contains(point_p):
                index = ranges[ranges['index']==polygon['properties']['M_Link_ID']].index.tolist()[0]
                
                returnpointSum(polygon, point, ranges, index,features)
    
    for index,row in ranges.iterrows():
        if row['from_perth_sum']> 0 and row['from_perth_total'] > 0 :
            ranges.set_value(index,'from_perth_average', ranges['from_perth_sum'][index] / ranges['from_perth_total'][index])
            ranges.set_value(index,'from_perth_per',  ranges['from_perth_average'][index]/  ranges['posted_speed'][index] * 100)
        if row['to_perth_sum']> 0 and row['to_perth_total'] > 0 :
            ranges.set_value(index,'to_perth_average', ranges['to_perth_sum'][index] / ranges['to_perth_total'][index])
            ranges.set_value(index,'to_perth_per',  ranges['to_perth_average'][index]/  ranges['posted_speed'][index] * 100)
        if row['from_perth_total'] == 0.0 and row['to_perth_total'] == 0.0:
            ranges.drop(index, inplace=True)
    
    ranges.to_csv(output+'.csv')
    

    with open(output + '.geojson', 'w') as outfile:
        collection = FeatureCollection(features)
        
        dump(collection, outfile)

def therepointSum(polygon, point, ranges, index,features):
    
    if not math.isnan(float(point['speed'])):
        cursum = ranges['from_perth_sum'][index] + float(point['speed'])*3.6      
                                
        ranges.set_value(index,'from_perth_sum',cursum)    
        
        ranges.set_value(index,'from_perth_total',ranges['from_perth_total'][index] + 1)

        ranges.set_value(index, 'posted_speed', polygon['properties']['Avg_Posted'])
        
        polygon['properties']['from_perth_sum'] = cursum
        polygon['properties']['from_perth_total'] = float(ranges['from_perth_total'][index])
        polygon['properties']['posted_speed'] = polygon['properties']['Avg_Posted']
        
        p = Polygon(polygon['geometry']['coordinates'])
        feature = Feature(geometry=p, properties=polygon['properties'])
        exists = False
        for index,feature_e in enumerate(features):
            if feature.properties['M_Link_ID'] == feature_e.properties['M_Link_ID']:
                exists = True
                features[index].properties = feature.properties
        if not exists:
            features.append(feature)
        
    return ranges

def returnpointSum(polygon, point, ranges, index,features):
    if not math.isnan(float(point['speed'])):
        cursum = ranges['to_perth_sum'][index] + float(point['speed'])*3.6      
                        
        ranges.set_value(index,'to_perth_sum',cursum)    
        
        ranges.set_value(index,'to_perth_total',ranges['to_perth_total'][index] + 1)
        ranges.set_value(index, 'posted_speed', polygon['properties']['Avg_Posted'])
        ranges.set_value(index, 'From_Int', polygon['properties']['From_Int'])
        ranges.set_value(index, 'To_Int', polygon['properties']['To_Int'])
        ranges.set_value(index, 'Distance',abs(polygon['properties']['End_SLK']- polygon['properties']['Start_SLK']) )

        polygon['properties']['to_perth_sum']  = cursum
        polygon['properties']['to_perth_total'] = float(ranges['to_perth_total'][index])
        polygon['properties']['posted_speed'] = polygon['properties']['Avg_Posted']        
        polygon['properties']['Distance'] = abs(polygon['properties']['End_SLK']- polygon['properties']['Start_SLK'])
        p = Polygon(polygon['geometry']['coordinates'])
        feature = Feature(geometry=p, properties=polygon['properties'])
        exists = False
        for index,feature_e in enumerate(features):
            if feature.properties['M_Link_ID'] == feature_e.properties['M_Link_ID']:
                exists = True
                features[index].properties = feature.properties
        if not exists:
            features.append(feature)
        
    return ranges

def main():
    averageSegments('.\\20170607_AM_PEAK_Albany_Hwy\\20170607.csv','.\\20170607_AM_PEAK_Albany_Hwy\\20170607-return.csv', 'Albany','.\\20170607_AM_PEAK_Albany_Hwy\\20170607-Albany-AM-averages')
    averageSegments('.\\20170607_PM_Peak_Albany_Hwy\\20170607.csv','.\\20170607_PM_Peak_Albany_Hwy\\20170607-return.csv', 'Albany','.\\20170607_PM_Peak_Albany_Hwy\\20170607-Albany-PM-averages')
    averageSegments('.\\20170608_AM_PEAK_Orrong_Road\\20170608.csv','.\\20170608_AM_PEAK_Orrong_Road\\20170608-return.csv', 'Orrong','.\\20170608_AM_PEAK_Orrong_Road\\20170608-Orrong-AM-averages')
    averageSegments('.\\20170608_PM_PEAK_Orrong_Road\\20170608.csv','.\\20170608_PM_PEAK_Orrong_Road\\20170608-return.csv', 'Orrong','.\\20170608_PM_PEAK_Orrong_Road\\20170608-Orrong-PM-averages')
    averageSegments('.\\20170620_AM_Albany_Hwy\\20170620.csv','.\\20170620_AM_Albany_Hwy\\20170620-return.csv', 'Albany','.\\20170620_AM_Albany_Hwy\\20170620-Albany-AM-averages')
    

if __name__ == '__main__' :
    main()
