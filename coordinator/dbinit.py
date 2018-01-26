import sqlite3, os, json
from os import path

CONFIG_PATH = 'coordinator.json'

# Load up the config file to get the db path
with open(CONFIG_PATH) as config_file:
    env = json.load(config_file)
    
db_filename = path.abspath(env['local-db-path'])

if path.exists(db_filename):
    os.remove(db_filename)

conn = sqlite3.connect(db_filename)
cur = conn.cursor()

# Create the new tables

"""
TABLE points

long_address: the serial number of the XBee associated with the point
"""
cur.execute("CREATE TABLE points(point_id TEXT UNIQUE);")

"""
TABLE rules

expression: a cexprtk-compatible conditional expression. Long addresses of Points in the statement must be contained contained within braces ({}) to be parsed
target_device: the long address of the device to manipulate
action: the action to perform when expression is true
"""
cur.execute("CREATE TABLE rules(expression TEXT, target_device TEXT, action TEXT);")

"""
TABLE rule_point

point_id: rowid of a point
rule_id: rowid of a rule
"""
cur.execute("CREATE TABLE rule_point(point_id INTEGER, rule_id INTEGER);")

conn.commit()

conn.close()

