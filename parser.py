import datetime
import dateutil.relativedelta
from HltvParser import Parser
import csv
import re


def write_to_csv(dic, first_time):
    with open("data.csv", "a") as f:
        w = csv.DictWriter(f, dic.keys())
        if first_time:
            w.writeheader()
        w.writerow(dic)


def minus_days(days, today):
    return today - dateutil.relativedelta.relativedelta(days=days)


def write_id(id):
    with open("ids", "a") as f:
        f.write(id + "\n")


def write_logs(log):
    with open("logs", "a") as f:
        f.write(log + "\n")


def load_ids(dic):
    with open("ids", "r") as f:
        for line in f.readlines():
            dic[line.strip()] = 1
    return dic


def get_match_id(link):
    split_match = re.split("/", link)
    match_id = split_match[4]
    return match_id


def rework_dict(match_data, team_dic, prefix):
    for key in team_dic.keys():
        if key == "maps":
            for key_mp in team_dic[key].keys():
                match_data[prefix + "_mp_" + key_mp] = team_dic[key][key_mp]
        elif key == "players":
            for key_p in team_dic[key].keys():
                match_data[prefix + "_pl_" + key_p] = team_dic[key][key_p]
        else:
            match_data[prefix + "_" + key] = team_dic[key]
    return match_data


today = datetime.date.today()
today_minus_three_months = today - dateutil.relativedelta.relativedelta(months=3)
end_date = minus_days(1, datetime.datetime.strptime("2018-11-26", "%Y-%m-%d"))
start_date = minus_days(90, end_date).strftime('%Y-%m-%d')

parser = Parser(start_date, end_date)

params_for_match = {
    "startDate": start_date,
    "endDate": end_date.strftime('%Y-%m-%d'),
}

count_of_err = 0
first_time = False

arr_of_top_30_links = [
    # "/ranking/teams/2019/august/26",
    # "/ranking/teams/2019/may/27",
    # "/ranking/teams/2019/february/25",
    # "/ranking/teams/2018/november/26",
    # "/ranking/teams/2018/august/27",
    "/ranking/teams/2018/may/28"]

for link_of_top in arr_of_top_30_links:
    arr_of_teams = parser.top_30_teams(link_of_top)

    dict_of_matches = dict()
    dict_of_matches = load_ids(dict_of_matches)
    for team in arr_of_teams:

        stat_links = parser.get_team_stat_link(parser.get_parsed_page(team))

        match_link = parser.get_team_match_link(parser.get_parsed_page(stat_links))

        matches = parser.get_team_matches_links_array(parser.get_parsed_page(match_link, params=params_for_match))

        # params_for_match['matchType'] = "Lan"
        # matches_lan = parser.get_team_matches_links_array(parser.get_parsed_page(match_link,params=params_for_match))
        #
        # params_for_match['matchType'] = "Online"
        # matches_online = parser.get_team_matches_links_array(parser.get_parsed_page(match_link,params=params_for_match))
        #
        # params_for_match['matchType'] = "BigEvents"
        # matches_big_events = parser.get_team_matches_links_array(parser.get_parsed_page(match_link,params=params_for_match))
        #
        # dic_of_lans = dict()
        # for key_m in matches_lan.keys():
        #     for lan in matches_lan[key_m]:
        #         dic_of_lans[get_match_id(lan)] = 1
        #
        # dic_of_online = dict()
        # for key_m in matches_online.keys():
        #     for online in matches_online[key_m]:
        #         dic_of_online[get_match_id(online)] = 1
        #
        # dic_of_big_events = dict()
        # for key_m in matches_big_events.keys():
        #     for event in matches_big_events[key_m]:
        #         dic_of_big_events[get_match_id(event)] = 1
        #
        #
        # with open("type_of_match.csv","a") as f:
        #     f.write("ids,lan,online,big_event\n")
        #     for key_m in matches.keys():
        #         for event in matches[key_m]:
        #             id = get_match_id(event)
        #             if id in dict_of_matches:
        #                 continue
        #             f.write(get_match_id(event))
        #             if id in dic_of_lans:
        #                 f.write(","+"1")
        #             else: f.write(","+"0")
        #
        #             if id in dic_of_online:
        #                 f.write("," + "1")
        #             else: f.write("," + "0")
        #
        #             if id in dic_of_big_events:
        #                 f.write("," + "1\n")
        #             else: f.write("," + "0\n")

        # parser.write_to_json(matches, parser.get_team_matches_links_array)

        for key_m in reversed(sorted(matches.keys())):
            count = 1
            for match in matches[key_m][::-1]:

                split_match = re.split("/", match)
                match_id = split_match[4]
                if match_id in dict_of_matches:
                    print('Next match')
                    write_logs("Next match")
                    continue
                else:
                    dict_of_matches[match_id] = 1
                    write_id(match_id)
                    print(match_id + "/" + split_match[5])
                    write_logs(match_id + "/" + split_match[5])
                try:
                    if len(matches[key_m][::-1]) > 1:
                        isBoOne = 0
                    else:
                        isBoOne = 1
                    # match = "/stats/matches/mapstatsid/87937/vitality-vs-gamerlegion?startDate=2019-05-28&endDate=2019-08-26&contextIds=9565&contextTypes=team"
                    match_data = parser.get_match_data(parser.get_parsed_page(match))
                    match_data['match_id'] = match_id
                    match_data['isBoOne'] = isBoOne
                    match_data['match_num'] = count

                    params = {
                        "startDate": parser.get_date_minus_n_days(90, datetime.datetime.strptime(match_data["date"],
                                                                                                 "%Y-%m-%d")),
                        "endDate": parser.get_date_minus_n_days(1,
                                                                datetime.datetime.strptime(match_data["date"],
                                                                                           "%Y-%m-%d"))
                    }

                    first_team_dic = parser.get_team_stats(
                        parser.get_parsed_page(match_data['ft_link'], params=params), match_data['map'])
                    second_team_dic = parser.get_team_stats(
                        parser.get_parsed_page(match_data['st_link'], params=params), match_data['map'])

                    match_data = rework_dict(match_data, first_team_dic, "ft")
                    match_data = rework_dict(match_data, second_team_dic, "st")

                    count += 1

                    write_to_csv(match_data, first_time)
                    first_time = False

                except Exception as e:
                    with open("errors", "a") as f:
                        count_of_err += 1
                        print("-----Error " + str(count_of_err) + " in match-----")
                        f.write("Error " + str(count_of_err) + " " + match + "\n")
                        f.write(str(e) + "\n")

    params_for_match['endDate'] = params_for_match['startDate']
    params_for_match['startDate'] = minus_days(90, datetime.datetime.strptime(params_for_match['endDate'],
                                                                              "%Y-%m-%d")).strftime('%Y-%m-%d')
    print("---------------------Next epoch---------------------")
    write_logs("---------------------Next epoch---------------------")
