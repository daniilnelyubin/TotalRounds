import re
import requests
import datetime
from bs4 import BeautifulSoup
import dateutil.relativedelta
from python_utils import converters
import pandas as pd
import numpy as np
import time
import sys
import json
import time


class Parser(object):
    def __init__(self, start_date, end_date):
        self.start_date_ = start_date
        self.end_date_ = end_date

    def write_in_file(self, arr, func):
        file = open("data/" + func.__name__, 'w')

        if type(arr) is not dict:
            for i in arr:
                file.write(str(i) + "\n")
        else:
            for data in arr.items():
                file.write(str(data) + "\n")
        file.close()

    def read_from_file(self, func_result):
        file = open("data/" + func_result.__name__, 'r')
        return [line.strip() for line in file.readlines()]

    def write_to_json(self, dict, func):
        file = open("data/" + func.__name__, 'w')
        app_json = json.dumps(dict)
        file.write(app_json)
        file.close()

    def read_from_json(self, func):
        file = open("data/" + func.__name__, 'r')
        loaded_json = json.load(file)
        return loaded_json

    def get_random_hader(self):

        users_agent = [
            "Opera/9.60 (Windows NT 6.0; U; en) Presto/2.1.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0)",
            "Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
            "Chrome/51.0.2704.64 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"
        ]
        header = [
            "https://www.hltv.org/stats",
            "https://www.hltv.org/events",
            "https://www.hltv.org/results",
            "https://www.hltv.org/matches",
            "https://www.hltv.org/ranking/teams/2019/august/26",
            "https://www.hltv.org/ranking/teams/2019/august/26",
            "https://www.hltv.org/ranking/teams/2019/may/27",
            "https://www.hltv.org/ranking/teams/2019/february/25",
            "https://www.hltv.org/ranking/teams/2018/november/26",
            "https://www.hltv.org/ranking/teams/2018/august/27",
            "https://www.hltv.org/ranking/teams/2018/may/28"
        ]

        headers = {
            "referer": header[np.random.randint(0, len(header))],
            "user-agent": users_agent[np.random.randint(0, len(users_agent))]
        }
        return headers

    def get_parsed_page(self, url, params=""):

        response = requests.get("https://www.hltv.org" + url, headers=self.get_random_hader(), params=params)

        if response.status_code == 200:
            return BeautifulSoup(response.text, "lxml")
        else:
            counter = 1
            print("Error!")
            print("Response status code: " + str(response.status_code))
            print("Url: " + response.url)

            if not response.status_code == 404:
                print("Attempt to make request")
                time.sleep(np.random.randint(6, 15))
                response = requests.get("https://www.hltv.org" + url, headers=self.get_random_hader(), params=params)
                if response.status_code == 200:
                    print("---Success---")
                    return BeautifulSoup(response.text, "lxml")
            if response.status_code == 429 or response.status_code == 500:
                while not response.status_code == 200:
                    time.sleep(np.random.randint(15, 20))
                    response = requests.get("https://www.hltv.org" + url, headers=self.get_random_hader(),
                                            params=params)
                    print("Attempt to make request")
                print("---Success---")
                return BeautifulSoup(response.text, "lxml")

    def top_30_teams(self,link):
        page = self.get_parsed_page(link)
        teams = page.find("div", {"class": "ranking"})
        teamlist = list()
        for team in teams.find_all("div", {"class": "ranked-team standard-box"}):
            teamlist.append(team.find("a", {"class": "moreLink"})['href'])
        return teamlist

    def get_team_stat_link(self, team_page):
        stats_link = ""
        # time.sleep(np.random.randint(0,3))
        page = team_page
        a_tags = page.findAll("a", {"class": "moreButton"})
        for a in a_tags:
            if 'stats' in a.text.split():
                stats_link = a['href']

        return stats_link

    def get_team_match_link(self, stat_page):
        a_tags = stat_page.find("div", {"class": "gtSmartphone-only"})
        a_tags = a_tags.findAll("a")

        for a in a_tags:
            if len(re.findall('matches', a['href'])) > 0:
                return a['href']

    def get_team_matches_links_array(self, team_matches_page):
        td_tags = team_matches_page.findAll("td", {"class": "time"})
        last_class = ""
        list_of_matches = list()
        count = 0
        dic = dict()
        for td in td_tags:
            if td.parent['class'][0] == last_class:
                list_of_matches.append(td.find('a')['href'])
            else:
                dic[count] = list_of_matches
                count += 1
                list_of_matches = list()
                last_class = td.parent['class'][0]
                list_of_matches.append(td.find('a')['href'])
        return dic

    def get_match_data(self, page):
        map = page.find("div", {"class": "match-info-box"}).text.split("\n")[2]

        match_info_box = page.find("div", {"class": "match-info-box"})
        date = match_info_box.find("span").text.split()[0]

        results = match_info_box.findAll("div", {"class": "bold"})
        first_team_score = int(results[0].text)
        second_team_score = int(results[1].text)

        first_team_link = re.split(r"\?", match_info_box.findAll("a", {"class": "block text-ellipsis"})[1]['href'])[0]
        second_team_link = re.split(r"\?", match_info_box.findAll("a", {"class": "block text-ellipsis"})[2]['href'])[0]



        rounds = page.findAll("div",{"class":"round-history-team-row"})
        count = 0
        rounds_dict_ft = {}
        rounds_dict_st = {}
        for half in rounds[:1]:
            for img in half.findAll("img",{"class":"round-history-outcome"}):
                count+=1
                if not img['title']=="":
                    rounds_dict_ft[count] = 1
                    rounds_dict_st[count] = 0
                else:
                    rounds_dict_ft[count] = 0
                    rounds_dict_st[count] = 1
        # for half in rounds[1:]:
        #     print(1)

        team_name = re.split("/", first_team_link)[4]
        pick_link = page.find("a", {"class": "match-page-link button"})['href']
        ft_pick = self.get_pick(self.get_parsed_page(pick_link), map, team_name)

        dic = {
            "map": map,
            "date": date,
            "ft_pick": ft_pick,
            "ft_score": first_team_score,
            "st_score": second_team_score,
            "ft_link": first_team_link,
            "st_link": second_team_link

        }

        for key in rounds_dict_ft.keys():
            dic["ft_round_"+str(key)+"_win"] = rounds_dict_ft[key]
        return dic

    def get_team_stats(self, team_page, map_name):
        data_dic = {}
        # age = self.get_team_age(team_page)
        data = team_page.findAll("div", {"class": "col standard-box big-padding"})
        for div in data:
            key = div.find("div", {"class": "small-label-below"}).text
            data = div.find("div", {"class": "large-strong"}).text
            if not "draws" in key:
                data_dic[key] = float(data)
            else:
                split_string = data.split()
                data_dic["Win Rate"] = float(split_string[0]) / (float(split_string[4]) + float(split_string[0]))
        data_dic['age'] = 24
        maps_link = ""

        a_tags = team_page.find("div", {"class": "gtSmartphone-only"})
        a_tags = a_tags.findAll("a")

        for a in a_tags:
            if len(re.findall('maps', a['href'])) > 0:
                maps_link = a['href']
                break
        data_dic['maps'] = self.get_team_map_one_info(
            self.get_parsed_page(self.get_team_one_map_href(self.get_parsed_page(maps_link), map_name)))

        data_dic['players'] = self.get_team_players_info(team_page)

        return data_dic

    def get_team_age(self,team_page):
        a_tags = team_page.findAll("a",{"class":"button"})
        for a in a_tags:
            if len(re.findall("team",a['href']))>0:
                team_profile = self.get_parsed_page(a['href'])
                divs = team_profile.findAll("div",{"class":"profile-team-stat"})
                for div in divs:
                    if len(re.findall("age",div.text))>0:
                        span = div.find("span")
                        return span.text

    def get_team_maps_info(self, maps_page):
        maps = maps_page.findAll("div", {"class": "tabs standard-box"})[1].findAll("div")
        map_dic = dict()
        for map in maps:
            a = map.find("a")
            map_href = a['href']
            time.sleep(1)
            map_dic[a.text] = self.get_team_map_one_info(self.get_parsed_page(map_href))
        return map_dic

    def get_team_map_one_info(self, map_page):
        spans = map_page.findAll("span", {"class": "strong"})
        map_info_dic = dict()
        for span in spans:
            name = span.text
            data = span.next_sibling.text
            if not "draws" in name:
                map_info_dic[name] = float(re.split("%", data)[0])
        return map_info_dic

    def get_team_one_map_href(self, maps_page, map_name=""):
        maps = maps_page.findAll("div", {"class": "tabs standard-box"})[1].findAll("div")
        map_dic = dict()
        for map in maps:
            a = map.find("a")
            map_href = a['href']
            if a.text == map_name:
                return map_href

    def get_team_players_info(self, team_page):
        divs = team_page.findAll("div", {"class": "col teammate"})
        list_of_players = list()
        for idx, div in enumerate(divs):
            if idx < 5:
                tag_a = div.find("a", {"class": "image-and-label"})
                player_link = tag_a['href']
                list_of_players.append(self.get_player_info(self.get_parsed_page(player_link)))
        avrg_players_stat = self.get_avrg_team_stats(list_of_players)
        avrg_players_stat['players_in_team'] = len(list_of_players)
        return avrg_players_stat

    def get_player_info(self, player_page):
        divs = player_page.findAll("div", {"class": "stats-row"})
        dic = dict()
        # dic['name'] = re.split("\'", player_page.find("h1", {"class": "statsPlayerName"}).text)[1]
        # dic['team'] = player_page.find("a", {"class": "large-strong text-ellipsis"})['href']
        colors_name = player_page.findAll("div", {"class": "summaryStatBreakdownSubHeader"})
        colors_data = player_page.findAll("div", {"class": "summaryStatBreakdownDataValue"})
        list_of_name = list()

        for i in colors_name:
            list_of_name.append(i.find("b").text)

        for idx, value in enumerate(colors_data):
            if idx > 1:
                if value.text=="-":
                    dic[list_of_name[idx]] = float(0)
                else:
                    dic[list_of_name[idx]] = float(re.split("%", value.text)[0])

        for div in divs:
            spans = div.findAll("span")
            dic[spans[0].text] = float(re.split("%", spans[1].text)[0])

        dic_ind = self.get_individual_player_info(player_page)

        for key in dic_ind:
            dic[key] = dic_ind[key]


        return dic

    def get_individual_player_info(self, player_page):
        dic = {}
        div = player_page.find('div', {"class": "tabs standard-box"})
        a_tags = div.findAll("a")
        individual_link = ""
        for a in a_tags:
            if len(re.findall('individual', a['href'])) > 0:
                individual_link = a['href']

        ind_page = self.get_parsed_page(individual_link)
        stats_rows = ind_page.findAll("div", {"class": "stats-row"})
        for idx, row in enumerate(stats_rows):
            if idx > 5:
                spans = row.findAll("span")
                dic[spans[0].text] = float(re.split("%", spans[1].text)[0])
        return dic

    def get_avrg_team_stats(self, arr):
        avrg_dic = dict()
        for idx, dic in enumerate(arr):
            for key in dic.keys():
                key_ = key
                if key_=="Rating 1.0":
                    key_ = "Rating 2.0"
                if idx == 0:
                    avrg_dic[key_] = dic[key]
                else:
                    avrg_dic[key_] += dic[key]
        count = len(arr)
        for key in avrg_dic.keys():
            avrg_dic[key] /= count
        return avrg_dic

    def get_date_minus_n_days(self, days, date):
        return date.date() - dateutil.relativedelta.relativedelta(days=days)

    def get_match_data_for_prediction(self, page):

        match_info_box = page.findAll("div", {"class": "team"})
        # date = match_info_box.find("span").text.split()[0]

        first_team_link = match_info_box[0].find("a")['href']
        first_team_link = self.get_team_stat_link(self.get_parsed_page(first_team_link))

        second_team_link = match_info_box[1].find("a")['href']
        second_team_link = self.get_team_stat_link(self.get_parsed_page(second_team_link))
        dic = {
            "ft_link": first_team_link,
            "st_link": second_team_link
        }
        return dic
    def get_pick(self,page,map,team_name):
        boxes = page.findAll("div",{"class":"standard-box veto-box"})
        if len(boxes)>1:
            pick_box = boxes[1]
            pick_divs = pick_box.find("div").findAll("div")
            for div in pick_divs:
                if map in div.text and team_name in div.text:
                    return 1
            return 0
        return -1