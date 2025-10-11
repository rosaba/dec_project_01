# dec_project_01
## NYC collisions
*open data sources:*
- https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data
- https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Vehicles/bm4k-52h4/about_data
- https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Person/f55k-p6yu/about_data

### BEFORE running the code
- Create conda environment from yml:
```conda env create -f environment.yml```

- Activate environment:
```conda activate proj1env```

- create X-App-Token at https://data.cityofnewyork.us/profile/edit/developer_settings
- Customize .env file from template.env

### RUN LOCALLY
- in .env set SERVER_NAME=localhost
- run pipeline:
```cd app```
```python -m ETL.pipeline```

- run unit tests from directory app:
```PYTHONPATH=. pytest ETL_tests```

### RUN WITH DOCKER:
- in .env set SERVER_NAME=collisions_postgres
- ```docker compose down -v```
- ```docker compose up --build```


