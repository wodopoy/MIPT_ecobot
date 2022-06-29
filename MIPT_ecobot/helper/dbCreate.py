import sys 
import os

sys.path.insert(1, os.path.join(sys.path[0], '../'))
from dbworker import db

db.create_all()
