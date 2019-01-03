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

