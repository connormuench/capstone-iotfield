from ws4py.client.threadedclient import WebSocketClient
import json, threading

points_waiting = {
    'sensor': [{'id': '12345678:0', 'name': 'Temperature sensor'}, {'id': '12345678:1', 'name': 'Water level sensor'}, {'id': '87654321:0', 'name': 'Water level sensor'}],
    'controllable_device': [{'id': '87654321:1', 'name': 'Water pump'}, {'id': '12345679:0', 'name': 'Water valve'}]  
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
                if point['id'] == key:
                    found_point = point
                    points_waiting[point_type].remove(point)
                    break
            if found_point:
                if not point_type in points_joined:
                    points_joined[point_type] = []
                points_joined[point_type].append(found_point)
        if params['action'] == 'remove-point':
            key = str(params['id'])
            point_type = str(params['type'])
            found_point = None
            for point in points_joined[point_type]:
                if point['id'] == key:
                    found_point = point
                    points_joined[point_type].remove(point)
                    break
            if found_point:
                if not point_type in points_joined:
                    points_waiting[point_type] = []
                points_waiting[point_type].append(found_point)


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

if __name__ == '__main__':
    try:
        ws = PiClient('ws://127.0.0.1:3002', headers=[('name', 'Moon Facility'), ('password', 'popeye'), ('id', '0112c6ea56b26df4')])
        #ws = PiClient('ws://127.0.0.1:3002', headers=[('name', 'Moon Facility'), ('password', 'popeye')])
        ws.connect()
        t = threading.Thread(target=ws.run_forever)
        t.start()
        while t.isAlive():
            t.join(1)
    except KeyboardInterrupt:
        ws.close()
        t.join()
