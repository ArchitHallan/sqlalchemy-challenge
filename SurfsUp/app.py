# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

from flask import Flask, jsonify

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route('/')
def homepage():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )
@app.route('/api/v1.0/precipitation')
def precipitation():
    """Return a list of date and precipitation values."""
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = (dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)).strftime("%Y-%m-%d")
    
    # Query date and precipitation values
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    
    session.close()

    # Convert to dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    """Return a list of all stations."""
    session = Session(engine)
    
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Convert to dictionary
    stations_list = [{"station": station, "name": name} for station, name in results]

    return jsonify(stations_list)


@app.route('/api/v1.0/tobs')
def tobs():
    """Return a list of TOBs for the last year of data for the most active station."""
    session = Session(engine)

    # Identify the most active station (hardcoded as per requirements)
    most_active_station = 'USC00519281'
    
    # Calculate the date 1 year ago from the last data point for this station
    recent_date = session.query(func.max(Measurement.date)).filter(Measurement.station == most_active_station).scalar()
    one_year_ago = (dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)).strftime("%Y-%m-%d")

    # Query for the date and temperature observations for the last year
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).filter(Measurement.station == most_active_station).all()
    
    session.close()

    # Convert to dictionary
    tobs_list = {date: tobs for date, tobs in results}

    return jsonify(tobs_list)



@app.route('/api/v1.0/<start>')
def start_date(start):
    """Return a list of min, avg, and max temperatures from the start date to the end of the dataset."""
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    session.close()

    # Convert to dictionary
    temps = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in results]

    return jsonify(temps)

@app.route('/api/v1.0/<start>/<end>')
def start_end_date(start, end):
    """Return a list of min, avg, and max temperatures from the start date to the end date."""
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()

    # Convert to dictionary
    temps = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in results]

    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)
