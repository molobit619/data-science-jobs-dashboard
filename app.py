from flask import Flask, render_template, jsonify, make_response, Response
import pandas as pd
from sqlalchemy import create_engine, func, MetaData, Table
from sqlalchemy.orm import Session
import os
from config import get_config
import numpy as np
from pprint import pprint
from matplotlib.figure import Figure
from matplotlib import cm
from matplotlib.backends.backend_agg import FigureCanvasAgg
import random
import io

app = Flask(__name__)

# App keys and sensity information
app_keys = get_config()

# App global variables
# constants
DB_USER = 'postgres'
DB_SCHEMA = 'data_science_jobs'
JOBS_TBL = 'jobs'

# variables

# helper functions
def get_skills_totals_by_tech_df():
    # get sqlalchemy engine
    engine = get_db_engine()

    # get reflected Job table
    Jobs = get_jobs_tbl(engine)

    #aggregate totals for each skell
    python_sum = func.sum(Jobs.columns.python)
    excel_sum = func.sum(Jobs.columns.excel)
    hadoop_sum = func.sum(Jobs.columns.hadoop)
    spark_sum = func.sum(Jobs.columns.spark)
    aws_sum = func.sum(Jobs.columns.aws)

    with engine.connect() as con:
        session = Session(con)
        result = session.query(python_sum, excel_sum, hadoop_sum, spark_sum, aws_sum) \
            .first()

    totals_by_tech_df = pd.DataFrame([float(entry) for entry in result])
    totals_by_tech_df = totals_by_tech_df.transpose()

    #assign columns to dataframe
    totals_by_tech_df.columns = ['python', 'excel', 'hadoop', 'spark', 'aws']

    return totals_by_tech_df


def get_db_engine():
    if get_db_engine.engine is None:
        postgres_config = app_keys['postgres']
        connection = f"postgresql+psycopg2://{DB_USER}:{postgres_config['password']}@{postgres_config['host']}/{DB_SCHEMA}"
        get_db_engine.engine = create_engine(connection, pool_recycle=3600)
    return get_db_engine.engine


# python way of defining static variables, we use it to avoid creating a new connection on multiple calls through the flask app
get_db_engine.engine = None


def get_jobs_tbl(engine):
    # Reflect jobs table
    metadata = MetaData()
    metadata.reflect(bind=engine)
    Jobs = metadata.tables['jobs']

    return Jobs


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/location")
def locations():
    return render_template("locations.html")

@app.route("/industries")
def industries():
    return render_template("industries.html")


@app.route("/salaries")
def avgsalary():
    return render_template("avgsalary.html")

@app.route("/skills")
def skills():
    return render_template("skills.html")

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

    # replace -1 values with NaN using np
    jobs_df = jobs_df.replace('-1', np.nan)

    # drop all NaN values
    jobs_df = jobs_df.dropna(axis=0, how='any')

    # drop all locations not specified with city, that only list United States
    jobs_df = jobs_df[jobs_df['location'] != 'United States']

    # get sqlalchemy engine
    engine = get_db_engine()

    with engine.connect() as con:
        jobs_df.to_sql('jobs', con, if_exists='replace',
                       method='multi', index_label='id')
        result = con.execute(
            f"select count(*) as total_entries from {JOBS_TBL}")

        # fetch results
        total_job_entries = {}
        for row in result:
            total_job_entries = dict(row)
        print(total_job_entries)

@app.route("/api/data-science/skills/totals_by_technology")
def skills_totals_by_tech():
    totals_by_tech_df = get_skills_totals_by_tech_df()
    return make_response(jsonify(totals_by_tech_df.to_dict(orient='split')))

@app.route("/api/data-science/skills/totals_by_technology.png")
def skills_totals_by_tech_png():
    totals_by_tech_df = get_skills_totals_by_tech_df()
    totals_by_tech_df = totals_by_tech_df.transpose() \
            .reset_index() \
            .rename(columns={'index': 'skill', 0: 'postings'})

    # Create bar chart for skills
    # https://www.machinelearningplus.com/plots/top-50-matplotlib-visualizations-the-master-plots-python/

    all_colors = list(cm.colors.cnames.keys())
    random.seed(100)
    c = random.choices(all_colors, k=7)

    # Plot Bars
    fig = Figure(figsize=(10,6))
    ax = fig.add_subplot(111)

    ax.bar(totals_by_tech_df.skill, totals_by_tech_df.postings, color=c, width=.5)
    for i, val in enumerate(totals_by_tech_df.postings.values):
        ax.text(i, val, float(val), horizontalalignment='center', verticalalignment='bottom', fontdict={'fontweight':400, 'size':12})

    ax.title.set_text("Desirable Skills")

    # capture image output
    output = io.BytesIO()

    canvas = FigureCanvasAgg(fig)
    canvas.print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route("/api/data-science/skills/top_positions_by_tech/<tech>")
def skills_top_ten_by_tech(tech):
    # get sqlalchemy engine
    engine = get_db_engine()

    # get reflected Job table
    Jobs = get_jobs_tbl(engine)

    filters = {
        'python': Jobs.columns.python,
        'excel':  Jobs.columns.excel,
        'hadoop': Jobs.columns.hadoop,
        'spark':  Jobs.columns.spark,
        'aws':    Jobs.columns.aws
    }

    active_tech_filter = None

    try:
        active_tech_filter = filters[tech]
    except KeyError as err:
        pass

    print(active_tech_filter)
    with engine.connect() as con:
        session = Session(con)
        statement = session.query(Jobs.columns.job_title, Jobs.columns.salary_estimate, Jobs.columns.rating, Jobs.columns.company_name, Jobs.columns.location) \
            .filter(active_tech_filter == 1 ) \
            .statement

        results_df = pd.read_sql(statement, session.bind)

    return make_response(jsonify(results_df.to_dict(orient='split')))

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

    #res = make_response(jsonify(results), 200)
    # print(results)
    res = [[x, y]for[x, y] in results]
    return jsonify(res)


@app.route("/api/data-science/job-openings/totals_by_location")
def job_openings_totals_by_location():
    # get sqlalchemy engine
    engine = get_db_engine()

    # get reflected Job table
    Jobs = get_jobs_tbl(engine)

    with engine.connect() as con:
        session = Session(con)
        job_count_totals = func.count(Jobs.columns.job_title)
        results = session.query(Jobs.columns.location, job_count_totals) \
            .group_by(Jobs.columns.location) \
            .order_by(job_count_totals.desc()) \
            .all()

    #res = make_response(jsonify(results), 200)
    # return results
    res = [[x, y]for[x, y] in results]
    return jsonify(res)


@app.route("/api/data-science/job-openings/totals_by_industry.png")
def job_openings_totals_by_industry_png():
    # get sqlalchemy engine
    engine = get_db_engine()

    # get reflected Job table
    Jobs = get_jobs_tbl(engine)

    industry_df = None

    # load dataframe using sqlalchemy
    with engine.connect() as con:
        session = Session(con)
        job_count_totals = func.count(Jobs.columns.job_title)
        statement = session.query(Jobs.columns.industry, job_count_totals) \
            .group_by(Jobs.columns.industry) \
            .order_by(job_count_totals.desc()) \
            .statement
        industry_df = pd.read_sql(statement, session.bind)

    industry_df = industry_df.rename(columns={'count_1': 'postings'})

    # Create circle bar for job posting count for each industry
    # https://www.python-graph-gallery.com/circular-barplot-basic

    fig = Figure(figsize=(12, 10))

    ax = fig.add_subplot(111, polar=True)
    ax.axis('off')

    # Constants = parameters controling the plot layout:
    upperLimit = 66
    lowerLimit = 8
    labelPadding = 4

    # Compute max and min in the dataset
    max = industry_df.postings.max()

    # Let's compute heights: they are a conversion of each item value in those new coordinates
    # In our example, 0 in the dataset will be converted to the lowerLimit (10)
    # The maximum will be converted to the upperLimit (100)
    slope = (max - lowerLimit) / max
    heights = slope * industry_df.postings + lowerLimit

    # Compute the width of each bar. In total we have 2*Pi = 360°
    width = 2 * np.pi / len(industry_df.index)

    # Compute the angle each bar is centered on:
    indexes = list(range(1, len(industry_df.index)+1))
    angles = [element * width for element in indexes][::-1]
    angles

    # Draw bars
    bars = ax.bar(
        x=angles,
        height=heights,
        width=width,
        bottom=lowerLimit,
        linewidth=2,
        edgecolor="white",
        color="#33FF82",
    )

    # Add labels
    for bar, angle, height, label in zip(bars, angles, heights, industry_df["industry"]):

        # Labels are rotated. Rotation must be specified in degrees :(
        rotation = np.rad2deg(angle)

        # Flip some labels upside down
        alignment = ""
        if angle >= np.pi/2 and angle < 3*np.pi/2:
            alignment = "right"
            rotation = rotation + 180
        else:
            alignment = "left"

        # Finally add the labels
        ax.text(
            x=angle,
            y=lowerLimit + bar.get_height() + labelPadding,
            s=label,
            ha=alignment,
            va='center',
            rotation=rotation,
            rotation_mode="anchor")

    # capture image output
    output = io.BytesIO()

    canvas = FigureCanvasAgg(fig)
    canvas.print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route("/api/data-science/job-openings/average_salary.png")
def job_openings_average_salary_png():
    # get sqlalchemy engine
    engine = get_db_engine()

    # get reflected Job table
    Jobs = get_jobs_tbl(engine)

    jobs_df = None

    # load dataframe using sqlalchemy
    with engine.connect() as con:
        session = Session(con)
        statement = session.query(Jobs).statement
        jobs_df = pd.read_sql(statement, session.bind)

    # TODO: implement salary graph
    return make_response(jobs_df.to_html(), 200)


@app.route("/api/data-science/highest-demand")
def highest_demand():
    res = make_response(jsonify({"highest-demand": 30}), 200)
    return res


@app.route("/api/data-science/average-salary")
def average_salary():
    res = make_response(jsonify({"average-salary": 40}), 200)
    return res


if __name__ == "__main__":
    load_data()
    app.run(debug=True)
