import numpy as np

import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/'start_date'/'end_date'"
       
    )


@app.route("/api/v1.0/precipitation")
def date_prcp():
    """Return a list of all dates and precipitation"""
    # Query date & prcp
    query = """
                SELECT m.date, m.prcp
                FROM Measurement as m
                ORDER BY m.date DESC"""

    df = pd.read_sql_query(query, engine)
    date_prcp = df.set_index(['date'])['prcp'].to_dict()


    return jsonify(date_prcp)


@app.route("/api/v1.0/tobs")
def tobs(): 
    """query for the dates and temperature observations 
    from a year from the last data point.
     Return a JSON list of Temperature Observations (tobs) for 
    the previous year."""
    
    temperature_query = """SELECT * FROM (SELECT m.date,
    m.tobs
    FROM Measurement as m
    WHERE m.date >= (SELECT DATE(max(date), '-1 year')
    FROM Measurement as m)
    ORDER BY m.date DESC)"""

    df = pd.read_sql_query(temperature_query, engine)
    temp = df.set_index(['date'])['tobs'].to_dict()

    return jsonify(temp)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    station_query = """SELECT station 
    FROM measurement GROUP BY station """
    station_df = pd.read_sql_query(station_query, engine)['station'].tolist()

    return (jsonify(station_df))

@app.route('/api/v1.0/<start>')
def start(start):
    return (jsonify(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()))

@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):
    return (jsonify(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()))

if __name__ == '__main__':
    app.run(debug=True)