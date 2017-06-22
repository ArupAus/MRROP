import json

with open('..\\GIS\\20170620-Albany-AM-averages-20.geojson') as f:
    jsonfile = json.load(f)


for index,feature in enumerate(jsonfile['features']):
    try:
        percentage = feature['properties']['from_perth_sum'] / feature['properties']['from_perth_total'] / feature['properties']['posted_speed']
        if percentage > 0.7:
            jsonfile['features'][index]['properties']['from_perth_quintile'] = 0
        if percentage <= 0.7 and percentage > 0.5:
            jsonfile['features'][index]['properties']['from_perth_quintile'] = 1
        if percentage <=0.5 and percentage > 0.3:
            jsonfile['features'][index]['properties']['from_perth_quintile'] = 2
        if percentage >= 0 and percentage < 0.3:
            jsonfile['features'][index]['properties']['from_perth_quintile'] = 3
        
        return_percentage = feature['properties']['to_perth_sum'] / feature['properties']['to_perth_total'] / feature['properties']['posted_speed']
        if return_percentage > 0.7:
            jsonfile['features'][index]['properties']['to_perth_quintile'] = 0
        if return_percentage <= 0.7 and return_percentage > 0.5:
            jsonfile['features'][index]['properties']['to_perth_quintile'] = 1
        if return_percentage <=0.5 and return_percentage > 0.3:
            jsonfile['features'][index]['properties']['to_perth_quintile'] = 2
        if return_percentage >= 0 and return_percentage < 0.3:
            jsonfile['features'][index]['properties']['to_perth_quintile'] = 3    
    except:
        print('no key')

with open('20170620-Albany-AM-averages-quartile.geojson', 'w') as outfile:
    
    
    json.dump(jsonfile, outfile)