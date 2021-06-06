import psycopg2
import pandas as pd
import credentials as creds
from flask import Flask

# Set up a connection to the postgres server.
# Add your password in credentials.py first.
conn_string = "host=" + creds.PGHOST + " port=" + "5432" + " dbname=" + creds.PGDATABASE + " user=" + creds.PGUSER \
    + " password=" + creds.PGPASSWORD
conn = psycopg2.connect(conn_string)
print("Connected!")

# Create a cursor object
cursor = conn.cursor()
app = Flask(__name__)


@app.route("/")
def index():
    # Route to all pages
    return('<h1>Welcome! Navigate to routes below to see:</h1> <h2><ul>'
           '<li><a href="http://127.0.0.1:5000/data-science/location">Which locations have the most data science job postings?</a><br></li><br>'
           '<li><a href="http://127.0.0.1:5000/data-science/industry">Which industries have the highest demand for data scientists?</a><br></li><br>'
           '<li><a href="http://127.0.0.1:5000/data-science/skill">What are the desirable skills?</a><br></li><br>'
           '<li><a href="http://127.0.0.1:5000/data-science/avgsalary">What is the average salary by state?</a><br></li><br></ul></h2>')
#    return render_template("index.html")


@app.route('/data-science/location')
def location():
    # Load the data from table named locations
    data = pd.read_sql('SELECT * FROM locations', conn)
    return (data.to_html())


@app.route('/data-science/industry')
def industry():
    data = pd.read_sql('SELECT * FROM industry', conn)
    return (data.to_html())


@app.route('/data-science/skill')
def skill():
    data = pd.read_sql('SELECT * FROM skill', conn)
    return (data.to_html())


@app.route('/data-science/avgsalary')
def avgsalary():
    data = pd.read_sql('SELECT * FROM averagesalary', conn)
    return (data.to_html())


if __name__ == "__main__":
    app.run(debug=True)
