#!/usr/bin/python3

import pandas as pd
from influxdb import DataFrameClient
import time
import datetime

column_names=['Build', 'ID', 'Summary', 'Component', 'Status', 'URL', 'BUGURL']
df = pd.read_csv('/root/bugs_over_builds.csv', skiprows=[0], index_col=[0], parse_dates=[0], names=column_names, skipinitialspace=True)
mytag={}
for eachbuild, df_eachbuild in df.groupby('Build'):
    mytag['Build'] = eachbuild
    print("MY TAG IS ", mytag)
    print("DF BUILD IS" , df_eachbuild)
    for eachstatus, df_eachbuild_eachstatus in df_eachbuild.groupby('Status'):
        mytag['Status'] = eachstatus
        client = DataFrameClient(host='10.162.168.44', username='root', password='susetesting', database='bugs_over_builds')
        client.write_points(df_eachbuild_eachstatus, 'test1',  time_precision='ms', tags=mytag)


