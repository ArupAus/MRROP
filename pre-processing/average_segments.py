
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
from shapely.geometry.polygon import Polygon

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

def averageSegments2():
    ranges = pd.read_json('.\GIS\SLK_json.json', orient='index')
    there = pd.read_csv(".\\20170607_AM_PEAK_Albany_Hwy\\20170607.csv")
    returning = pd.read_csv(".\\20170607_AM_PEAK_Albany_Hwy\\20170607-return.csv")
    ranges['there_sum'] = 0
    ranges['there_total'] = 0 
    ranges['return_sum'] = 0
    ranges['return_total'] = 0

    
    for index,row in ranges.iterrows():        
        
        for index2, point in there.iterrows():
            if row['end_lat'] >= row['start_lat'] and row['end_long'] <= row['start_long']:
                if float(point['lat']) >= float(row['start_lat']) and float(point['lon']) <= float(row['start_long']) and float(point['lat']) <= float(row['end_lat']) and float(point['lon']) >= float(row['end_long']):
                    ranges = therepointSum(point,ranges,index)
            if row['end_lat'] <= row['start_lat'] and row['end_long'] >= row['start_long']:
                if float(point['lat']) <= float(row['start_lat']) and float(point['lon']) >= float(row['start_long']) and float(point['lat']) >= float(row['end_lat']) and float(point['lon']) <= float(row['end_long']):
                    ranges = therepointSum(point,ranges,index) 
            if row['end_lat'] <= row['start_lat'] and row['end_long'] <= row['start_long']:
                if float(point['lat']) <= float(row['start_lat']) and float(point['lon']) <= float(row['start_long']) and float(point['lat']) >= float(row['end_lat']) and float(point['lon']) >= float(row['end_long']):
                    ranges = therepointSum(point,ranges,index)
            if row['end_lat'] >= row['start_lat'] and row['end_long'] >= row['start_long']:
                if float(point['lat']) >= float(row['start_lat']) and float(point['lon']) >= float(row['start_long']) and float(point['lat']) <= float(row['end_lat']) and float(point['lon']) <= float(row['end_long']):
                    ranges = therepointSum(point,ranges,index)
        
        for index3, point in returning.iterrows():
            
            if row['end_lat'] >= row['start_lat'] and row['end_long'] <= row['start_long']:
                if float(point['lat']) >= float(row['start_lat']) and float(point['lon']) <= float(row['start_long']) and float(point['lat']) <= float(row['end_lat']) and float(point['lon']) >= float(row['end_long']):
                    ranges = returnpointSum(point,ranges,index)
            if row['end_lat'] <= row['start_lat'] and row['end_long'] >= row['start_long']:
                if float(point['lat']) <= float(row['start_lat']) and float(point['lon']) >= float(row['start_long']) and float(point['lat']) >= float(row['end_lat']) and float(point['lon']) <= float(row['end_long']):
                    ranges = returnpointSum(point,ranges,index) 
            if row['end_lat'] <= row['start_lat'] and row['end_long'] <= row['start_long']:
                if float(point['lat']) <= float(row['start_lat']) and float(point['lon']) <= float(row['start_long']) and float(point['lat']) >= float(row['end_lat']) and float(point['lon']) >= float(row['end_long']):
                    ranges = returnpointSum(point,ranges,index)
            if row['end_lat'] >= row['start_lat'] and row['end_long'] >= row['start_long']:
                if float(point['lat']) >= float(row['start_lat']) and float(point['lon']) >= float(row['start_long']) and float(point['lat']) <= float(row['end_lat']) and float(point['lon']) <= float(row['end_long']):
                    ranges = returnpointSum(point,ranges,index)
            
                
    for index,row in ranges.iterrows():
        if row['there_sum']> 0 and row['there_total'] > 0 :
            ranges.set_value(index,'there_average', ranges['there_sum'][index] / ranges['there_total'][index])
        if row['return_sum']> 0 and row['return_total'] > 0 :
            ranges.set_value(index,'return_average', ranges['return_sum'][index] / ranges['return_total'][index])

    
    ranges.to_csv('.\\20170607_AM_PEAK_Albany_Hwy\\averages.csv')


def averageSegments():
    ranges = pd.read_json('.\GIS\SLK_json.json', orient='index')
    slks = pd.read_json('.\GIS\SLK_Albany.geojson')
    there = pd.read_csv(".\\20170607_AM_PEAK_Albany_Hwy\\20170607.csv")
    returning = pd.read_csv(".\\20170607_AM_PEAK_Albany_Hwy\\20170607-return.csv")
    ranges['there_sum'] = 0
    ranges['there_total'] = 0 
    ranges['return_sum'] = 0
    ranges['return_total'] = 0

    
    for polygon in slks.features:
        
        for index2, point in there.iterrows():
            shape_p = shape(polygon['geometry'])
            point_p = Point(point.lon, point.lat)
            
            if shape_p.contains(point_p):
                index = ranges[ranges['index']==polygon['properties']['M_Link_ID']].index.tolist()[0]
                
                therepointSum(polygon, point, ranges, index)

        for index3, point in returning.iterrows():
            shape_p = shape(polygon['geometry'])
            point_p = Point(point.lon, point.lat)
            
            if shape_p.contains(point_p):
                index = ranges[ranges['index']==polygon['properties']['M_Link_ID']].index.tolist()[0]
                
                returnpointSum(polygon, point, ranges, index)
    
                
    for index,row in ranges.iterrows():
        if row['there_sum']> 0 and row['there_total'] > 0 :
            ranges.set_value(index,'there_average', ranges['there_sum'][index] / ranges['there_total'][index])
            ranges.set_value(index,'there_per',  ranges['there_average'][index]/  ranges['posted_speed'][index])
        if row['return_sum']> 0 and row['return_total'] > 0 :
            ranges.set_value(index,'return_average', ranges['return_sum'][index] / ranges['return_total'][index])
            ranges.set_value(index,'return_per',  ranges['return_average'][index]/  ranges['posted_speed'][index])
        if row['there_total'] == 0.0 and row['return_total'] == 0.0:
            ranges.drop(index, inplace=True)
    
    ranges.to_csv('.\\20170607_AM_PEAK_Albany_Hwy\\averages.csv')

def therepointSum(polygon, point, ranges, index):
    if not math.isnan(float(point['speed'])):
        cursum = ranges['there_sum'][index] + float(point['speed'])*3.6      
                                
        ranges.set_value(index,'there_sum',cursum)    
        
        ranges.set_value(index,'there_total',ranges['there_total'][index] + 1)

        ranges.set_value(index, 'posted_speed', polygon['properties']['Avg_Posted'])
    return ranges

def returnpointSum(polygon, point, ranges, index):
    if not math.isnan(float(point['speed'])):
        cursum = ranges['return_sum'][index] + float(point['speed'])*3.6      
                        
        ranges.set_value(index,'return_sum',cursum)    
        
        ranges.set_value(index,'return_total',ranges['return_total'][index] + 1)
        ranges.set_value(index, 'posted_speed', polygon['properties']['Avg_Posted'])
    return ranges

def main():
    averageSegments()
    

if __name__ == '__main__' :
    main()
