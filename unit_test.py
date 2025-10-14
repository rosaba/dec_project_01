import unittest
import pandas as pd
from crash_vehicle_join_tf import transform_data  

class TestTransformData(unittest.TestCase):
    def setUp(self):
        # Sample crash data
        self.crash_data = pd.DataFrame([
            {
                "collision_id": "4849452",
                "crash_date": "2025-10-10",
                "crash_time": "23:05",
                "borough": "NYC",
                "vehicle_type_code1": "Sedan",
                "location": {"latitude": "40.570835", "longitude": "-74.16983", "human_address": "{}"},
                "number_of_persons_injured": "1",
                "number_of_persons_killed": "0",
                "number_of_pedestrians_injured": "0",
                "number_of_pedestrians_killed": "0",
                "number_of_cyclist_injured": "0",
                "number_of_cyclist_killed": "0",
                "number_of_motorist_injured": "1",
                "number_of_motorist_killed": "0"
            }
        ])

        # Sample vehicles data
        self.vehicles_data = pd.DataFrame([
            {
                "collision_id": "4849452",
                "pre_crash": "Going Straight Ahead"
            }
        ])

    def test_transform_output(self):
        transformed = transform_data(self.crash_data, self.vehicles_data)

        # Check output is a DataFrame
        self.assertIsInstance(transformed, pd.DataFrame)

        # Check expected columns exist
        expected_columns = [
            "collision_id", "crash_date", "crash_time", "borough",
            "vehicle_type_code1_clean", "day_of_week", "Weekend_Weekday",
            "latitude", "longitude", "pre_crash"
        ]
        for col in expected_columns:
            self.assertIn(col, transformed.columns)

        # Check that join worked
        self.assertEqual(transformed.loc[0, "pre_crash"], "Going Straight Ahead")

        # Check that borough was filled
        self.assertEqual(transformed.loc[0, "borough"], "NYC")

if __name__ == '__main__':
    unittest.main()