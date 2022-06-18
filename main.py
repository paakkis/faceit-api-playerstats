from faceitstats import Stats

API_KEY = ""
player = "myy"

faceit = Stats(API_KEY, player)
faceit.get_player_id()
faceit.get_players_stats()
faceit.get_all_match_stats()
faceit.dump()
