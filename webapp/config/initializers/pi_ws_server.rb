require 'em-websocket'
require 'pi_lists'
require 'securerandom'
require 'json'

pi_lists = PiLists.instance

class EM::WebSocket::Connection
  def remote_ip
    get_peername[2,6].unpack('nC4')[1..4].join('.')
  end
end

# Spin up a new thread for running the Pi Websocket server
Thread.new {
  EM.run {
    EM::WebSocket.run(host: '0.0.0.0', port: '3002') do |ws|
      # Callback to run whenever a new connection is created
      ws.onopen { |handshake|
        # DEBUG print the details of the new connection
        puts "Websocket opened #{{path: handshake.path, query: handshake.query, origin: handshake.origin, headers: handshake.headers}}"
        # Validate the provided password
        if handshake.headers['password'] == ENV['FACILITY_ACCESS_PASSWORD']
          # If the Pi provided its own ID, check to see if it is already used by another
          if handshake.headers.key?('id') && !pi_lists.not_accepted.key?(handshake.headers['id']) && !pi_lists.accepted.key?(handshake.headers['id'])
            points = {}
            points[:sensor] = {}
            points[:controllable_device] = {}
            rules = {}
            if Facility.where(pi_id: handshake.headers['id']).count == 0
              # No match in the DB, so add it to the list of unaccepted Pis
              pi_lists.not_accepted[handshake.headers['id']] = {ws: ws, hs: handshake}
            else
              # Pi exists in the DB, so add it to the list of accepted Pis and update its IP address in the DB, if necessary
              pi_lists.accepted[handshake.headers['id']] = {ws: ws, hs: handshake}
              facility = Facility.where(pi_id: handshake.headers['id'])[0]
              facility.network_address = ws.remote_ip
              facility.save
              facility.end_devices.each do |end_device|
                end_device.sensors.each do |sensor|
                  points[:sensor][end_device.address + ':' + sensor.point.remote_id.to_s] = 'n/a'
                end
                end_device.controllable_devices.each do |controllable_device|
                  remote_id = end_device.address + ':' + controllable_device.point.remote_id.to_s
                  points[:controllable_device][remote_id] = controllable_device.mode.downcase
                  rules[remote_id] = controllable_device.rules.map { |rule| {expression: rule.expression, action: rule.action, is_active: rule.is_active, server_id: rule.id} }
                end
              end
            end
            ws.send({action: 'id-verification', status: 'OK', points: points, rules: rules}.to_json)
          else
            # Pi either didn't provide its own or the one it provided is already in use, so generate a new, unique ID
            pi_id = nil
            loop do
              pi_id = SecureRandom.hex(8)
              break if !pi_lists.not_accepted.key?(pi_id) && !pi_lists.accepted.key?(pi_id) && Facility.where(pi_id: pi_id).count == 0
            end
            # Send the new ID back to the Pi and add it to the list of unaccepted Pis
            ws.send({action: 'id-verification', status: 'new', id: pi_id}.to_json)
            pi_lists.not_accepted[pi_id] = {ws: ws, hs: handshake}
          end
        else
          ws.send({action: 'connection-refused', status: 'Invalid password'}.to_json)
          ws.close()
        end
      }

      # Callback to run whenever a new message is received
      ws.onmessage { |msg|
        jsonified_msg = JSON.parse(msg)
        puts msg
        if jsonified_msg.key?('action')
          puts('debug6')
          # ACTION: available-points
          if jsonified_msg['action'] == 'available-points'
            # Add the points to the points map for the controller to retrieve
            pi_lists.points[jsonified_msg['request_id']] = jsonified_msg['points']
            puts('debug7')
          # ACTION: record
          elsif jsonified_msg['action'] == 'record'
            # Identify the specified end device and point
            puts('debug8')
            end_device = EndDevice.where(address: jsonified_msg['address']).first
            pp(end_device)
            if !end_device.nil?
    puts('debug9')
              point = end_device.points.find { |point| point.remote_id.to_s == jsonified_msg['remote_id'].to_s }
              if !point.nil?
    puts('debug10')
                # Add the record to the point's list of records
                record = point.records.new(value: jsonified_msg['value'], unit: jsonified_msg['unit'])
    puts('debug11')
                record.save_and_broadcast
    puts('debug12')
              end
            end
          end
        end
        #ws.send({pong: msg}.to_json)
      }

      # Callback to run whenever a connection is closed
      ws.onclose {
        pi_lists.not_accepted.each_pair { |k, v| pi_lists.not_accepted.delete k if v[:ws] == ws }
        pi_lists.accepted.each_pair { |k, v| pi_lists.accepted.delete k if v[:ws] == ws }
        puts 'ws closed'
      }

      # Callback to run whenever an error occurs with a connection
      ws.onerror { |e|
        puts "Websocket Error: #{e.to_json}"
      }
    end
  }
}
