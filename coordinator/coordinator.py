import sqlite3, json, serial, time, re, threading, pint
import lib.cexprtk as cexprtk
from datetime import datetime, timedelta
from db_man import DatabaseManager
from os import path
from point import Point
from prog_xbee import ProgrammableXBee
from rule import Rule
from ws4py.client.threadedclient import WebSocketClient
        
class Container():
    def __init__(self, obj=None):
        self.__obj = obj
        
    def set_obj(self, obj):
        self.__obj = obj
        
    def get_obj(self):
        return self.__obj


# Constants
CONFIG_PATH = 'coordinator.json'
POINT_CONN_MSG = 'Joining'
CONN_CONFIRM_MSG = 'Join confirmed'
KEYBOARD_INTERRUPT_CODE = 4040

# Load up the config file
with open(CONFIG_PATH) as config_file:
    env = json.load(config_file)

# Create the database manager and unit registry
db_man = DatabaseManager(env['local-db-path'])
ureg = pint.UnitRegistry()
ureg.autoconvert_offset_to_baseunit = True  # Handles temperature ambiguities
Q_ = ureg.Quantity

# Set up the lists of points waiting to connect and already connected with their last readings
points_waiting = {}
points_joined = db_man.get_all_points()
last_reading = {}

# Declare the XBee and ws so the functions have access to it
xbee = None
ws_container = Container()
ws = ws_container.get_obj

# Declare the thread references globally so all functions have access
ws_thread_container = Container()
ws_thread = ws_thread_container.get_obj
connection_thread = None

class PiClient(WebSocketClient):
    def __init__(self, address, headers=None):
        self.isconnected = False
        WebSocketClient.__init__(self, address, headers=headers)

    def opened(self):
        self.isconnected = True
        print('Websocket opened')

    def closed(self, code, reason=None):
        self.isconnected = False
        if code != KEYBOARD_INTERRUPT_CODE:
            # Unexpected disconnection, try to reconnect
            connection_thread = threading.Thread(target=connect_to_server)
            connection_thread.start()
        print('Websocket closed')

    def received_message(self, m):
        print(m)
        handle_message(str(m), self)
        print(m)
   
   
def handle_message(msg, ws):
    '''
    Handles messages received by the client

    msg: the message received
    ws: the Websocket object
    '''
    params = json.loads(msg)
    if 'action' in params:
        # First returned message from the server for verifying the Pi's ID
        if params['action'] == 'id-verification':
            db_man.empty_db()
            if params['status'].lower() == 'new':
                env['pi_id'] = params['id']
                with open(CONFIG_PATH, 'w') as config_file:
                    json.dump(env, config_file, indent=4, separators=(',', ': '), sort_keys=True)
                print('id: ' + env['pi_id'])
            if params['status'].lower() == 'ok':
                for point_type, points in params['points'].viewitems():
                    point_type = str(point_type)
                    if not point_type in points_joined:
                        points_joined[point_type] = {}
                    point_type_dict = points_joined[point_type]
                    for point_id, mode in points.viewitems():
                        point_id = str(point_id)
                        point_type_dict[point_id] = ''
                        db_man.add_point(Point(point_id=point_id, mode=str(mode), name='', point_type=point_type))
                for point_id, rules in params['rules'].viewitems():
                    target_point = db_man.get_point(str(point_id))
                    for rule in rules:
                        db_man.add_rule(Rule(target_device=target_point, **rule))
        # Server can refuse the connection for any reason
        elif params['action'] == 'connection-refused':
            print('Connection was refused by the server: ' + params['status'])
        elif params['action'] == 'request-points':
            if ws.isconnected:
                ws.send(json.dumps({'action': 'available-points', 'request_id': params['request_id'], 'points': points_waiting}))
        elif params['action'] == 'add-point':
            key = str(params['id'])
            point_type = str(params['type'])
            found_point = None
            for point in points_waiting[point_type]:
                if point == key:
                    found_point = points_waiting[point_type][point]
                    del points_waiting[point_type][point] # if found, remove from points waiting
                    break
            if found_point:
                if not point_type in points_joined:
                    points_joined[point_type] = {}
                points_joined[point_type][key] = found_point
                db_man.add_point(Point(point_id=key, name=found_point, point_type=point_type))
        elif params['action'] == 'remove-point':
            key = str(params['id'])
            point_type = str(params['type'])
            found_point = None
            for point in points_joined[point_type]:
                if point == key:
                    found_point = points_joined[point_type][point]
                    del points_joined[point_type][point]
                    break
            if found_point:
                if not point_type in points_waiting:
                    points_waiting[point_type] = {}
                points_waiting[point_type][key] = found_point
                db_man.remove_point(db_man.get_point(key))
        elif params['action'] == 'set-mode':
            point = db_man.get_point(params['id'])
            point.mode = str(params['mode'])
            db_man.update_point(point)
        elif params['action'] == 'control-device':
            split_id = str(params['id']).split(':')
            address = split_id[0]
            remote_id = split_id[1]
            xbee.tx(dest_addr_long=address.decode('hex'), data=remote_id + ':' + str(params['command']).lower())
        elif params['action'] == 'add-rule':
            db_man.add_rule(Rule(target_device=db_man.get_point(str(params['point_id'])), **params['rule']))
        elif params['action'] == 'remove-rule':
            db_man.remove_rule(db_man.get_rule(str(params['server_id'])))
        elif params['action'] == 'edit-rule':
            db_man.update_rule(Rule(target_device=db_man.get_point(str(params['point_id'])), **params['rule']))
            

def sub_base_value(match):
    """
    Converts a given quantity to its base units and returns its magnitude
    """
    
    return str(Q_(match.group(1)).to_base_units().magnitude)


def connect_to_server():
    """
    Continuously attempts to connect to the web server. Should be run in a thread to prevent blocking
    """

    headers = [('name', env['name']), ('password', env['webserver-password'])]
    if 'pi_id' in env: #looks thru env dict for pi_id which is sent by the server if cant be found (first time around) otherwise it passes it in everytime
        headers.append(('id', env['pi_id']))
    ws_container.set_obj(PiClient(env['webserver-address'], headers=headers))
    
    while True:
        try:
            print('Attempting to connect to the server...')
            ws().connect()
            # Successful connection if we've gotten to here, so stop trying to connect
            break
        except KeyboardInterrupt:
            return
        except Exception as e:
            print(e)
            time.sleep(env['reconnect-interval-seconds'])
    
    ws_thread_container.set_obj(threading.Thread(target=ws().run_forever))
    ws_thread().start()


def send_to_server(data, long_address):
    """
    Sends data to the main data/web server
    
    data: string of data to send
    """
    match = re.search('([^:]*):([-+]?\d+(?:\.\d+)?)\s*(.*)', data)
    quantity = Q_(match.group(2) + ' ' + match.group(3))
    
    if ws().isconnected:
        ws().send(json.dumps({'action': 'record', 'address': long_address, 'remote_id': match.group(1), 'value': quantity.magnitude, 'unit': str(quantity.units)}))
    
    
def perform_rule_action(rule):
    """
    Performs the action specified by the provided rule
    
    rule: the rule specifying which action to perform on which device
    """
    
    # TODO
    print('performing rule action {} on {}'.format(rule.action, rule.target_device.point_id))
    split_id = rule.target_device.point_id.split(':')
    xbee.tx(dest_addr_long=split_id[0].decode('hex'), data=split_id[1] + ':' + rule.action.lower())
    

def enforce_rules(point):
    """
    Enforces rules set by the user
    
    long_address: the address of the point to check rules for
    """
    
    if point is None:
        return
    
    rules = db_man.get_rules_for_sensor(point)
    for rule in rules:
        if not rule.is_active or rule.target_device.mode.lower() != 'auto':
            continue
            
        failed = False
        subbed_expression = rule.expression
        for match in re.finditer('{(?:[^|]*\|)?([A-Fa-f0-9]+:\d+).*}', rule.expression):
            # Replace all occurrences of point addresses (enclosed in braces) in the expression with their most recent value
            if match.group(1) not in last_reading:
                # At least one of the addresses specified in the expression doesn't have a last reading, so the expression can't be evaluated
                failed = True
                break
            subbed_expression = re.sub('{(?:[^|]*\|)?([A-Fa-f0-9]+:\d+).*}', str(last_reading[match.group(1)].magnitude), subbed_expression, count=1)
        if failed:
            continue
        # Ensure all values are in base units
        subbed_expression = re.sub('\[([-+]?\d+(?:\.\d+)?\s*.*)\]', sub_base_value, subbed_expression)
        
        # Need to explicitly assert the expression returns true here, otherwise non-zero, non-None return values would also pass
        if cexprtk.evaluate_expression(subbed_expression, {}) == True:
            perform_rule_action(rule)


def handle_rx_packet(packet):
    """
    Handles received packets
    
    Everything in this packet dic is binary. Encode belongs to binary library, changing binary to string. Decode belongs to string lib, changing string to binary
    packet: dictionary representation of a packet generated by the ZigBee class
    """
    
    # Convert the xbee address (MAC address) to a human-readable string
    long_address = packet['source_addr_long'].encode('hex')
    
    # Check if the packet is an initial connection packet from a point
    if POINT_CONN_MSG in packet['rf_data']:
        points = packet['rf_data'][len(POINT_CONN_MSG):]
        counter_NameArr = 0
        for point in points.split(';'):
            point_id = long_address + ':' + str(counter_NameArr)
            point_split = point.split(':')
            name = point_split[0]
            if point_split[1].lower() == 's': 
                pt_type = "sensor"
            else: 
                pt_type = "controllable_device"
            
            # Check to see if the point is already joined
            if pt_type in points_joined and point_id in points_joined[pt_type]:
                points_joined[pt_type][point_id] = name
                point = db_man.get_point(point_id)
                point.name = name
                db_man.update_point(point)
            else:
                if not pt_type in points_waiting:
                    points_waiting[pt_type] = {}
                points_waiting[pt_type][point_id] = name
                
            counter_NameArr += 1 

        xbee.tx(dest_addr_long=long_address.decode('hex'), data=CONN_CONFIRM_MSG)
        return
    
    # Point is sending data intended for the server, so cache the value, pass it on and check if there are any rules set on the sensor value
    for reading in packet['rf_data'].split(';'):
        match = re.search('([^:]*):([-+]?\d+(?:\.\d+)?\s*.*)', reading)
        point_id = long_address + ":" + match.group(1)
        last_reading[point_id] = Q_(match.group(2)).to_base_units()
        send_to_server(reading, long_address)
        enforce_rules(db_man.get_point(point_id))
    

def xbee_callback(packet):
    """
    Callback function that is executed for each received packet
    
    packet: dictionary representation of a packet generated by the ZigBee class
    """
    
    # DEBUG
    print(str(datetime.now()) + str(packet))
    
    # Check the type of packet and dispatch it to the appropriate handler
    if packet['id'] == 'rx':
        handle_rx_packet(packet)


# Entry point

if __name__ == '__main__':
    xbee = ProgrammableXBee(env)

    connection_thread = threading.Thread(target=connect_to_server)
    connection_thread.start()
        
    while True:
        try:
            xbee_callback(xbee.wait_read_frame())
        except KeyboardInterrupt:
            if ws():
                ws().close(code=KEYBOARD_INTERRUPT_CODE)
            if ws_thread():
                ws_thread().join()
            break
            
    xbee.halt()
