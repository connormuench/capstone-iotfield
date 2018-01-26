import sqlite3, json, serial, time, re, threading
import lib.cexprtk as cexprtk
from datetime import datetime
from db_man import DatabaseManager
from os import path
from point import Point
from prog_xbee import ProgrammableXBee
from ws4py.client.threadedclient import WebSocketClient

# String constants
CONFIG_PATH = 'coordinator.json'
POINT_CONN_MSG = 'Joining' #mar: changed from Waiting to join to joining. change in codewarrior
CONN_CONFIRM_MSG = 'Join confirmed'

# Load up the config file
with open(CONFIG_PATH) as config_file:
    env = json.load(config_file)

# Create the database manager
db_man = DatabaseManager(env['local-db-path'])

# Set up the lists of points waiting to connect and already connected with their last readings
points_waiting = {}
points_joined = db_man.get_all_points()
last_reading = {}

# Declare the XBee and ws so the functions have access to it
xbee = None
ws = None

class PiClient(WebSocketClient):
    def __init__(self, address, headers=None):
        #self.id = ''
        WebSocketClient.__init__(self, address, headers=headers)

    def opened(self):
        print('success')
       # pass

    def closed(self, code, reason=None):
        print('closed')
       # pass

    def received_message(self, m):
        handle_message(str(m), self) #string rep of m
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
            if 'status' in params and params['status'].lower() == 'new':
                env['pi_id'] = params['id']
                print('id: ' + env['pi_id'])
        # Server can refuse the connection for any reason
        if params['action'] == 'connection-refused':
            print('Connection was refused by the server: ' + params['status'])
        if params['action'] == 'request-points':
            ws.send(json.dumps({'action': 'available-points', 'request_id': params['request_id'], 'points': points_waiting}))
        if params['action'] == 'add-point':
            key = str(params['id'])
            point_type = str(params['type'])
            found_point = None
            for point in points_waiting[point_type]:
                if point == key: #point = point id and key = passed in
                    found_point = points_waiting[point_type][point]
                    del points_waiting[point_type][point] #if found, remove from points waiting
                    break
            if found_point:
                if not point_type in points_joined:
                    points_joined[point_type] = {}
                points_joined[point_type][key] = found_point
        if params['action'] == 'remove-point':
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

def send_to_server(data, long_address):
    """
    Sends data to the main data/web server
    last_reading[long_address] = re.search('[^:]*:(\d+)\s*.*', packet['rf_data']).group(0)
    data: string of data to send
    """
    match = re.search('([^:]*):([-+]?\d+(?:\.\d+)?)\s*(.*)', reading)
    
    ws.send(json.dumps({'action': 'record', 'address': long_address, 'remote_id': match.group(0), 'value': match.group(1), 'unit': match.group(2)}))
    
    
   #TODO 
def perform_rule_action(long_address, action):
    """
    Performs the action specified by the provided rule
    
    rule: the rule specifying which action to perform on which device
    """
    
    # TODO
    pass
    
#TODO
def enforce_rules(long_address):
    """
    Enforces rules set by the user
    
    long_address: the address of the point to check rules for
    """
    
    # TODO UNTESTED
    rules = db_man.get_rules_for_sensor(Point(long_address=long_address))
    for rule in rules:
        failed = False
        subbed_expression = rule.expression
        for match in re.finditer('{([A-Fa-f0-9]+)}', rule.expression):
            # Replace all occurrences of point addresses (enclosed in braces) in the expression with their most recent value
            if match.group(0) not in last_reading:
                # At least one of the addresses specified in the expression doesn't have a last reading, so the expression can't be evaluated
                failed = True
                break
            subbed_expression = re.sub('{([A-Fa-f0-9]+)}', last_reading[match.group(0)], subbed_expression, count=1)
        if failed:
            continue
        
        # Need to explicitly assert the expression returns true here, otherwise non-zero, non-None return values would also pass
        if cexprtk.evaluate_expression(subbed_expression) == True:
            perform_rule_action(rule.long_address, rule.action)


def handle_rx_packet(packet):
    """
    Handles received packets
    
    Eveyrhting in this packet dic is binary. encode belongs to binary library , changing binary to hex. and decode belongs to string lib , changing hex to binary
    packet: dictionary representation of a packet generated by the ZigBee class
    """
    
    # Convert the xbee address (MAC address) to a human-readable string which is set on the xbee xctu
    long_address = packet['source_addr_long'].encode('hex')
    
    # Check if the packet is an initial connection packet from a point
    if POINT_CONN_MSG in packet['rf_data']:
        points = packet['rf_data'][len(POINT_CONN_MSG):] #includes name and type
        counter_NameArr = 0
        for point in points.split(';'):
            point_id = long_address + ':' + str(counter_NameArr)
            point_split = point.split(':')
            name = point_split[0]
            if point_split[1].lower() == 's': 
                pt_type = "sensor"
            else: 
                pt_type = "controllable_device"
                
            pt_type = point_split[1]
            
        # Check to see if the point was already connected : point is always going to be a key from the dictionary from get all points
            if point_id in points_joined: #returns a boolean (1 if true ) 
                if not pt_type in points_joined: 
                    points_joined[pt_type] = {}
                points_joined[pt_type][point_id] = name
            else: 
                #points_waiting[point_id] = name #if not joined, then we assume it's waiting so will simulatenaouly add the key and the value 
                if not pt_type in points_waiting: 
                    points_waiting[pt_type] = {}
                points_waiting[pt_type][point_id] = name
            counter_NameArr += 1  

        xbee.tx(dest_addr_long=long_address.decode('hex'), data=CONN_CONFIRM_MSG)
       
        # DEBUG Temporary section for auto-adding points until the web server is running and we can add from there
        """
        point = Point(long_address=long_address)
        points_joined.append(point)
        db_man.add_point(point)
        xbee.tx(dest_addr_long=long_address.decode('hex'), data=CONN_CONFIRM_MSG)
        """    
        # Add the point to the list of waiting points the user can add through the web application
        #points_waiting.append(packet['source_addr_long'])
        return
    
    # Point is sending data intended for the server, so cache the value, pass it on and check if there are any rules set on the sensor value
    for reading in packet['rf_data'].split(';'):
        match = re.search('([^:]*):([-+]?\d+(?:\.\d+)?)\s*.*', reading)
        point_id = long_address + ":" + match.group(0) #match.group(0) is the ID number of the points in the point (ex: 0: temp sensor means 0 is the ID number)
        last_reading[point_id] = match.group(1)
        send_to_server(reading, long_address)
        enforce_rules(point_id)
    

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

xbee = ProgrammableXBee(env)

try:
    headers = [('name', env['name']), ('password', env['webserver_password'])]
    if 'pi_id' in env: #looks thru env def for pi_id which is sent by the server if cant be found (first time around) otherwise it passes it in everytime
        headers.append(('id', env['pi_id']))
    ws = PiClient(env['webserver_address'], headers=headers)
    ws.connect()
    t = threading.Thread(target=ws.run_forever)
    t.start()
    
while True:
    try:
        
        xbee_callback(xbee.wait_read_frame())
    except KeyboardInterrupt:
        ws.close()
        t.join()
        break
        
xbee.halt()
