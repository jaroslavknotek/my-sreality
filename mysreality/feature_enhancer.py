import pandas as pd
import geopy.distance
import numpy as np
import datetime
import json

def add_distance(df,stations=None,coords_base = None,minutes_per_km = 2):

    if stations is None:
        with open('assets/stations.json') as f:
            stations = json.load(f)
            
    data_distances = []
    for _,row in df.iterrows():
        coords = row.gps_lat,row.gps_lon
        distance_data = _get_distances_record(
            coords,
            stations,
            coords_base=coords_base,
            minutes_per_km = minutes_per_km
        )
        data_distances.append(distance_data)
    df_d = pd.DataFrame(data_distances)
    return pd.concat([df,df_d],axis=1)

    

def _get_distances_record(coords_from,stations,coords_base = None,minutes_per_km = 2):

    data = {}

    if coords_base is None:
        coords_base = stations['Praha']['gps']
        
    if coords_base is not None:
        distance_to_base = geopy.distance.geodesic(coords_from, coords_base)
        data['distance_to_base_km'] = distance_to_base

    closest_station,distance_km,trip_to_base = find_closest_way(coords_from,stations)

    data['closest_station_name'] = closest_station
    data['closest_station_km'] = distance_km
    
    data['trip_base_min'] = trip_to_base.seconds/60

    data['commute_min'] = data['closest_station_km'] *minutes_per_km + data['trip_base_min']

    return data
    

def calculate_distances(coords_from,locations):

    loc_to_km_min = {}
    for k,v in locations.items():
        coords_to = v['gps']
        distance = geopy.distance.geodesic(coords_from, coords_to)
        loc_to_km_min[k]=distance.km

    
    return loc_to_km_min

def find_closest(distances):
    k = list(distances.keys())
    kms_to_station = [v for v in  distances.values()]
    idx = np.argmin(kms_to_station)
    return k[idx],kms_to_station[idx]
    

def find_closest_way(coords_from,stations):
    distances = calculate_distances(coords_from,stations)

    closest_place,kms = find_closest(distances)
    time_to_base = datetime.timedelta(
        minutes=stations[closest_place]['trip_base_min']
    )
    return closest_place,kms,time_to_base

def score_estates(df,score_map = None):
    if score_map is None:
        with open('assets/estate_score_map.json') as f:
            score_map = json.load(f)
        
    df['state_score'] = df['Stav objektu'].map(score_map)
    return df
