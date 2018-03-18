class MainController < ApplicationController
  before_action :authenticate_user!
  before_action only: [:admin_panel] { check_admin '/' }

  def search
    @facilities = []
    @controllable_devices = []
    @sensors = []
    query = params[:q].downcase

    current_user.facilities.each do |facility|
      if facility.name.downcase.include?(query)
        @facilities.push(facility)

        # Add all points from facility to list of results
        facility.end_devices.each do |end_device|
          @controllable_devices.concat(end_device.controllable_devices)
          @sensors.concat(end_device.sensors)
        end
      else
        # Add all points from facility that match the query
        facility.end_devices.each do |end_device|
          @controllable_devices.concat(end_device.controllable_devices.select { |controllable_device| controllable_device.point.name.downcase.include?(query) })
          @sensors.concat(end_device.sensors.select { |sensor| sensor.point.name.downcase.include?(query) })
        end
      end
    end

    respond_to do |format|
      format.html {
        # Link the facilities to their access level for the current user
        @access_levels = []
        @facilities.each do |facility|
          @access_levels.concat(facility.access_levels.select { |access_level| access_level.user_id == current_user.id })
        end
      }
      format.json {
        # Limit results so the dropdown has a max length
        limit = 4
        @facilities = @facilities[0..limit].map do |facility| 
          {
            name: facility.name, 
            url: facility_path(facility)
          }
        end

        @controllable_devices = @controllable_devices[0..limit].map do |controllable_device|
          {
            name: controllable_device.point.name + ' | ' + controllable_device.point.end_device.facility.name, 
            url: facility_controllable_device_path(controllable_device.point.end_device.facility.id, controllable_device)
          }
        end

        @sensors = @sensors[0..limit].map do |sensor|
          {
            name: sensor.point.name + ' | ' + sensor.point.end_device.facility.name, 
            url: facility_sensor_path(sensor.point.end_device.facility.id, sensor)
          }
        end

        render json: {facilities: @facilities, controllable_devices: @controllable_devices, sensors: @sensors}
      }
    end
  end

  def visualization
    respond_to do |format|
      format.html {
        @data = {}
      }
      format.json {
        points_tree = []
        current_user.facilities.each do |facility|
          facility_tree = {id: facility.id * -1, text: facility.name, children: []}
          facility.end_devices.each do |end_device|
            end_device.points.each do |point|
              quantity = 'unitless'
              if point.records.count > 0 && point.records[0].unit == 'degC'
                quantity = 'temperature'
              end
              facility_tree[:children].push({id: point.id, text: point.name, quantity: quantity})
            end
          end
          points_tree.push(facility_tree)
        end
        render json: points_tree
      }
    end
  end

  def points
    points_list = []
    if params.include?(:point_ids)
      params[:point_ids].each do |point_id|
        points_list.push(Point.find(point_id))
      end
    end

    respond_to do |format|
      format.html {}
      format.json {
        render json: {y_axis: 'Temperature (degC)', x_axis: 'Time', data: chart_data_from_points(points_list)}
      }
    end
  end

  def admin_panel
    @users = {}
    User.all.each do |user|
      @users[user.id] = {}
    end

    @facilities =  {}
    Facility.all.each do |facility|
      @facilities[facility.id] = {}
    end

    AccessLevel.all.each do |access_level|
      @users[access_level.user_id][access_level.facility_id] = access_level.level
      @facilities[access_level.facility_id][access_level.user_id] = access_level.level
    end

  end
end
