from flask import Flask, render_template, jsonify, make_response
import pandas as pd
from sqlalchemy import create_engine, func, MetaData, Table
from sqlalchemy.orm import Session
import os
from config import get_config
from pprint import pprint

app = Flask(__name__)

# App keys and sensity information
app_keys = get_config()

# App global variables
## constants
DB_USER = 'postgres'
DB_SCHEMA = 'data_science_jobs'
JOBS_TBL = 'jobs'

## variables

# helper functions
def get_db_engine():
    if get_db_engine.engine is None:
        postgres_config = app_keys['postgres']
        connection = f"postgresql+psycopg2://{DB_USER}:{postgres_config['password']}@{postgres_config['host']}/{DB_SCHEMA}"
        get_db_engine.engine   = create_engine(connection, pool_recycle=3600);
    return get_db_engine.engine
# python way of defining static variables, we use it to avoid creating a new connection on multiple calls through the flask app
get_db_engine.engine = None

def get_jobs_tbl(engine):
    # Reflect jobs table
    metadata = MetaData()
    metadata.reflect(bind=engine)
    Jobs = metadata.tables['jobs']

    return Jobs

@app.route("/api/data-science/load-data")
def load_data():
    """
    This endpoint loads the csv data into the table `data_science_jobs`.`jobs`
    """
    jobs_df = None
    with open(os.path.join('.', 'data', 'DS_Jobs.csv'), 'r', encoding='utf8') as fd:
        jobs_df = pd.read_csv(fd)

    # rename columns before creating table
    jobs_df = jobs_df.rename(columns={
        'Job Title': 'job_title',
        'Salary Estimate': 'salary_estimate',
        'Job Description': 'job_description',
        'Rating': 'rating',
        'Company Name': 'company_name',
        'Location': 'location',
        'Headquarters': 'headquarters',
        'Size': 'size',
        'Type of ownership': 'type_of_ownership',
        'Industry': 'industry',
        'Sector': 'sector',
        'Revenue': 'revenue'
    }).copy()

    # get sqlalchemy engine
    engine = get_db_engine()

    res = None
    with engine.connect() as con:
        jobs_df.to_sql('jobs', con, if_exists='replace', method='multi', index_label='id')
        result = con.execute(f"select count(*) as total_entries from {JOBS_TBL}")

        # fetch results
        total_job_entries = {}
        for row in result:
            total_job_entries = dict(row)

        res = make_response(jsonify(total_job_entries), 200)

    return res

@app.route("/api/data-science/job-openings/totals_by_position")
def job_openings_totals_by_position():
    # get sqlalchemy engine
    engine = get_db_engine()

    # get reflected Job table
    Jobs = get_jobs_tbl(engine)

    with engine.connect() as con:
        session = Session(con)
        job_count_totals = func.count(Jobs.columns.job_title)
        results = session.query(Jobs.columns.job_title, job_count_totals) \
            .group_by(Jobs.columns.job_title) \
            .order_by(job_count_totals.desc()) \
            .all()

    res = make_response(jsonify(results), 200)
    return res

@app.route("/api/data-science/highest-demand")
def highest_demand():
    res = make_response(jsonify({"highest-demand": 30}), 200)
    return res

@app.route("/api/data-science/average-salary")
def average_salary():
    res = make_response(jsonify({"average-salary": 40}), 200)
    return res

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
