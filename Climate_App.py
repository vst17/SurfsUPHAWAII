# Dependencies

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect Database into ORM clases
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)
# Flask Routes
@app.route("/")
def welcome():
    """List all availbale api routes."""
    return(
        f"<center><h1>Hawaii Precipitation and Weather Data:</h1><br/><br/></center>"
        f"<b>Pick from the available routes below:</b><br/><br/>"
        f"Precipiation from August 23, 2016 to August 23, 2017.<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"A list of all the weather stations in Hawaii.<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"The Temperature Observations (tobs) from August 23, 2016 to August 23, 2017 .<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Type in a single date (i.e., 2015-01-01) to see the min, max and avg temperature since that date.<br/>"
        f"input &ltstart&gt and &ltend&gt in format %Y-%M-%D </br>"
        f"/api/v1.0/&ltstart&gt</br>"
        f"/api/v1.0/&ltstart&gt&&ltend&gt</br>"
    )
begin_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query for the dates and temperature observations from the last year.
    Convert the query results to a Dictionary using date as the 'key 'and 'tobs' as the value."""


    # Retrieve the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date > begin_date).\
                        order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of for the precipitation data
    precipitation_data = []
    for prcp_data in results:
        prcp_data_dict = {}
        prcp_data_dict["Date"] = prcp_data.date
        prcp_data_dict["Precipitation"] = prcp_data.prcp
        precipitation_data.append(prcp_data_dict)
        

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    """Return a json list of stations from the dataset."""
    # Query all the stations
    results = session.query(Station).all()

    # Create a dictionary from the row data and append to a list of all_stations.
    all_stations = []
    for stations in results:
        stations_dict = {}
        stations_dict["Station"] = stations.station
        stations_dict["Station Name"] = stations.name
        stations_dict["Latitude"] = stations.latitude
        stations_dict["Longitude"] = stations.longitude
        stations_dict["Elevation"] = stations.elevation
        all_stations.append(stations_dict)
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a json list of Temperature Observations (tobs) for the previous year"""
    # Query all the stations and for the given date. 
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
                    group_by(Measurement.date).\
                    filter(Measurement.date > begin_date).\
                    order_by(Measurement.station).all()
                    
    # Create a dictionary from the row data and append to a list of for the temperature data.
    temp_data = []
    for tobs_data in results:
        tobs_data_dict = {}
        tobs_data_dict["Station"] = tobs_data.station
        tobs_data_dict["Date"] = tobs_data.date
        tobs_data_dict["Temperature"] = tobs_data.tobs
        temp_data.append(tobs_data_dict)
    
    return jsonify(temp_data)
    
@app.route("/api/v1.0/<start_date>")
def start_stats(start_date):
    #Return a json list of the minimum temperature, the average temperature, and the
    #max temperature for a given start date
    # Query all the stations and for the given date. 
    minimum = session.query(Measurement.tobs, func.min(Measurement.tobs)).filter(Measurement.date >= start_date)
    maximum = session.query(Measurement.tobs, func.max(Measurement.tobs)).filter(Measurement.date >= start_date)
    average = session.query(Measurement.tobs, func.avg(Measurement.tobs)).filter(Measurement.date >= start_date)

    start_temp = {"Tmin": minimum[0][0], "Tmax": maximum[0][0], "Tavg": average[0][0]}
    
    
    return jsonify(start_temp)
    

@app.route("/api/v1.0/<start_date>&<end_date>")
def start(start_date, end_date):
    #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."
    minimum = session.query(Measurement.tobs, func.min(Measurement.tobs)).filter(Measurement.date.between(start_date, end_date))
    maximum = session.query(Measurement.tobs, func.max(Measurement.tobs)).filter(Measurement.date.between(start_date, end_date))
    average = session.query(Measurement.tobs, func.avg(Measurement.tobs)).filter(Measurement.date.between(start_date, end_date))

    start_end_temps = {"Tmin": minimum[0][0], "Tmax": maximum[0][0], "Tavg": average[0][0]}
    
    return jsonify(start_end_temps)

if __name__ == '__main__':
    app.run(debug=True)