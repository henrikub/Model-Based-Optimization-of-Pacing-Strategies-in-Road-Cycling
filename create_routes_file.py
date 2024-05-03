from activity_reader_tcx.activity_reader import *
import json
import numpy as np

surface_friction = {
    'pavement': 0.004,
    'sand': 0.004,
    'brick': 0.0055,
    'wood': 0.0065,
    'cobbles': 0.0055,
    'ice': 0.0075,
    'snow': 0.0075,
    'gravel': 0.012,
    'dirt': 0.016
}

downtown_titans = ActivityReader("Downtown_titans.tcx")
downtown_titans.remove_period_after(24600 + 100)

downtown_titans_friction = []
for d in downtown_titans.distance:
    if d <= 21400:
        downtown_titans_friction.append(surface_friction['pavement'])
    elif 21400 < d <= 21570:
        downtown_titans_friction.append(surface_friction['cobbles'])
    elif 21570 < d <= 22100:
        downtown_titans_friction.append(surface_friction['pavement'])
    elif 22100 < d <= 22230:
        downtown_titans_friction.append(surface_friction['wood'])
    else:
        downtown_titans_friction.append(surface_friction['pavement'])

mech_isle_loop = ActivityReader("Mech_isle_loop_time_trial.tcx")
mech_isle_loop.remove_period_after(4000 + 100)

mech_isle_loop_friction = []
for d in mech_isle_loop.distance:
    if d <= 300:
        mech_isle_loop_friction.append(surface_friction['pavement'])
    elif 300 < d <= 500:
        mech_isle_loop_friction.append(surface_friction['wood'])
    elif 500 < d <= 950:
        mech_isle_loop_friction.append(surface_friction['dirt'])
    elif 950 < d <= 1150:
        mech_isle_loop_friction.append(surface_friction['sand'])
    elif 1150 < d <= 1450:
        mech_isle_loop_friction.append(surface_friction['dirt'])
    elif 1450 < d <= 1525:
        mech_isle_loop_friction.append(surface_friction['wood'])
    elif 1525 < d <= 1970:
        mech_isle_loop_friction.append(surface_friction['dirt'])
    elif 1970 < d <= 2030:
        mech_isle_loop_friction.append(surface_friction['wood'])
    elif 2030 < d <= 2520:
        mech_isle_loop_friction.append(surface_friction['dirt'])
    else:
        mech_isle_loop_friction.append(surface_friction['pavement'])

hilly_route = ActivityReader("Hilly_route.tcx")
hilly_route.remove_period_after(9100 + 400)

hilly_route_friction = []
for d in hilly_route.distance:
    if d <= 6150:
        hilly_route_friction.append(surface_friction['pavement'])
    elif 6150 < d <= 6300:
        hilly_route_friction.append(surface_friction['cobbles'])
    elif 6300 < d <= 6850:
        hilly_route_friction.append(surface_friction['pavement'])
    elif 6850 < d <= 6990:
        hilly_route_friction.append(surface_friction['wood'])
    else:
        hilly_route_friction.append(surface_friction['pavement'])

cobbled_climbs = ActivityReader("Cobbled_climbs.tcx")
cobbled_climbs.remove_period_after(9200 + 400)

cobbled_climbs_friction = []
for d in cobbled_climbs.distance:
    if d <= 5600:
        cobbled_climbs_friction.append(surface_friction['pavement'])
    elif 5600 < d <= 5900:
        cobbled_climbs_friction.append(surface_friction['cobbles'])
    elif 5900 < d <= 6850:
        cobbled_climbs_friction.append(surface_friction['pavement'])
    elif 6850 < d <= 7000:
        cobbled_climbs_friction.append(surface_friction['cobbles'])
    else:
        cobbled_climbs_friction.append(surface_friction['pavement'])

two_bridges_loop = ActivityReader("Two_bridges_loop.tcx")
two_bridges_loop.remove_period_after(7100)

two_bridges_loop_friction = []
for d in two_bridges_loop.distance:
    if d <= 2600:
        two_bridges_loop_friction.append(surface_friction['pavement'])
    elif 2600 < d <= 2750:
        two_bridges_loop_friction.append(surface_friction['wood'])
    elif 2750 < d <=  3250:
        two_bridges_loop_friction.append(surface_friction['pavement'])
    elif 3250 < d <= 3525:
        two_bridges_loop_friction.append(surface_friction['cobbles'])
    else:
        two_bridges_loop_friction.append(surface_friction['pavement'])

park_perimeter_loop = ActivityReader("Park_perimeter_loop.tcx")
park_perimeter_loop.remove_period_after(9800 + 100)
park_perimeter_loop_friction = len(park_perimeter_loop.distance)*[surface_friction['pavement']]

routes_dict = {
    'Downtown Titans': {
        'distance': downtown_titans.distance,
        'elevation': downtown_titans.elevation,
        'friction': downtown_titans_friction,
        'lead_in': 100
    },
    'Mech Isle Loop': {
        'distance': mech_isle_loop.distance,
        'elevation': mech_isle_loop.elevation,
        'friction': mech_isle_loop_friction,
        'lead_in': 100    
    },
    'Hilly Route': {
        'distance': hilly_route.distance,
        'elevation': hilly_route.elevation,
        'friction': hilly_route_friction,
        'lead_in': 400    
    }, 
    'Cobbled Climbs': {
        'distance': cobbled_climbs.distance,
        'elevation': cobbled_climbs.elevation,
        'friction': cobbled_climbs_friction,
        'lead_in': 400    
    },
    'Two Bridges Loop': {
        'distance': two_bridges_loop.distance,
        'elevation': two_bridges_loop.elevation,
        'friction': two_bridges_loop_friction,
        'lead_in': 0    
    },
    'Park Perimeter Loop': {
        'distance': park_perimeter_loop.distance,
        'elevation': park_perimeter_loop.elevation,
        'friction': park_perimeter_loop_friction,
        'lead_in': 100    
    }                     
}
for key in routes_dict:
    
    if routes_dict[key]['lead_in'] != 0:
        index_start = np.argwhere(np.array(routes_dict[key]['distance']) > routes_dict[key]['lead_in'])[0][0]
        routes_dict[key]['distance'] = list(np.array(routes_dict[key]['distance'][index_start:-1]) - routes_dict[key]['lead_in'])
        routes_dict[key]['elevation'] = routes_dict[key]['elevation'][index_start:-1]
        routes_dict[key]['friction'] = routes_dict[key]['friction'][index_start:-1]
    for i in range(len(routes_dict[key]['distance'])-1):
        if routes_dict[key]['distance'][i] >= routes_dict[key]['distance'][i+1]:
            print("found two point at the same distance in ", key, " at distance: ", routes_dict[key]['distance'][i])
            routes_dict[key]['distance'][i+1] = routes_dict[key]['distance'][i] + 0.1

routes_dict['Two Bridges Loop']['lead_in'] = 180

import json
with open('routes.json', 'w') as file:
    json.dump(routes_dict, file)