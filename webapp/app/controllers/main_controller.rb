class MainController < ApplicationController
  def search
    @facilities = []
    @controllable_devices = []
    @sensors = []
    query = params[:q].downcase

    current_user.facilities.each do |facility|
      if facility.name.downcase.include?(query)
        @facilities.push(facility)
        facility.end_devices.each do |end_device|
          @controllable_devices.concat(end_device.controllable_devices)
          @sensors.concat(end_device.sensors)
        end
        next
      end
      facility.end_devices.each do |end_device|
        @controllable_devices.concat(end_device.controllable_devices.select { |controllable_device| controllable_device.point.name.downcase.include?(query) })
        @sensors.concat(end_device.sensors.select { |sensor| sensor.point.name.downcase.include?(query) })
      end
    end

    respond_to do |format|
      format.html
      format.json {
        @facilities = @facilities[0..4].map do |facility| 
          {
            name: facility.name, 
            url: facility_path(facility)
          }
        end

        @controllable_devices = @controllable_devices[0..4].map do |controllable_device|
          {
            name: controllable_device.point.name + ' | ' + controllable_device.point.end_device.facility.name, 
            url: facility_controllable_device_path(controllable_device.point.end_device.facility.id, controllable_device)
          }
        end

        @sensors = @sensors[0..4].map do |sensor|
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
