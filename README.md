# dec_project_01
## NYC collisions
*open data sources:*
- https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data
- https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Vehicles/bm4k-52h4/about_data
- https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Person/f55k-p6yu/about_data

## Approach and challenges

1- Data Source in NYC Collison Open API 

2- We extracted three data from API, collison data, vehciles data, person data

3- We faced a challenge that we could not find the updated date, as result of which we to use max data of crash date from each file ( for incremental load) to get the most updated data for upsert and also the data can be extracted using sql. Since there was no updated date, our project is not tracking the historical changes.

4- We then post the data in postgress 

5- We also did one transformation to answer questions how many are the crashes happening each week and uploading it back to postgres DB.

6- We then dockerized it and used Amazon services for deployiong it on cloud.


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
```python -m ELT.pipeline```

- run unit tests from directory app:
```PYTHONPATH=. pytest ELT_tests```

### RUN WITH DOCKER:
- in .env set SERVER_NAME=collisions_postgres
- ```docker compose down -v```
- ```docker compose up --build```

### Architecture Diagram

<img width="716" height="755" alt="Screenshot 2025-10-13 at 22 18 48" src="https://github.com/user-attachments/assets/c233a7ea-f9b7-4547-97d4-f3dd7511ec31" />

### Cloud Screenshots

## In this Step we have created IAM user.
<img width="1302" height="493" alt="Screenshot 2025-10-13 at 21 44 46" src="https://github.com/user-attachments/assets/8bddbb5b-c2e1-4569-b14a-ab4e4621a260" />

## In this Step we are attaching relevant Policies to IAM user.
<img width="1302" height="753" alt="Screenshot 2025-10-13 at 21 45 14" src="https://github.com/user-attachments/assets/016781ef-9a88-44cf-9cac-d4f7a6f34660" />
<img width="1302" height="819" alt="Screenshot 2025-10-13 at 21 45 31" src="https://github.com/user-attachments/assets/4cd85c73-a086-4e51-b7d7-c3fd702979a1" />

## Creating Repo in ECR (BY IAM user) and uploading docker image
<img width="1302" height="551" alt="Screenshot 2025-10-13 at 21 48 39" src="https://github.com/user-attachments/assets/45602677-9733-4c4b-8c06-926a6d47709a" />
<img width="1302" height="678" alt="Screenshot 2025-10-13 at 21 48 45" src="https://github.com/user-attachments/assets/2b830a20-dfa1-47ff-b675-ae574898b0a1" />

## Creating Compute Cluster in ECS
<img width="1302" height="678" alt="Screenshot 2025-10-13 at 21 49 27" src="https://github.com/user-attachments/assets/8118deb9-3d6b-4499-9d40-06e7743282d9" />

## Creating destination DB and security group for DB

<img width="1302" height="678" alt="Screenshot 2025-10-13 at 21 50 05" src="https://github.com/user-attachments/assets/4eeafbdb-3c90-4bb1-8921-63639f640cd1" />
<img width="1254" height="755" alt="Screenshot 2025-10-14 at 16 08 26" src="https://github.com/user-attachments/assets/e69530cf-ff82-492f-a3f3-417312292757" />
<img width="1301" height="755" alt="Screenshot 2025-10-14 at 16 08 34" src="https://github.com/user-attachments/assets/dc1a6b4a-74b8-4df3-817d-3e5162173075" />


## Log monitoring through cloud watch
<img width="1302" height="810" alt="Screenshot 2025-10-13 at 21 50 45" src="https://github.com/user-attachments/assets/98e5fda2-d35a-43d1-8c2e-1765ff7cb038" />




