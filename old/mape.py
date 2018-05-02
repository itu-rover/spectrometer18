import os
import sys
import numpy as np
import pandas as pd
#from sklearn.utils import check_arrays

def mean_absolute_percentage_error(y_true, y_pred):
    # y_true, y_pred = check_arrays(y_true, y_pred)

    ## Note: does not handle mix 1d representation
    #if _is_1d(y_true):
    #    y_true, y_pred = _check_1d_array(y_true, y_pred)

    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
def _mean_absolute_percentage_error(y_true, y_pred):
    sum_error = 0
    for i in range(len(y_true)):
        sum_error += np.abs((y_true[i] - y_pred[i]) / y_true[i])
    return sum_error * 100 / len(y_true)

fields = ['count', 'wavelength', 'intensity']
_DEBUG = 1

dataframes = []

if _DEBUG == 1:
    df = pd.read_csv('dataset/utah3_4/output.csv', skipinitialspace=True, names=fields, sep='\t', skiprows=1)
    df2 = pd.read_csv('dataset/utah3_1/output.csv', skipinitialspace=True, names=fields, sep='\t', skiprows=1)
    mean_compared = np.mean(df.intensity)
    mean_actual = np.mean(df2.intensity)
    df1_real = []
    df2_real = []
    for i in range(len(df.intensity)):
        if (df.intensity[i] != 0) and (df2.intensity[i] != 0):
            df1_real.append(df.intensity[i])
            df2_real.append(df2.intensity[i])
    compared_dataframe = []
    for i in range(len(df1_real)):
        compared_dataframe.append(df1_real[i] * ( mean_compared / mean_actual))
        print df2_real[i], df1_real[i] * (mean_actual / mean_compared)
    print _mean_absolute_percentage_error(compared_dataframe, df2_real)
else:
    # Load Dataset
    for path in os.listdir("dataset/"):
        if path != ".DS_Store":
            _df = pd.read_csv("dataset/" + path + "/output.csv", skipinitialspace=True, names=fields, sep='\t', skiprows=1)
            _df.name = path
            dataframes.append(_df)

    actual_data_path = "results/" + sys.argv[1] + "/output.csv"
    df_actual = pd.read_csv(actual_data_path, skipinitialspace=True, names=fields, sep='\t', skiprows=1)
    mape_threshold = 0.7
    for df in dataframes:
        mape_val = mean_absolute_percentage_error(df.intensity, df_actual.intensity)
        if mape_val > mape_threshold:
            print "{0}\t: {1}".format(df.name, mape_val)
