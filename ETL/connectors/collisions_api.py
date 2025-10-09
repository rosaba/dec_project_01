import requests
from loguru import logger

class CollisionsApiClient:
    def __init__(self, app_token: str):
        self.app_token = app_token
        self.base_url = "https://data.cityofnewyork.us/resource"
        

    def get_collisions_datasets(self, dataset_id: str, params: dict) -> dict:

        response = requests.get(
            f"{self.base_url}/{dataset_id}", 
            params=params,
            headers={'X-App-Token': self.app_token}
            )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to extract data from NYC Collisions API. Status Code: {response.status_code}. Response: {response.text}"
            )
        
    def get_all_collisions_since(self, dataset_id: str, since_date: str, limit: int = 1000, max_rows: int = 100000):
        """
        Pulls all records since a given crash_date, paginated.
        """
        collected_data = []

        for offset in range(0, max_rows, limit):
            params = {
                "$where": f"crash_date > '{since_date}' AND crash_time IS NOT NULL",
                "$order": "crash_date DESC, crash_time DESC",
                "$limit": str(limit),
                "$offset": offset
            }

            try:
                data = self.get_collisions_datasets(dataset_id=dataset_id, params=params)
                if not data:
                    break
                collected_data.extend(data)
                logger.info(f"Collected {len(data)} rows of data with id {dataset_id} since {since_date}: now at {len(collected_data)} in total")
            except Exception as e:
                print(f"Error collecting data for dataset with id '{dataset_id}': {str(e)}")

        return collected_data