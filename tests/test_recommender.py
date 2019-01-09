import app_recommender
import pandas as tpd
import random


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
    
    kpiMatrix, _ = app_recommender.makeMatrix(loads_df, lane_df, carrierid)

    #with the default corridor, we expect to get all the loads back.
    assert loads_count == len(kpiMatrix[0].loads.index)

    #now if our loads have a different corridor...we get no loads back.
    loads_df = create_loads_df('sammich-hungry')
    kpiMatrix, _ = app_recommender.makeMatrix(loads_df, lane_df, carrierid)

    #...we should get no loads returned
    assert 0 == len(kpiMatrix[0].loads.index)


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


def test_find_ode_single_matching_load():

    carrierid = 5213
    newloads_df = create_newloads_df() #current loads

    matching_corridor = newloads_df.at[0,"corridor"]
    
    lane_df = create_ode_df(matching_corridor)
    loads_df = create_loads_df(matching_corridor) #historical loads
    kpiMatrix, odlist = app_recommender.makeMatrix(loads_df, lane_df, carrierid)
    

    #randomloadindex = random.randint(0,10)
    #newload = newloads_df.iloc[randomloadindex]
    #could use ... next(lane_df.itertuples())

    #the results
    matchlist = None
    #perc_weight = None
    #corridor_vol = None

    target_load = next(newloads_df.itertuples()) #Gets us the first load
    matchlist, _, _ = app_recommender.find_ode(kpiMatrix, target_load, odlist)

    assert len(loads_df.index) == len(matchlist.index) #returns the same number of loads because we feed in matching corridors




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


def create_newloads_df():

    newloads_df = tpd.DataFrame(columns=['loadID', 'loaddate', 'StateType', 'value', 'customer_rate',
       'equipment', 'equipmentlength', 'miles', 'pu_appt', 'origin',
       'destination', 'originLon', 'originLat', 'destinationLon',
       'destinationLat', 'originCluster', 'destinationCluster', 'corridor',
       'industryID', 'industry', 'originDH', 'destDH', 'puGap', 'totalDH'], index=list(range(10)))

    #originDH & destDH may be settable by truck/default.
    #originDH_default = 250
    #destDH_default = 300
    #gap_default=48
    #totalDH = originDH_default+destDH_default
    # newloads_df.loc[0] = {
    #     "loadID": 15563494, "loaddate": '2019-01-07', "StateType": 1, "value": 100000.0, "customer_rate": 1250.0, 
    #     "equipment": 'G', "equipmentlength": 48.0, "miles": 541.0, "pu_appt": tpd.Timestamp(year=2019, month=1, day=11, hour=16), "origin": 'Piscataway-NJ', 
    #     "destination":  'Hope Mills-NC', "originLon": -74.454, "originLat": 40.561, "destinationLon": -78.946, 
    #     "destinationLat": 34.971, "originCluster": 'Elizabeth Region', "destinationCluster": 'Fayetteville NC Region', "corridor": 'Elizabeth Region-Fayetteville NC Region',
    #     "industryID": 52, "industry": 'Finance and Insurance', "originDH": originDH_default, "destDH": destDH_default, "puGap": gap_default, "totalDH": totalDH
    # }
    
    newloads_df.loc[0] = {"loadID":15749742,"loaddate":"2019-01-08","StateType":1,"value":100000,"customer_rate":2589.44,"equipment":"R","equipmentlength":48,"miles":1156,"pu_appt":"2019-01-08","origin":"Groveport-OH","destination":"Houston-TX","originLon":-82.885,"originLat":39.852,"destinationLon":-95.363,"destinationLat":29.763,"originCluster":"Columbus OH Region","destinationCluster":"Houston Region","corridor":"Columbus OH Region-Houston Region","industryID":72,"industry":"Accommodation and Food Services","originDH": 250, "destDH": 300, "puGap": 300, "totalDH": 550 }
    newloads_df.loc[1] = {"loadID":15774898,"loaddate":"2019-01-07","StateType":1,"value":100000,"customer_rate":2500,"equipment":"R","equipmentlength":53,"miles":928,"pu_appt":"2019-01-07","origin":"Nogales-AZ","destination":"San Francisco-CA","originLon":-110.933,"originLat":31.347,"destinationLon":-122.42,"destinationLat":37.778,"originCluster":"Phoenix Region","destinationCluster":"Tracy Region","corridor":"Phoenix Region-Tracy Region","industryID":81,"industry":"Other Services (except Public Administration)","originDH": 250, "destDH": 300, "puGap": 300, "totalDH": 550 }
    newloads_df.loc[2] = {"loadID":15748651,"loaddate":"2019-01-08","StateType":1,"value":100000,"customer_rate":970,"equipment":"V","equipmentlength":53,"miles":569,"pu_appt":"2019-01-08","origin":"Jacksonville-FL","destination":"Muscle Shoals-AL","originLon":-81.656,"originLat":30.332,"destinationLon":-87.669,"destinationLat":34.748,"originCluster":"Orlando Region","destinationCluster":"Birmingham Region","corridor":"Orlando Region-Birmingham Region","industryID":42,"industry":"Wholesale Trade","originDH": 250, "destDH": 300, "puGap": 300, "totalDH": 550 }
    newloads_df.loc[3] = {"loadID":15695845,"loaddate":"2019-01-08","StateType":1,"value":100000,"customer_rate":1461.62,"equipment":"V","equipmentlength":53,"miles":484,"pu_appt":"2019-01-08","origin":"Decatur-IN","destination":"Shawano-WI","originLon":-84.934,"originLat":40.843,"destinationLon":-88.606,"destinationLat":44.776,"originCluster":"West OH Region","destinationCluster":"Green Bay Region","corridor":"West OH Region-Green Bay Region","industryID":72,"industry":"Accommodation and Food Services","originDH": 250, "destDH": 300, "puGap": 300, "totalDH": 550 }
    newloads_df.loc[4] = {"loadID":15744265,"loaddate":"2019-01-07","StateType":1,"value":50000,"customer_rate":1080.93,"equipment":"V,R","equipmentlength":48,"miles":411,"pu_appt":"2019-01-07","origin":"Irwindale-CA","destination":"Fairfield-CA","originLon":-117.875,"originLat":34.151,"destinationLon":-122.028,"destinationLat":38.249,"originCluster":"Ontario CA Region","destinationCluster":"Tracy Region","corridor":"Ontario CA Region-Tracy Region","industryID":31,"industry":"Manufacturing","originDH": 250, "destDH": 300, "puGap": 300, "totalDH": 550 }
    newloads_df.loc[5] = {"loadID":15759398,"loaddate":"2019-01-07","StateType":1,"value":100000,"customer_rate":2254.32,"equipment":"F,SD,K,FWS","equipmentlength":30,"miles":558,"pu_appt":"2019-01-07","origin":"Mercer-PA","destination":"Boxborough-MA","originLon":-80.24,"originLat":41.227,"destinationLon":-71.527,"destinationLat":42.492,"originCluster":"Warren OH Region","destinationCluster":"Boston Region","corridor":"Warren OH Region-Boston Region","industryID":31,"industry":"Manufacturing","originDH": 250, "destDH": 300, "puGap": 300, "totalDH": 550 }
    newloads_df.loc[6] = {"loadID":15743931,"loaddate":"2019-01-07","StateType":1,"value":50000,"customer_rate":2133.57,"equipment":"V,R","equipmentlength":48,"miles":1208.8,"pu_appt":"2019-01-07","origin":"Seabrook-TX","destination":"Mesa-AZ","originLon":-95.024,"originLat":29.564,"destinationLon":-111.847,"destinationLat":33.432,"originCluster":"Houston Region","destinationCluster":"Phoenix Region","corridor":"Houston Region-Phoenix Region","industryID":42,"industry":"Wholesale Trade","originDH": 250, "destDH": 300, "puGap": 300, "totalDH": 550 }
    newloads_df.loc[7] = {"loadID":15768897,"loaddate":"2019-01-08","StateType":1,"value":100000,"customer_rate":1592.34,"equipment":"V","equipmentlength":53,"miles":666,"pu_appt":"2019-01-08","origin":"Hot Springs-AR","destination":"Cincinnati-OH","originLon":-93.057,"originLat":34.503,"destinationLon":-84.511,"destinationLat":39.097,"originCluster":"Little Rock AR Region","destinationCluster":"Cincinnati Region","corridor":"Little Rock AR Region-Cincinnati Region","industryID":32,"industry":"Manufacturing","originDH": 250, "destDH": 300, "puGap": 300, "totalDH": 550 }
    newloads_df.loc[8] = {"loadID":15752058,"loaddate":"2019-01-07","StateType":1,"value":100000,"customer_rate":1600,"equipment":"V","equipmentlength":53,"miles":757,"pu_appt":"2019-01-07","origin":"Weiner-AR","destination":"Scranton-SC","originLon":-90.898,"originLat":35.62,"destinationLon":-79.744,"destinationLat":33.914,"originCluster":"North AR Region","destinationCluster":"SC Region","corridor":"North AR Region-SC Region","industryID":31,"industry":"Manufacturing","originDH": 250, "destDH": 300, "puGap": 300, "totalDH": 550 }
    newloads_df.loc[9] = {"loadID":15765622,"loaddate":"2019-01-07","StateType":1,"value":50000,"customer_rate":1308.06,"equipment":"V,R","equipmentlength":48,"miles":1014,"pu_appt":"2019-01-07","origin":"Aurora-CO","destination":"Pico Rivera-CA","originLon":-104.862,"originLat":39.74,"destinationLon":-117.998,"destinationLat":34.002,"originCluster":"Denver Region","destinationCluster":"Ontario CA Region","corridor":"Denver Region-Ontario CA Region","industryID":31,"industry":"Manufacturing","originDH": 250, "destDH": 300, "puGap": 300, "totalDH": 550 }


    # newloads_df.at[0, "loadID"] = 15563494
    # newloads_df.at[0, "loaddate"] = '2019-01-07'
    # newloads_df.at[0, "StateType"] = 1
    # newloads_df.at[0, "value"] = 100000.0
    # newloads_df.at[0, "customer_rate"] = 1250.0
    # newloads_df.at[0, "equipment"] = 'G'
    # newloads_df.at[0, "equipmentlength"] = 48.0
    # newloads_df.at[0, "miles"] = 541.0
    # newloads_df.at[0, "pu_appt"] = tpd.Timestamp(year=2019, month=1, day=11, hour=16) #Timestamp(‘2017-12-15 19:02:35-0800’, tz=’US/Pacific’)
    # newloads_df.at[0, "origin"] = 'Piscataway-NJ'
    # newloads_df.at[0, "originLon"] = -74.454
    # newloads_df.at[0, "originLat"] = 40.561
    # newloads_df.at[0, "destinationLon"] = -78.946
    # newloads_df.at[0, "destinationLat"] = 34.971
    # newloads_df.at[0, "originCluster"] = 'Elizabeth Region'
    # newloads_df.at[0, "destinationCluster"] = 'Fayetteville NC Region'
    # newloads_df.at[0, "corridor"] = 'Elizabeth Region-Fayetteville NC Region'
    # newloads_df.at[0, "industryID"] = 52
    # newloads_df.at[0, "industry"] = 'Finance and Insurance'

    # newloads_df.at[0, "originDH"] = originDH_default ##originDH & destDH may be settable by truck/default.
    # newloads_df.at[0, "destDH"] = destDH_default
    # newloads_df.at[0, "puGap"] = gap_default
    # newloads_df.at[0, "totalDH"] = totalDH


    return newloads_df


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