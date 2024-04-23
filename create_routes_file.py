from activity_reader_tcx.activity_reader import *
import json

richmond_rollercoaster = ActivityReader("Richmond_rollercoaster.tcx")
richmond_rollercoaster.remove_period_after(17100)

downtown_titans = ActivityReader("Downtown_titans.tcx")
downtown_titans.remove_period_after(24600)

mech_isle_loop = ActivityReader("Mech_isle_loop_time_trial.tcx")
mech_isle_loop.remove_period_after(4170)

hilly_route = ActivityReader("Hilly_route.tcx")
hilly_route.remove_period_after(9600)

greater_london_flat = ActivityReader("Greater_london_flat_race.tcx")
greater_london_flat.remove_period_after(17500)

canopies_and_coastlines = ActivityReader("Canopies_and_coastlines_time_trial.tcx")
canopies_and_coastlines.remove_period_after(27800)

cobbled_climbs = ActivityReader("Cobbled_climbs.tcx")
cobbled_climbs.remove_period_after(18400)

two_bridges_loop = ActivityReader("Two_bridges_loop.tcx")
two_bridges_loop.remove_period_after(7100)

park_perimeter_loop = ActivityReader("Park_perimeter_loop.tcx")
park_perimeter_loop.remove_period_after(9800)

routes_dict = {
    'Richmond Rollercoaster': {
        'distance': richmond_rollercoaster.distance,
        'elevation': richmond_rollercoaster.elevation,
        'lead_in': 0
    },
    'Downtown Titans': {
        'distance': downtown_titans.distance,
        'elevation': downtown_titans.elevation,
        'lead_in': 800
    },
    'Mech Isle Loop': {
        'distance': mech_isle_loop.distance,
        'elevation': mech_isle_loop.elevation,
        'lead_in': 0    
    },
    'Hilly Route': {
        'distance': hilly_route.distance,
        'elevation': hilly_route.elevation,
        'lead_in': 500    
    },
    'Greater London Flat': {
        'distance': greater_london_flat.distance,
        'elevation': greater_london_flat.elevation,
        'lead_in': 0    
    },
    'Canopies and Coastlines': {
        'distance': canopies_and_coastlines.distance,
        'elevation': canopies_and_coastlines.elevation,
        'lead_in': 0    
    },
    'Cobbled Climbs': {
        'distance': cobbled_climbs.distance,
        'elevation': cobbled_climbs.elevation,
        'lead_in': 300    
    },
    'Two Bridges Loop': {
        'distance': two_bridges_loop.distance,
        'elevation': two_bridges_loop.elevation,
        'lead_in': 0    
    },
    'Park Perimeter Loop': {
        'distance': park_perimeter_loop.distance,
        'elevation': park_perimeter_loop.elevation,
        'lead_in': 400    
    }                     
}
import json
with open('routes.json', 'w') as file:
    json.dump(routes_dict, file)