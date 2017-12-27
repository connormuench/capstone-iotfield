class SensorsController < ApplicationController
  before_action :set_sensor, only: [:show, :update, :destroy]

  # GET facilities/1/sensors/1
  def show
  end

  # POST facilities/1/sensors
  def create
    @sensor = Sensor.new
    facility = Facility.find(params[:facility_id])

    address = params[:address]
    end_devices = facility.end_devices
    found_end_device = nil

    end_devices.each do |end_device|
      if end_device.address == address
        found_end_device = end_device
        break
      end
    end

    ActiveRecord::Base.transaction do
      if found_end_device.nil?
        found_end_device = facility.end_devices.new(address: address)
        if not found_end_device.save
          render :new
        end
      end

      point = found_end_device.points.new(point_params)
      point.pointable = @sensor

      if not point.save
        render :new
        raise ActiveRecord::Rollback
      end

      if facility.save
        if @sensor.save
          redirect_to [facility, @sensor], notice: 'Sensor was successfully created.'
        else
          render :new
          raise ActiveRecord::Rollback
        end
      else
        render :new
        raise ActiveRecord::Rollback
      end
    end
  end

  # PATCH/PUT facilities/1/sensors/1
  def update
    if @sensor.update(sensor_params)
      redirect_to @sensor, notice: 'Sensor was successfully updated.'
    else
      render :edit
    end
  end

  # DELETE facilities/1/sensors/1
  def destroy
    @sensor.destroy
    redirect_to sensors_url, notice: 'Sensor was successfully destroyed.'
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_sensor
      @sensor = Sensor.find(params[:id])
    end

    def point_params
      params.require(:point).permit(:name, :remote_id, :description, :location)
    end
end
