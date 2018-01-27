import sqlite3
from point import Point
from rule import Rule
from os import path
import re

class DatabaseManager():
    def __init__(self, db_path):
        """
        Constructor for the DatabaseManager class
        
        db_path: path to the location of the SQLite3 database
        """
        
        self.__conn = sqlite3.connect(path.abspath(db_path))
        
        # use this so dictionaries are returned instead of tuples
        self.__conn.row_factory = sqlite3.Row
        self.__cur = self.__conn.cursor()
    
    
    def get_all_points(self):
        """
        Retrieves a list of all Points in the database
        """
        
        self.__cur.execute('SELECT *, rowid FROM points;')
        temp_dic = {}
        for record in self.__cur.fetchall():
            temp_dic[record['point_id']] = None
        return temp_dic
        
        
    def get_point(self, long_address):
        """
        Retrieves the point corresponding to the provided long address
        
        long_address: the long address of the Point to retrieve
        """
        
        self.__cur.execute('SELECT *, rowid FROM points WHERE point_id = ?;', (long_address,))
        return Point(**self.__cur.fetchone())
    
        
    def add_point(self, point):
        """
        Adds a point to the table of connected points in the database
        
        point: the Point to be added to the database
        """
        
        self.__cur.execute("INSERT INTO points (point_id) VALUES (?);", (point.long_address,))
        self.__conn.commit()
    
        
    def get_rules_for_sensor(self, sensor):
        """
        Gets rules associated with the provided sensor
        This differs from get_rules_for_controllable_device() as it gets rules that the provided device is part of the expression for
        
        sensor: the Point to get rules for
        """
        
        self.__cur.execute("""SELECT rules.rowid, expression, target_device, action, target_devices.long_address FROM 
                                (rules INNER JOIN rule_point ON rules.rowid = rule_id) 
                                    INNER JOIN points AS sensors ON sensors.rowid = point_id 
                                        INNER JOIN points AS target_devices ON target_devices.rowid = target_device
                                        WHERE sensors.point_id = ?;""", (sensor.point_id,))
        return [Rule(rowid=rule['rowid'], expression=rule['expression'], target_device=Point(rowid=rule['target_device'], long_address=rule['long_address']), action=rule['action']) for rule in self.__cur.fetchall()]
        
        
    def get_rules_for_controllable_device(self, controllable_device):
        """
        Gets rules associated with the provided controllable device
        This differs from get_rules_for_sensor() as it gets rules that the provided device is the target device for
        
        controllable_device: the Point to get rules for
        """
        
        self.__cur.execute("""SELECT rules.rowid, expression, target_device, action, long_address FROM 
                                rules INNER JOIN points ON points.rowid = target_device 
                                WHERE long_address = ?;""", (controllable_device.long_address,))
        return [Rule(rowid=rule['rowid'], expression=rule['expression'], target_device=Point(rowid=rule['target_device'], long_address=rule['long_address']), action=rule['action']) for rule in self.__cur.fetchall()]
        
    
    def add_rule(self, rule):
        """
        Adds a rule to the database
        
        rule: the Rule to add to the database
        """
        
        if not rule.target_device.point_id:
            rule.target_device = self.get_point(rule.target_device.long_address)
        self.__cur.execute('INSERT INTO rules (expression, target_device, action) VALUES (?, ?, ?);', (rule.expression, rule.target_device.point_id, rule.action))
        self.__conn.commit()
        
        self.__add_relationships_for_rule(rule)
        
    
    def __add_relationships_for_rule(self, rule):
        """
        Adds the relationships for the new rule into the database
        
        rule: the Rule to add to the database
        """
        
        long_addresses = re.findall('{([a-fA-F0-9]+)}', rule.expression)
        print long_addresses
        self.__cur.execute("SELECT rowid FROM rules WHERE expression = ?;", (rule.expression,))
        rule_id = self.__cur.fetchone()['rowid']
        point_ids = []
        for long_address in long_addresses:
            self.__cur.execute("SELECT rowid FROM points WHERE point_id = ?;", (long_address,))
            point_ids.append(self.__cur.fetchone()['rowid'])
        print point_ids
        print [(rule_id, point_id) for point_id in point_ids]
        self.__cur.executemany("INSERT INTO rule_point (rule_id, point_id) VALUES (?, ?);", [(rule_id, point_id) for point_id in point_ids])
        self.__conn.commit()
        
        
