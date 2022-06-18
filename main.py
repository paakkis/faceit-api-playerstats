from faceitstats import Stats

API_KEY = "8ebb08a2-8fb4-4daf-b90f-68ff7876ccf2"
player = "myy"

faceitmyy = Stats(API_KEY, player)
faceitmyy.get_player_id()
faceitmyy.get_players_stats()
faceitmyy.get_all_match_stats()
faceitmyy.dump()
