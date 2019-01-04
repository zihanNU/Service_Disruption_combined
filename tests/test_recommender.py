import app_recommender
import pandas as tpd

def test_get_odelist_hist():
    my_df = tpd.DataFrame(columns=['originCluster', 'destinationCluster', 'corridor', 'equipment', 'origin_count', 'origin_max', 'dest_count', 'dest_max'])

    _origin = "Nashville Region"
    _destination = "South GA Region"
    _corridor = "Atlanta Region-South East AL Region"
    _equipment = "Equip"
    _origin_count = 29
    _origin_max = 104
    _dest_count = 35
    _dest_max = 111

    my_df.loc[0] = { "originCluster": _origin, "destinationCluster" : _destination, 
                        "corridor" : _corridor, "equipment" : _equipment, 
                        "origin_count" : _origin_count, "origin_max": _origin_max, 
                        "dest_count" : _dest_count, "dest_max" : _dest_max }

    actual = app_recommender.get_odelist_hist(my_df)

    assert _origin == actual["origin"][0]
    assert _destination == actual["destination"][0]
    assert _corridor == actual["corridor"][0]
    assert _equipment == actual["equipment"][0]
    assert _origin_count == actual["origin_count"][0]
    assert _origin_max == actual["origin_max"][0]
    assert _dest_count == actual["dest_count"][0]
    assert _dest_max == actual["dest_max"][0]


def test_get_odelist_new():
    my_df = tpd.DataFrame(columns=['originCluster', 'destinationCluster', 'corridor', 'equipment'])

    _origin = "Nashville Region"
    _destination = "South GA Region"
    _corridor = "Atlanta Region-South East AL Region"
    _equipment = "Equip"

    my_df.loc[0] = { "originCluster": _origin, "destinationCluster" : _destination, 
                        "corridor" : _corridor, "equipment" : _equipment}

    actual = app_recommender.get_odelist_new(my_df)

    assert _origin == actual["origin"][0]
    assert _destination == actual["destination"][0]
    assert _corridor == actual["corridor"][0]
    assert _equipment == actual["equipment"][0]


def test_api_json_output():

    my_df = tpd.DataFrame(columns=['loadID', 'Reason', 'Score'])
    my_df.loc[0] = {"loadID" : tpd.Series(1234567), "Reason": "Because I", "Score" : tpd.Series("123")}
    my_df.loc[1] = {"loadID" : tpd.Series(9876543), "Reason": "Sayso", "Score" : tpd.Series(987.654)}
    my_df.loc[2] = {"loadID" : tpd.Series(5555555), "Reason": "dude", "Score" : tpd.Series(42.1)}
    
    actual = app_recommender.api_json_output(my_df)
    assert type(actual) is list
    assert 3 == len(actual)
    
    assert actual[0]["loadid"] == 1234567
    assert actual[0]["Reason"] == "Because I"
    assert actual[0]["Score"] == 123

    assert actual[1]["loadid"] == 9876543
    assert actual[1]["Reason"] == "Sayso"
    assert actual[1]["Score"] == 987    

    assert actual[2]["loadid"] == 5555555
    assert actual[2]["Reason"] == "dude"
    assert actual[2]["Score"] == 42        

def test_score_deadhead():
    """
        Test the function that scores deadhead
        Lower deadhead creates higher scores
    """
    my_list = [223.5, 187.1, 18.0, 66]
    result = app_recommender.score_deadhead(my_list, 250)

    assert 11 == round(result[0])
    assert 25 == round(result[1])
    assert 93 == round(result[2])
    assert 74 == round(result[3])


def test_class_carrier_ode_loads_kpi_std():

    carrierid = 5213
    lane_df = create_ode_df()
    ode = next(lane_df.itertuples())
    expected_origin = ode.origin

    loads_df = create_loads_df()
    expected_load1 = loads_df.values[0][0]
    expected_load2 = loads_df.values[1][0]

    actual_class = app_recommender.carrier_ode_loads_kpi_std(carrier=carrierid, ode=ode, loads=loads_df)

    assert actual_class.carrier == carrierid
    assert actual_class.ode.origin == expected_origin
    assert actual_class.loads.values[0][0] == expected_load1
    assert actual_class.loads.values[1][0] == expected_load2
    

def test_makeMatrix():
    """makeMatrix(x,y,z) are the same inputs to carrier_ode_loads_kpi_std class
    
    Returns: two lists, list1 has the appended carrier_ode_loads_kpi_std classes
    list2 has the 'corridor' from the passed in ode?
    """
    
    carrierid = 5213
    lane_df = create_ode_df()
    #ode = next(lane_df.itertuples())
    
    loads_df = create_loads_df()
    loads_count = len(loads_df.index)
    
    kpiMatrix, odlist = app_recommender.makeMatrix(loads_df, lane_df, carrierid)

    #with the default corridor, we expect to get all the loads back.
    assert loads_count == len(kpiMatrix[0].loads.index)

    #now if our loads have a different corridor...we get no loads back.
    loads_df = create_loads_df('sammich-hungry')
    kpiMatrix, odlist = app_recommender.makeMatrix(loads_df, lane_df, carrierid)

    #...we should get no loads returned
    assert 0 == len(kpiMatrix[0].loads.index)

def create_loads_df(corridor='Louisville KY Region-Orlando Region'):

    loads_df = tpd.DataFrame(columns=['loadid', 'loaddate', 'carrierID', 'hot', 'customer_rate',
       'carrier_cost', 'margin_perc', 'miles', 'rpm', 'kpiScore', 'originDH',
       'pu_GAP', 'originCluster', 'destinationCluster', 'corridor',
       'equipment', 'origin_count', 'dest_count', 'industryID', 'industry',
       'originLat', 'originLon', 'destinationLat', 'destinationLon',
       'createdate', 'updatedate', 'origin_max', 'dest_max'], index=list(range(2)))

    #loads_df.loc[0] = { "loadid": 1234 }
    #loads_df.loc[1] = { "loadid": 9876 }

    loads_df.at[0,"loadid"] = 1234
    loads_df.at[1,"loadid"] = 9876

    loads_df["corridor"] = corridor
    
    return loads_df


def create_ode_df(corridor='Louisville KY Region-Orlando Region'):
    lane_df = tpd.DataFrame(columns=['origin', 'destination', 'corridor', 'equipment', 'origin_count',
        'origin_max', 'dest_count', 'dest_max'])
    lane_df.loc[0] = {
        "corridor": corridor,
        "dest_count": 41,
        "dest_max": 41,
        "destination": 'Orlando Region',
        "equipment": 'other',
        "origin": 'Louisville KY Region',
        "origin_count": 10,
        "origin_max": 33
    }
    return lane_df