import pandas as pd
import numpy as np
import os, sys
from collections import Counter

DEBUG = False

def calculate_between_dataset(data_name, correlation_threshold=0.7, debug=False):
    fields = ['count', 'wavelength', 'intensity']
    dataframes = []

    # Load Dataset
    for path in os.listdir("dataset/"):
        if path != ".DS_Store":
            _df = pd.read_csv("dataset/" + path + "/output.csv", skipinitialspace=True, names=fields, sep='\t', skiprows=1)
            _df.name = path
            dataframes.append(_df)

    # Load Actual Data
    actual_data_path = "results/" + data_name + "/output.csv"
    # Read Actual Data
    df_actual = pd.read_csv(actual_data_path, skipinitialspace=True, names=fields, sep='\t', skiprows=1)

    if debug:
        print "Dataset : Correlation Coefficient"

    found_max = -1
    result_string = []
    for df in dataframes:
        corref = np.corrcoef(df.intensity, df_actual.intensity)[0][1]
        if corref > correlation_threshold:
            if corref > found_max:
                found_max = corref
            if df.name != data_name:
                result_string.append("{0} : {1}".format(df.name, corref))

    result_string = sorted(result_string, cmp=None, key=lambda x: x.split(" : ")[1], reverse=True)
    return result_string

def closest_match(input_string):
    name_dict = { }
    for line in input_string:
        name = line.split(" : ")[0].split("_")[0]
        if not name in name_dict.keys():
            name_dict[name] = 1
        else:
            name_dict[name] = name_dict[name] + 1
    return max(name_dict, key=name_dict.get)

if DEBUG:
    dataframes = []
    fields = ['count', 'wavelength', 'intensity']
    df = pd.read_csv('dataset/utah3_4/output.csv', skipinitialspace=True, names=fields, sep='\t', skiprows=1)
    df2 = pd.read_csv('dataset/utah3_1/output.csv', skipinitialspace=True, names=fields, sep='\t', skiprows=1)
    print np.corrcoef(df.intensity, df2.intensity)[0][1]

result = calculate_between_dataset(sys.argv[1], correlation_threshold=0.6, debug=True)
for line in result:
    print line

print closest_match(result)
