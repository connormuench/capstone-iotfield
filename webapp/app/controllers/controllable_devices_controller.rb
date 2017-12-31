class ControllableDevicesController < ApplicationController
  before_action :set_controllable_device, only: [:show, :update, :destroy]

  # GET /controllable_devices/1
  def show
  end

  # POST /controllable_devices
  def create
    @controllable_device = ControllableDevice.new

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
      point.pointable = @controllable_device

      if not point.save
        render :new
        raise ActiveRecord::Rollback
      end

      if facility.save
        if @controllable_device.save
          if params.key?(:rules_attributes)
            params[:rules_attributes].each do |rule|
              new_rule = @controllable_device.rules.new(rule_params(rule))
              if not new_rule.save
                render :new
                raise ActiveRecord::Rollback
              end
            end
          end

          redirect_to [facility, @controllable_device], notice: 'Sensor was successfully created.'
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

  # PATCH/PUT /controllable_devices/1
  def update
    if @controllable_device.update(controllable_device_params)
      redirect_to @controllable_device, notice: 'Controllable device was successfully updated.'
    else
      render :edit
    end
  end

  # DELETE /controllable_devices/1
  def destroy
    if @controllable_device.end_device.points == 1
      @controllable_device.end_device.destroy
    end

    @controllable_device.destroy
    redirect_to controllable_devices_url, notice: 'Controllable device was successfully destroyed.'
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_controllable_device
      @controllable_device = ControllableDevice.find(params[:id])
    end

    # Only allow a trusted parameter "white list" through.
    def point_params
      params.require(:point).permit(:name, :remote_id, :description, :location)
    end

    def rule_params(rule)
      rule.permit(:is_active, :expression, :action)
    end
end
