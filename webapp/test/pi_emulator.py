from ws4py.client.threadedclient import WebSocketClient
import json, threading, random, time

points_waiting = {
    'sensor': {'12345678:0': 'Temperature sensor', '12345678:1': 'Water level sensor', '87654321:0': 'Water level sensor'},
    'controllable_device': {'87654321:1': 'Water pump', '12345679:0': 'Water valve'}
}

points_joined = {}

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
                ws.id = params['id']
                print('id: ' + ws.id)
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
                if point == key:
                    found_point = points_waiting[point_type][point]
                    del points_waiting[point_type][point]
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
                if not point_type in points_joined:
                    points_waiting[point_type] = {}
                points_waiting[point_type][key] = found_point


class PiClient(WebSocketClient):
    def __init__(self, address, headers=None):
        self.id = ''
        WebSocketClient.__init__(self, address, headers=headers)

    def opened(self):
        print('success')
        pass

    def closed(self, code, reason=None):
        print('closed')
        pass

    def received_message(self, m):
        handle_message(str(m), self)
        print(m)

def sendData(ws):
    if 'sensor' in points_joined:
        for sensor in points_joined['sensor']:
            ws.send(json.dumps({'action': 'record', 'address': sensor['id'].split(':')[0], 'remote_id': int(sensor['id'].split(':')[1]), 'value': random.randint(20, 25), 'unit': 'degC'}))

if __name__ == '__main__':
    random.seed()
    try:
        ws = PiClient('ws://127.0.0.1:3002', headers=[('name', 'Moon Facility'), ('password', 'popeye'), ('id', '0112c6ea56b26df4')])
        #ws = PiClient('ws://127.0.0.1:3002', headers=[('name', 'Moon Facility'), ('password', 'popeye')])
        ws.connect()
        t = threading.Thread(target=ws.run_forever)
        t.start()
        while t.isAlive():
            t.join(1)
            time.sleep(2)
            sendData(ws)
    except KeyboardInterrupt:
        ws.close()
        t.join()
