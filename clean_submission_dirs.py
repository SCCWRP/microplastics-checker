import os
import shutil
from sqlalchemy import create_engine
import pandas as pd

eng = os.environ.get("DB_CONNECTION_STRING")

submissionids = pd.read_sql("SELECT DISTINCT submissionid FROM submission_tracking_table WHERE submit = 'yes'", eng).submissionid.tolist()

submissionids = [str(s) for s in submissionids]

incomplete_submissionids = [str(d) for d in os.listdir('files') if str(d) not in submissionids]

for submissionid in incomplete_submissionids:
    shutil.rmtree(os.path.join('files',submissionid))

