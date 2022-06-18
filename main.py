from faceitstats import Stats

API_KEY = ""
player = "myy"

faceitmyy = Stats(API_KEY, player)
faceitmyy.get_player_id()
faceitmyy.get_players_stats()
faceitmyy.get_all_match_stats()
faceitmyy.dump()
