import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, make_scorer, explained_variance_score, mean_squared_error
import numpy as np
import xgboost as xgb
import pickle
from mining import *
import sys
import os

data_file = ""


if __name__ == "__main__":
    arguments = sys.argv[1:]
    for idx, value in enumerate(arguments):
        if idx % 2 == 0:
            if value == "-d":
                data_file = arguments[idx + 1]
            else:
                print("No file in ./data/")
                sys.exit()
    if data_file == "":
        print("No file in ./data/")
        sys.exit()
    file_name = clear_all_data("data/" + data_file)

    df_ = pd.read_csv(file_name)

    df_.drop(
        ["id"],
        axis=1, inplace=True)

    df = df_[(df_.ft_score + df_.st_score) < 31]
    y_wot = (df.ft_score + df.st_score).to_numpy()
    X_wot = df.drop(["ft_score", 'st_score'], axis=1).to_numpy()
    df = df_
    y = (df.ft_score + df.st_score).to_numpy()
    X = df.drop(["ft_score", 'st_score'], axis=1).to_numpy()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)
    X_train_wot, X_test_wot, y_train_wot, y_test_wot = train_test_split(X_wot, y_wot, test_size=0.3, random_state=1)
    mean_dic = {}
    # Overtime
    boost_ot = xgb.XGBRegressor(learning_rate=0.4, n_estimators=50, max_depth=11)

    # Without overtime
    boost_wot = xgb.XGBRegressor(learning_rate=0.5, n_estimators=20, max_depth=8)

    # # Boost Linear
    # boost_linear = xgb.XGBRegressor(learning_rate=0.6, n_estimators=70, max_depth=5,booster="gblinear")

    # boost = xgb.XGBRegressor(booster="gblinear")

    # parametrs = {
    #     "learning_rate": [0.3, 0.05, 0.1, 0.4, 0.5, 0.6],
    #     "max_depth": [5, 6, 7, 8, 9, 10, 11, 12],
    #     "n_estimators": [20, 30, 40, 50, 60, 70, 80]
    # }
    #
    # gs = GridSearchCV(boost,param_grid=parametrs,n_jobs=-1,scoring=make_scorer(mean_squared_error,greater_is_better=False),cv=3)
    # gs.fit(X_train,y_train)


    boost_wot.fit(X_train_wot, y_train_wot)
    boost_ot.fit(X_train,y_train)
    # predicted = (boost_ot.predict(X_test) + boost_wot.predict(X_test)) / 2

    predicted_wot = boost_wot.predict(X_test_wot)
    predicted_ot = boost_ot.predict(X_test)




    print("Boost wo overtime result:", np.sqrt(mean_squared_error(predicted_wot, y_test_wot)))

    print("Boost overtime result:", np.sqrt(mean_squared_error(predicted_ot, y_test)))

    try:
        os.mkdir("models")
    except FileExistsError:
        a = 1

    # pickle.dump(boost_ot, open("models/xgb_overtime.pickle.dat", "wb"))
    # pickle.dump(boost_wot, open("models/xgb_best.pickle.dat", "wb"))

