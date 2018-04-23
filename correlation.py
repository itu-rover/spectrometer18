import pandas as pd
import numpy as np
import os, sys
fields = ['count', 'wavelength', 'intensity']
DEBUG = 0

dataframes = []

if DEBUG == 1:
    df = pd.read_csv('dataset/utah3_4/output.csv', skipinitialspace=True, names=fields, sep='\t', skiprows=1)
    df2 = pd.read_csv('dataset/utah3_1/output.csv', skipinitialspace=True, names=fields, sep='\t', skiprows=1)
    print np.corrcoef(df.intensity, df2.intensity)[0][1]
else:
    # Load Dataset
    for path in os.listdir("dataset/"):
        if path != ".DS_Store":
            _df = pd.read_csv("dataset/" + path + "/output.csv", skipinitialspace=True, names=fields, sep='\t', skiprows=1)
            _df.name = path
            dataframes.append(_df)

    actual_data_path = "results/" + sys.argv[1] + "/output.csv"
    df_actual = pd.read_csv(actual_data_path, skipinitialspace=True, names=fields, sep='\t', skiprows=1)

    correlation_threshold = 0.7
    for df in dataframes:
        corref = np.corrcoef(df.intensity, df_actual.intensity)[0][1]
        if corref > correlation_threshold:
            print "{0}\t: {1}".format(df.name, corref)
