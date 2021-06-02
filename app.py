from flask import Flask, render_template, jsonify, make_response

app = Flask(__name__)

@app.route("/api/data-science/job-openings")
def job_openings():
    res = make_response(jsonify({"job-openings": 20}), 200)
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
