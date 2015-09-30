from collections import defaultdict
import signal   # signal-related #@$#
import sys      # ditto


from bottle import run, Bottle, request, response
app = Bottle()

from db import sql, sql_value

## Signal Handler
def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

NUM_DAYS = 1

ALL_PLAYERS_STATS = """
SELECT *
FROM Player;
"""

KILL_STATS_OVER_DAYS = """
SELECT
  attacker, COUNT(*) AS kills,
  SUM(dominated) AS dominations,
  SUM(revenge) AS revenges
FROM killlog
WHERE FROM_UNIXTIME(killtime) >= NOW() - INTERVAL %s DAY
GROUP BY attacker
"""

DEATH_STATS_OVER_DAYS = """
SELECT
  victim, COUNT(*) AS deaths,
  SUM(dominated) AS dominated
FROM killlog
WHERE FROM_UNIXTIME(killtime) >= NOW() - INTERVAL %s DAY
GROUP BY victim
"""

PLAYER_KILL_STATS_OVER_DAYS = """
SELECT SUM(CASE when attacker=%s then 1 else 0 end) as kills,
       SUM(CASE when victim=%s then 1 else 0 end) as deaths,
       SUM(CASE when assister=%s then 1 else 0 end) as assists,
       SUM(CASE when attacker=%s AND dominated=1 then 1 else 0 end) as dominations,
       SUM(CASE when attacker=%s AND revenge=1 then 1 else 0 end) as revenges
FROM killlog
WHERE FROM_UNIXTIME(killtime) >= NOW() - INTERVAL 18 HOUR
"""


ROUTES = {
  'stats-over-days':    r'/v1/stats-over-days/<days:float>',
  'all-players-stats':  r'/v1/players',
  'player-stat':        r'/v1/player/<steamid>',
  'root':               r'/',
}


@app.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@app.route(ROUTES['root'])
def root():
    return {"routes": ROUTES}


@app.route(ROUTES['all-players-stats'])
def all_player_stats():
    players = sql(ALL_PLAYERS_STATS)
    return {"results": players}


@app.route(ROUTES['stats-over-days'])
def stats_over(days):
    if days < 1:
        return {"GT": "FO"}

    kill_stats = sql(KILL_STATS_OVER_DAYS, days)
    death_stats = sql(DEATH_STATS_OVER_DAYS, days)
    stats_by_steam_id = defaultdict(dict)

    for stat in kill_stats:
        player = stat['attacker']
        stats_by_steam_id[player].update(stat)
        del stats_by_steam_id[player]['attacker']

    for stat in death_stats:
        player = stat['victim']
        stats_by_steam_id[player].update(stat)
        del stats_by_steam_id[player]['victim']
    return stats_by_steam_id

@app.route(ROUTES['player-stat'])
def player_stats(steamid):
    player_stats = sql(PLAYER_KILL_STATS_OVER_DAYS, (steamid, steamid, steamid, steamid, steamid))
    
    resp = player_stats[0]
    for k, v in resp.items():
        if v == None:
            resp[k] = 0

    return resp


if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8000, debug=True)
