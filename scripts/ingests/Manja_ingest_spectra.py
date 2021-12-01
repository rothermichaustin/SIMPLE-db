from scripts.ingests.ingest_utils import *
from scripts.ingests.utils import *
import pandas as pd
import numpy.ma as ma
import dateutil
from sqlalchemy import func

SAVE_DB = False  # save the data files in addition to modifying the .db file
RECREATE_DB = False  # recreates the .db file from the data files

logger.setLevel(logging.INFO)

db = load_simpledb('SIMPLE.db', recreatedb=RECREATE_DB)

# Read in CSV file as Astropy table
data = Table.read('scripts/ingests/Manja_spectra4.csv')

# ingest_publication(db, doi='10.1086/507522')

ingest_sources(db, data['Source'], data['reference'], comments=data['comments'])

ingest_spectra(db, data['Source'], data['Spectrum'], 'nir', 'VLT', 'ISAAC', 'SW LRes', data['observation_date'], data['reference'], comments=data['comments'])
