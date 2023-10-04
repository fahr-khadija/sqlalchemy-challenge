# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta
import pandas as pd
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station=Base.classes.station

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
    return (
        f"Welcome to the Climate App!<br/>"
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/end_date"
    )

# Define the /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
   
def precipitation():
    # Calculate the date 12 months ago from the most recent date
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)

    # Query precipitation data for the last 12 months
    precipitation_data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago).all()
    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

# Define the /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    # Query for a list of stations
    station_list = session.query(stations.station).all()

    # Convert the query results to a list
    #stations_all = list(np.ravel(station_list))
    stations_a = [station[0] for station in station_list]
    return jsonify(stations_a)

# the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date 12 months ago from the most recent date
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)

    # Query temperature observations for the last 12 months of the most active station
    temperature_data = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == stations_a).\
        filter(measurement.date >= one_year_ago).all()

    # Convert the query results to a list of dictionaries
    temperature_list = [{"Date": date, "Temperature": tobs} for date, tobs in temperature_data]

    return jsonify(temperature_list)

# Define the /api/v1.0/start_date and /api/v1.0/start_date/end_date routes
@app.route("/api/v1.0/<start_date>")
@app.route("/api/v1.0/<start_date>/<end_date>")
def temperature_range(start_date, end_date=None):
    # Define the query for calculating temperature statistics
    if end_date:
        temperature_stats = session.query(
            func.min(measurement.tobs).label('min_temperature'),
            func.avg(measurement.tobs).label('avg_temperature'),
            func.max(measurement.tobs).label('max_temperature')
        ).filter(and_(measurement.date >= start_date, measurement.date <= end_date)).all()
    else:
        temperature_stats = session.query(
            func.min(measurement.tobs).label('min_temperature'),
            func.avg(measurement.tobs).label('avg_temperature'),
            func.max(measurement.tobs).label('max_temperature')
        ).filter(measurement.date >= start_date).all()

    # Create a dictionary for  temperature statistics
    
    stats_dict = {
        "Minimum Temp": temperature_stats[0].min_temperature,
        "Average Temp": temperature_stats[0].avg_temperature,
        "Maximum Temp": temperature_stats[0].max_temperature
    }

    return jsonify(stats_dict)

if __name__ == "__main__":
    app.run(debug=True)
