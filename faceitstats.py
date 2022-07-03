import json
import requests
from tqdm import tqdm


class Stats:
    def __init__(self, api_key, player):
        self.api_key = ""
        self.player = player
        self.player_id = None
        self.player_stats = None
        self.match_data = None

    def get_player_id(self):
        headers = {'Authorization': f'Bearer {self.api_key}',
                   'accept': 'application/json'}
        url = f'https://open.faceit.com/data/v4/players?nickname={self.player}'
        json_url = requests.get(url, headers=headers)
        data = json.loads(json_url.text)
        try:
            data = data["player_id"]
        except:
            data = None
            print(f'Cannot find id of {self.player}')
        self.player_id = data
        return data

    def get_players_stats(self):
        headers = {'Authorization': f'Bearer {self.api_key}',
                   'accept': 'application/json'}
        url = f'https://open.faceit.com/data/v4/players/{self.player_id}/stats/csgo'

        json_url = requests.get(url, headers=headers)
        data = json.loads(json_url.text)
        try:
            data = data["lifetime"]
        except:
            data = None
            print(f'Cannot find stats of {self.player}')
        self.player_stats = data
        return data

    def get_all_match_stats(self):
        player_matches = self.get_all_matches()
        print('Found total of ', len(player_matches), ' matches.')
        limit = 0
        while limit < 10:
            for match_id in tqdm(player_matches):
                limit += 1
                data = self.get_single_match_stats(match_id)
                data['Team'] = self.get_match_teammates(match_id)
                player_matches[match_id].update(data)
            self.match_data = player_matches
        return player_matches

    def get_single_match_stats(self, match_id):
        headers = {'Authorization': f'Bearer {self.api_key}',
                   'accept': 'application/json'}
        url = f'https://open.faceit.com/data/v4/matches/{match_id}/stats'
        json_url = requests.get(url, headers=headers)
        data = json.loads(json_url.text)

        try:
            map = data['rounds'][0]["round_stats"]["Map"]
            rounds = data['rounds'][0]["round_stats"]["Rounds"]
            data = data['rounds'][0]['teams'][0]
            filtered = [el for el in data['players']
                        if f'{self.player}' in el['nickname']]
            stats = filtered[0]['player_stats']
            stats['Map'] = map
            stats['Rounds'] = rounds
        except:
            data = json.loads(json_url.text)
            try:
                map = data['rounds'][0]["round_stats"]["Map"]
                rounds = data['rounds'][0]["round_stats"]["Rounds"]
                data = data['rounds'][0]['teams'][1]
                filtered = [el for el in data['players']
                            if f'{self.player}' in el['nickname']]
                stats = filtered[0]['player_stats']
                stats['Map'] = map
                stats['Rounds'] = rounds
            except:
                print(
                    f"Error getting {self.player}'s stats from match {match_id}")
                stats = dict()
        return dict(sorted(stats.items(), key=lambda x: x[0].lower()))

    def get_match_teammates(self, match_id):
        mates = []
        headers = {'Authorization': f'Bearer {self.api_key}',
                   'accept': 'application/json'}
        url = f'https://open.faceit.com/data/v4/matches/{match_id}/stats'
        json_url = requests.get(url, headers=headers)
        data = json.loads(json_url.text)
        try:
            for mate in data['rounds'][0]['teams'][0]['players']:
                mates.append(mate['nickname'])
            if self.player not in mates:
                mates.clear()
                for mate in data['rounds'][0]['teams'][1]['players']:
                    mates.append(mate['nickname'])
        except:
            print(
                f"Error getting {self.player}'s teammates from match {match_id}")
        return mates

    def get_all_matches(self):
        offset = 0
        limit = 100
        index = 0
        url = f'https://open.faceit.com/data/v4/players/{self.player_id}/history?game=csgo&offset={offset}&limit={limit}'
        match = self.get_matches_per_page(url)
        try:
            while (limit is not None and index < 15):
                nextUrl = f'https://open.faceit.com/data/v4/players/{self.player_id}/history?game=csgo&offset={offset}&limit={limit}'
                next_match = self.get_matches_per_page(nextUrl)
                match.update(next_match)
                offset += 100
                index += 1
        except:
            print(f"Error getting all stats from {self.player}")
        return match

    def get_matches_per_page(self, url):
        headers = {'Authorization': f'Bearer {self.api_key}',
                   'content-type': 'application/json', 'cache-control': 'max-age=10', 'charset': 'utf-8'}
        json_url = requests.get(url, headers=headers)
        data = json.loads(json_url.text)
        player_matches = dict()

        if "items" not in data:
            return player_matches, None
        item_data = data["items"]
        for item in item_data:
            try:
                match_id = item["match_id"]
                player_matches[match_id] = dict()
            except KeyError:
                print("Error getting all matches from page")
        return player_matches

    def dump(self):
        if self.player_stats is None or self.match_data is None:
            print("No data found")
            return
        fused_data = {self.player_id: {
            "player_stats": self.player_stats, "match_data": [self.match_data]}}
        player = self.player
        file_name = "stats_" + player + '.json'
        with open(file_name, 'w') as f:
            json.dump(fused_data, f, indent=4)
        print(f"Dumped all stats from player {self.player}")
