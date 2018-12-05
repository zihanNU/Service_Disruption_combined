import unittest
import app_recommender
import pandas as tpd

class RecommenderTest(unittest.TestCase):


    def test_get_odelist_hist(self):
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

        self.assertEqual(_origin, actual["origin"][0], "Expected origin to be equal")
        self.assertEqual(_destination, actual["destination"][0], "Expected destination to be equal")
        self.assertEqual(_corridor, actual["corridor"][0], "Expected corridor to be equal")
        self.assertEqual(_equipment, actual["equipment"][0], "Expected equipment to be equal")
        self.assertEqual(_origin_count, actual["origin_count"][0], "Expected origin_count to be equal")
        self.assertEqual(_origin_count, actual["origin_max"][0], "Expected origin_max to = origin_count (probably a bug)")
        self.assertEqual(_dest_count, actual["dest_count"][0], "Expected dest_count to be equal")
        self.assertEqual(_dest_max, actual["dest_max"][0], "Expected dest_max to be equal")
