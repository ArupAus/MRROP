import json

with open('public/master.geojson', 'rb') as f:
    data = json.load(f)

features = data['features']

for j, feature in enumerate(features):
    features[j]['geometry']['coordinates'] = features[j]['geometry']['coordinates'][1], features[j]['geometry']['coordinates'][0] 

data['features'] = features

with open('public/master.geojson', 'w') as f:
    json.dump(data, f, indent=2)