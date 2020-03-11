import argparse
import requests
import json
import time
from datetime import datetime
from datetime import timedelta
import logging
import logging.config
import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from restbus import restbus
import models

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

db.app = app
db.init_app(app)

INTERVAL = 60


def setup_logging(default_path='logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    """Setup logging configuration """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


if __name__ == "__main__":
    '''Script to read data via the RESTBUS API and save to a database. '''
    parser = argparse.ArgumentParser(description='Read the RestBus API')
    parser.add_argument(
        '-o', '--logfile', help='JSON file with the logger configuration', required=True)
    parser.add_argument(
        '-r', '--route', help='The route number to gather data on', required=False, default="1")
    parser.add_argument('-a', '--all', dest='all', action='store_true',
                        help='Collect all vehicles', required=False, default=False)
    args = parser.parse_args()
    # Create the logging for any type of messages we want to send to a file
    setup_logging(default_path=args.logfile)
    logger = logging.getLogger(__name__)
    # Create an instance of the API
    api1 = restbus()
    # Grab either all the locations or for a specific route
    while True:
        if args.all == True:
            vehicles = api1.get_json('vehicles/')
        else:
            vehicles = api1.get_json('routes/{}/vehicles/'.format(args.route))
        if not vehicles == "":
            for vehicle in vehicles:
                timenow = datetime.now()
                true_time = timenow - \
                    timedelta(seconds=int(vehicle['secsSinceReport']))
                # Save the data to the database
                total_secs = (true_time - true_time.replace(hour=0, minute=0, second=0, microsecond=0)).seconds
                loc = models.Location(datetime=timenow,
                               rid=vehicle['routeId'], vid=vehicle['id'], secs=int(
                                   vehicle['secsSinceReport']),
                               kph=int(vehicle['kph']), head=int(vehicle['heading']), dir=vehicle['directionId'],
                               lat=float(vehicle['lat']), lon=float(vehicle['lon']),
                               timeInSec=total_secs,
                               timeInMin=int(total_secs/60),
                               timeInHour=int(total_secs/3600),
                               year=timenow.timetuple().tm_year,
                               dow=timenow.weekday() + 1,
                               doy=timenow.timetuple().tm_yday)
                db.session.add(loc)
                db.session.commit()

        time.sleep(INTERVAL)
