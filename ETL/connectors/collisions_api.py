import requests
from loguru import logger

class CollisionsApiClient:
    """
    Client for interacting with the NYC Open Data Collisions API.

    Handles authentication via app token and provides methods to fetch vehicle collision data.
    """

    def __init__(self, app_token: str) -> None:
        """
        Initializes the API client with the required app token.

        Args:
            app_token (str): Socrata API token for authenticating requests.
        """
        self.app_token = app_token
        self.base_url = "https://data.cityofnewyork.us/resource"
        

    def get_collisions_datasets(self, dataset_id: str, params: dict) -> dict:
        """
        Fetch collision dataset from the NYC Open Data API.

        Args:
            dataset_id (str): The identifier of the dataset to fetch.
            params (dict): Query parameters for the API request.

        Returns:
            dict: Parsed JSON response from the API.

        Raises:
            Exception: If the request fails with a non-200 status code.
        """

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
        
    def get_all_collisions_since(self, dataset_id: str, since_date: str, limit: int = 1000, max_rows: int = 100000) -> list:
        """
        Fetches all collision records since a specified crash date.

        Retrieves data in paginated batches using the given `limit`, up to a maximum of `max_rows`.

        Args:
            dataset_id (str): The ID of the dataset to query.
            since_date (str): The crash_date (in ISO format) to start fetching records from.
            limit (int, optional): Number of records per page (default is 1000).
            max_rows (int, optional): Maximum number of records to fetch in total (default is 100000).

        Returns:
            list: A list of dictionaries representing collision records.

        Raises:
            Exception: If the API call fails during any page request.
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