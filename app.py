import signal # signal-related #@$#
import sys

import json

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

DAILY_KILL_COUNT = """
	SELECT COUNT(*) AS value
	FROM   killlog
	WHERE  FROM_UNIXTIME(killtime) >= NOW() - INTERVAL 1 DAY
	AND    attacker = %s
"""

DAILY_DEATH_COUNT = """
	SELECT COUNT(*) AS value
	FROM   killlog
	WHERE  FROM_UNIXTIME(killtime) >= NOW() - INTERVAL 1 DAY
	AND    victim = %s
"""

DAILY_DOMINATIONS_COUNT = """
	SELECT SUM(dominated) AS value
	FROM   killlog
	WHERE  FROM_UNIXTIME(killtime) >= NOW() - INTERVAL 1 DAY
	AND    attacker = %s
"""

DAILY_REVENGES_COUNT = """
	SELECT SUM(revenge) AS value
	FROM   killlog
	WHERE  FROM_UNIXTIME(killtime) >= NOW() - INTERVAL 1 DAY
	AND    attacker = %s
"""


ROUTES = {
  'daily-kills':        r'/player/<steamId>/daily-kills',
  'all-players-stats':  r'/players',
  'player-stat':        r'/player/<steamId>',
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


@app.route(ROUTES['player-stat'])
def player_stats(steamId):
    print("steamId:", steamId)
    player = sql("SELECT * FROM Player WHERE steamId = %s", steamId)[0]
    return {"result": player}


@app.route(ROUTES['daily-kills'])
def daily_kills(steamId):
    result = {}

    # TODO: make this suck less
    result['kills'] = int(sql_value(DAILY_KILL_COUNT, steamId))
    result['deaths'] = int(sql_value(DAILY_DEATH_COUNT, steamId))
    result['dominations'] = int(sql_value(DAILY_DOMINATIONS_COUNT, steamId))
    result['revenges'] = int(sql_value(DAILY_REVENGES_COUNT, steamId))
    print(result)

    return {"result": result}


if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8000, debug=True)
