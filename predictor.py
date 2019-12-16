import datetime
import dateutil.relativedelta
from HltvParser import Parser
import csv
import re
from os import walk
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
import xgboost as xgb
import pickle
import os.path
import sys


def clear_data_in_dict(data):
    del data["ft_link"]
    del data["st_link"]
    del data["date"]
    del data["ft_age"]
    del data["st_age"]
    del data["ft_pl_players_in_team"]
    del data["st_pl_players_in_team"]
    return data


def write_to_csv(dic, first_time, file_name):
    with open("data/" + file_name + ".csv", "a") as f:
        w = csv.DictWriter(f, dic.keys())
        if first_time:
            w.writeheader()
        w.writerow(dic)


def clear_existing_data():
    mypath = "data/"

    for (dirpath, dirnames, filenames) in walk(mypath):
        for file in filenames:
            if not re.search(r"vs", file) is None:
                try:
                    df = pd.read_csv(mypath + file)
                    df = clear_data_frame(df)
                    df.to_csv(mypath + file, index=False)
                    print(file)
                except Exception as e:
                    continue


def get_data_for_prediction(match_url, map, days):
    if os.path.exists("data/" + re.split("/", match_url)[3] + "-" + map + ".csv"):
        return

    match_url = match_url
    parser = Parser("0", "0")
    first_time = True
    count_of_err = 0

    match_data = parser.get_match_data_for_prediction(parser.get_parsed_page(match_url))
    match_data['date'] = datetime.date.today()
    today_minus_three_months = match_data['date'] - dateutil.relativedelta.relativedelta(days=days)
    params = {
        "startDate": today_minus_three_months,
        "endDate": match_data['date']
    }

    first_team_dic = parser.get_team_stats(
        parser.get_parsed_page(match_data['ft_link'], params=params), map)
    second_team_dic = parser.get_team_stats(
        parser.get_parsed_page(match_data['st_link'], params=params), map)
    for key in first_team_dic.keys():
        if key == "maps":
            for key_mp in first_team_dic[key].keys():
                match_data["ft_mp_" + key_mp] = first_team_dic[key][key_mp]
        elif key == "players":
            for key_p in first_team_dic[key].keys():
                match_data["ft_pl_" + key_p] = first_team_dic[key][key_p]
        else:
            match_data["ft_" + key] = first_team_dic[key]
    for key in second_team_dic.keys():
        if key == "maps":
            for key_mp in second_team_dic[key].keys():
                match_data["st_mp_" + key_mp] = second_team_dic[key][key_mp]
        elif key == "players":
            for key_p in second_team_dic[key].keys():
                match_data["st_pl_" + key_p] = second_team_dic[key][key_p]
        else:
            match_data["st_" + key] = second_team_dic[key]

    match_data = clear_data_in_dict(match_data)

    write_to_csv(match_data, first_time, re.split("/", match_url)[3] + "-" + map)
    first_time = False


def clear_data_frame(data_frame):
    return data_frame.drop(
        ["ft_link", "st_link", "date", "ft_age", "st_age", "ft_pl_players_in_team",
         "st_pl_players_in_team"],
        axis=1)


# matches = {
#     "/matches/2335621/mibr-vs-nip-starladder-major-2019" : "Inferno",
#     # "/matches/2335621/mibr-vs-nip-starladder-major-2019":"Mirage"
# }

boost_ot = pickle.load(open("models/xgb_overtime.pickle.dat", "rb"))
boost_wot = pickle.load(open("models/xgb_best.pickle.dat", "rb"))


map = "Inferno"
link = ""
days = 90

if __name__ == "__main__":
    arguments = sys.argv[1:]
    for idx, value in enumerate(arguments):
        if idx % 2 == 0:
            if value == "-m":
                map = arguments[idx + 1]
            if value == "-l":
                link = arguments[idx + 1]
                link = re.split(r".org" ,link)[-1]
            if value == "-t":
                days = arguments[idx + 1]

    if link == "":
        print("No link")
        sys.exit()
    
    if (map != "Inferno") and (map != "Dust2") and (map != "Nuke") and (map != "Overpass") and (
            map != "Train") and (map != "Mirage") and (map != "Vertigo"):
        print("Wrong map")
        sys.exit()

    boost_ot = pickle.load(open("models/xgb_overtime.pickle.dat", "rb"))
    boost_wot = pickle.load(open("models/xgb_best.pickle.dat", "rb"))

    matches = {link: map}

    for url in matches.keys():
        map = matches[url]
        get_data_for_prediction(url, map, days=days)
        data_df = pd.read_csv("data/" + re.split("/", url)[3] + "-" + map + ".csv")
        # data_df = clear_data_frame(data_df)
        X = data_df.to_numpy()
        print(url)
        print("Overtime model: " + str(boost_ot.predict(X)[0]))
        print("WO Overtime model: " + str(boost_wot.predict(X)[0]))
        print("Average: " + str((boost_ot.predict(X) + boost_wot.predict(X))[0] / 2))
