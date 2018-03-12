import sqlite3, re, json
from point import Point
from rule import Rule
from os import path
from threading import Lock

class DatabaseManager():
    def __init__(self, db_path):
        """
        Constructor for the DatabaseManager class
        
        db_path: path to the location of the SQLite3 database
        """
        
        self.__conn = sqlite3.connect(path.abspath(db_path), check_same_thread=False)
        
        # use this so dictionaries are returned instead of tuples
        self.__conn.row_factory = sqlite3.Row
        self.__conn.text_factory = str
        self.__cur = self.__conn.cursor()
        self.__conn_lock = Lock()
    
    
    def get_all_points(self):
        """
        Retrieves a list of all Points in the database
        """
        
        self.__conn_lock.acquire()
        self.__cur.execute('SELECT *, rowid FROM points;')
        points = {}
        records = self.__cur.fetchall()
        self.__conn_lock.release()
        for record in records:
            if not record['point_type'] in points:
                points[record['point_type']] = {}
            points[record['point_type']][record['point_id']] = record['name']
        return points
        
        
    def get_point(self, point_id):
        """
        Retrieves the point corresponding to the provided point_id
        
        point_id: the point_id of the Point to retrieve
        """
        
        self.__conn_lock.acquire()
        self.__cur.execute('SELECT *, rowid FROM points WHERE point_id = ?;', (point_id,))
        point = self.__cur.fetchone()
        self.__conn_lock.release()
        return None if point is None else Point(**point)
        
        
    def get_point_by_rowid(self, rowid):
        """
        Retrieves the point corresponding to the provided rowid
        
        rowid: the rowid of the Point to retrieve
        """
        
        self.__conn_lock.acquire()
        self.__cur.execute('SELECT *, rowid FROM points WHERE rowid = ?;', (rowid,))
        point = self.__cur.fetchone()
        self.__conn_lock.release()
        return None if point is None else Point(**point)
    
        
    def add_point(self, point):
        """
        Adds a point to the table of connected points in the database
        
        point: the Point to be added to the database
        """
        
        self.__conn_lock.acquire()
        self.__cur.execute("INSERT INTO points (point_id, name, point_type, mode) VALUES (?, ?, ?, ?);", (point.point_id, point.name, point.point_type, point.mode))
        self.__conn.commit()
        self.__conn_lock.release()
        
    
    def remove_point(self, point):
        """
        Removes a point from the table of connected points, as well as any rule relationships it has
        
        point: the Point to be removed from the database
        """
        
        point = self.get_point(point.point_id)
        
        if point is None:
            return
            
        rules = self.get_rules_for_controllable_device(point)
        
        self.__conn_lock.acquire()
        self.__cur.execute("DELETE FROM points WHERE rowid = ?;", (point.rowid,))
        self.__cur.execute("DELETE FROM rule_point WHERE point_id = ?;", (point.rowid,))
        self.__cur.execute("DELETE FROM rules WHERE target_device = ?;", (point.rowid,))
        self.__cur.executemany("DELETE FROM rule_point WHERE rule_id = ?;", [(rule.rowid) for rule in rules])
        self.__conn.commit()
        self.__conn_lock.release()
        
    
    def update_point(self, point):
        """
        Updates a point with new values
        
        point: the Point to be updated, with its new values. Must have rowid set
        """
        
        if point is None:
            return
        
        self.__conn_lock.acquire()
        self.__cur.execute('UPDATE points SET name = ?, point_type = ?, mode = ? WHERE rowid = ?', (point.name, point.point_type, point.mode, point.rowid))
        self.__conn.commit()
        self.__conn_lock.release()
    
        
    def get_rules_for_sensor(self, sensor):
        """
        Gets rules associated with the provided sensor
        This differs from get_rules_for_controllable_device() as it gets rules that the provided device is part of the expression for
        
        sensor: the Point to get rules for
        """
        
        if sensor is None:
            return
        
        self.__conn_lock.acquire()
        self.__cur.execute("""SELECT rules.rowid, expression, target_device, action, target_devices.point_id, is_active, server_id FROM 
                                (rules INNER JOIN rule_point ON rules.rowid = rule_id) 
                                    INNER JOIN points AS sensors ON sensors.rowid = rule_point.point_id 
                                        INNER JOIN points AS target_devices ON target_devices.rowid = target_device
                                        WHERE sensors.point_id = ?;""", (sensor.point_id,))
        records = self.__cur.fetchall()
        self.__conn_lock.release()
        return [Rule(rowid=rule['rowid'], expression=rule['expression'], target_device=self.get_point(rule['point_id']), action=rule['action'], is_active=json.loads(rule['is_active']), server_id=rule['server_id']) for rule in records]
        
        
    def get_rules_for_controllable_device(self, controllable_device):
        """
        Gets rules associated with the provided controllable device
        This differs from get_rules_for_sensor() as it gets rules that the provided device is the target device for
        
        controllable_device: the Point to get rules for
        """
        
        if controllable_device is None:
            return
        
        controllable_device = self.get_point(controllable_device.point_id)
        
        if controllable_device is None:
            return
        
        self.__conn_lock.acquire()
        self.__cur.execute("""SELECT rules.rowid, expression, target_device, action, point_id, is_active, server_id FROM 
                                rules INNER JOIN points ON points.rowid = target_device 
                                WHERE point_id = ?;""", (controllable_device.point_id,))
        records = self.__cur.fetchall()
        self.__conn_lock.release()
        return [Rule(rowid=rule['rowid'], expression=rule['expression'], target_device=controllable_device, action=rule['action'], is_active=json.loads(rule['is_active']), server_id=rule['server_id']) for rule in records]
        
    
    def get_rule(self, server_id):
        """
        Gets a rule specified by the provided server_id
        
        server_id: the ID of the rule on the server
        """
        
        self.__conn_lock.acquire()
        self.__cur.execute('SELECT *, rowid FROM rules WHERE server_id = ?;', (server_id,))
        rule = dict(self.__cur.fetchone())
        self.__conn_lock.release()
        
        if not rule:
            return None
        
        rule['target_device'] = self.get_point_by_rowid(rule['target_device'])
        rule['is_active'] = json.loads(rule['is_active'].lower())
        
        return Rule(**rule)
    
    
    def add_rule(self, rule):
        """
        Adds a rule to the database
        
        rule: the Rule to add to the database
        """
        
        if not rule.target_device.rowid:
            rule.target_device = self.get_point(rule.target_device.point_id)
        self.__conn_lock.acquire()
        self.__cur.execute('INSERT INTO rules (expression, target_device, action, is_active, server_id) VALUES (?, ?, ?, ?, ?);', (rule.expression, rule.target_device.rowid, rule.action, rule.is_active, rule.server_id))
        self.__conn.commit()
        self.__conn_lock.release()
        
        self.__add_relationships_for_rule(rule)
        
        
    def remove_rule(self, rule):
        """
        Removes a rule from the database
        
        rule: the rule to remove from the database
        """
        
        if rule is None:
            return
        
        if not rule.rowid:
            rule = self.get_rule(rule.server_id)
            
        if rule is None:
            return
            
        self.__conn_lock.acquire()
        self.__cur.execute('DELETE FROM rules WHERE rowid = ?;', (rule.rowid,))
        self.__cur.execute('DELETE FROM rule_point WHERE rule_id = ?;', (rule.rowid))
        self.__conn.commit()
        self.__conn_lock.release()
        
        
    def update_rule(self, rule):
        """
        Updates a rule in the database
        
        rule: the rule to be updated
        """
        
        if rule is None:
            return
        
        if not rule.rowid:
            rule.rowid = self.get_rule(rule.server_id).rowid
            
        if rule is None:
            return
            
        self.__conn_lock.acquire()
        self.__cur.execute('UPDATE rules SET expression = ?, target_device = ?, action = ?, is_active = ? WHERE rowid = ?;', (rule.expression, rule.target_device.rowid, rule.action, rule.is_active, rule.rowid))
        self.__cur.execute('DELETE FROM rule_point where rule_id = ?;', (rule.rowid,))
        self.__conn.commit()
        self.__conn_lock.release()
        
        self.__add_relationships_for_rule(rule)
        
        
    def empty_db(self):
        """
        Empties all tables in the database
        """
        
        self.__conn_lock.acquire()
        self.__cur.execute('DELETE FROM points;')
        self.__cur.execute('DELETE FROM rules;')
        self.__cur.execute('DELETE FROM rule_point;')
        self.__conn.commit()
        self.__conn_lock.release()
        
    
    def __add_relationships_for_rule(self, rule):
        """
        Adds the relationships for the new rule into the database
        
        rule: the Rule to add to the database
        """
        
        if rule is None:
            return
            
        # Find all point IDs in the expression
        point_ids = re.findall('{(?:[^|]*\|)?([a-fA-F0-9]+:\d+)}', rule.expression)
        if not rule.rowid:
            rule = self.get_rule(rule.server_id)
            
        if rule is None:
            return
            
        rule_id = rule.rowid
        rowids = []
        self.__conn_lock.acquire()
        for point_id in point_ids:
            self.__cur.execute("SELECT rowid FROM points WHERE point_id = ?;", (point_id,))
            point = self.__cur.fetchone()
            if point is not None:
                rowids.append(point['rowid'])
        self.__cur.executemany("INSERT INTO rule_point (rule_id, point_id) VALUES (?, ?);", [(rule_id, rowid) for rowid in rowids])
        self.__conn.commit()
        self.__conn_lock.release()
