# dec_project_01
https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data
https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Vehicles/bm4k-52h4/about_data
https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Person/f55k-p6yu/about_data

### BEFORE running the code
- Create conda environment from yml:
```conda env create -f environment.yml```

- Activate environment:
```conda activate proj1env```

- create X-App-Token at https://data.cityofnewyork.us/profile/edit/developer_settings
- Customize .env file from template.env

# RUN
- run pipeline:
```cd ETL```
```python pipeline.py```