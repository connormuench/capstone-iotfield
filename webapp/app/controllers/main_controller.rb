class MainController < ApplicationController
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
end
