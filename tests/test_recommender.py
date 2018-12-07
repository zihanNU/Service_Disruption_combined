import app_recommender
import pandas as tpd

def test_get_odelist_hist():
    my_df = tpd.DataFrame(columns=['originCluster', 'destinationCluster', 'corridor', 'equipment', 'origin_count', 'dest_count', 'dest_max'])

    _origin = "Nashville Region"
    _destination = "South GA Region"
    _corridor = "Atlanta Region-South East AL Region"
    _equipment = "Equip"
    _origin_count = 29
    _dest_count = 35
    _dest_max = 111

    my_df.loc[0] = { "originCluster": _origin, "destinationCluster" : _destination, 
                        "corridor" : _corridor, "equipment" : _equipment, 
                        "origin_count" : _origin_count, "dest_count" : _dest_count, "dest_max" : _dest_max }

    actual = app_recommender.get_odelist_hist(my_df)

    assert _origin == actual["origin"][0]
    assert _destination == actual["destination"][0]
    assert _corridor == actual["corridor"][0]
    assert _equipment == actual["equipment"][0]
    assert _origin_count == actual["origin_count"][0]
    assert _origin_count == actual["origin_max"][0] #there is a bug in the original code here.
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


def test_epic_fail():
    assert True == False