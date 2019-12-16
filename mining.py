import numpy as np
import pandas as pd
import seaborn as sns
from sklearn import preprocessing
import sys
import re
import warnings

warnings.simplefilter(action='ignore', category=Warning)

def clear_all_data(file_path):
# def get_team_id(team_link):
#     return re.split("/", team_link)[3]

    df = pd.read_csv(file_path)
    # df = pd.read_csv("data/data.csv")
    df.rename(columns={"match_id": "ids"}, inplace=True)

    df_all = df[df['isBoOne'] == 1]

    counter = 0
    df_all.head()
    # for idx, i in enumerate(df_all.index):
    #     first_team_id = get_team_id(df_all.iloc[idx]['first_team_link'])
    #     second_team_id = get_team_id(df_all.iloc[idx]['second_team_link'])
    #     if (df_all.iloc[idx]['match_num'] - df_all.iloc[idx - 1]['match_num']) == 1 and (
    #             first_team_id == last_first_team) and (second_team_id == last_second_team):
    #
    #         df_all.at[i, 'best_of_3_id'] = counter
    #
    #         if df_all.iloc[idx - 1]['first_team_score'] > df_all.iloc[idx - 1]['second_team_score']:
    #             df_all.at[i, 'ft_win_last_map'] = 1
    #         else:
    #             df_all.at[i, 'st_win_last_map'] = 1
    #
    #         df_all.at[i, 'ft_prev_map_score'] = df_all.iloc[idx - 1]['first_team_score']
    #         df_all.at[i, 'st_prev_map_score'] = df_all.iloc[idx - 1]['second_team_score']
    #
    #     else:
    #         counter += 1
    #         df_all.at[i, 'best_of_3_id'] = counter
    #         # print(df_all.iloc[i]['map'])
    #
    #         last_first_team = get_team_id(df_all.iloc[idx]['first_team_link'])
    #         last_second_team = get_team_id(df_all.iloc[idx]['second_team_link'])

    # df_all.head(15)

    # df_all.drop("first_team_link",axis=1,inplace=True)
    # df_all.drop("second_team_link",axis=1,inplace=True)


    # df_all = df_all.groupby("best_of_3_id").filter(lambda x: len(x) > 1)
    # df_all = df_all.groupby("best_of_3_id").filter(lambda x: len(x) < 4)
    # df_all = df_all.groupby("best_of_3_id").filter(lambda x: x['match_num'].sum() == 6 or x['match_num'].sum() == 3)


    df_all.drop("date", axis=1, inplace=True)
    df_all.drop("ft_link", axis=1, inplace=True)
    df_all.drop("st_link", axis=1, inplace=True)

    le = preprocessing.LabelEncoder()

    maps = le.fit_transform(df_all['map'])

    maps = np.reshape(maps, (maps.shape[0], 1))

    df_all['map'] = maps

    df_all['ft_age'].fillna(df_all.ft_age.mean(), inplace=True)
    df_all['st_age'].fillna(df_all.st_age.mean(), inplace=True)

    df_all = df_all[df_all.columns.drop(list(df_all.filter(regex='ft_round')))]

    file_name = "data/clear_bo1_file.csv"
    df_all.to_csv(file_name, index_label="id")
    print("=========================")
    print("Data has been processed.")
    print("=========================")
    return file_name
