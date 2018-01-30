class ControllableDevicesController < PointsController
  require 'pi_lists'

  before_action :set_controllable_device, only: [:show, :update, :destroy]
  before_action :set_facility, only: [:show, :create, :update, :destroy]
  before_action :authenticate_user!
  before_action only: [:create, :update, :destroy] { check_admin(facility_url(Facility.find(params[:facility_id]))) }

  # GET /facilities/1/controllable_devices/1
  def show
    records = @controllable_device.point.records
    @data = records_to_hash records
    if records.count > 0
      @unit = @sensor.point.records.first.unit
    end
  end

  # POST /facilities/1/controllable_devices
  def create
    @controllable_device = ControllableDevice.new

    id_split = params[:remote_id].split(':')
    address = id_split[0]
    remote_id = id_split[1]
    end_devices = @facility.end_devices
    found_end_device = nil

    # See if the end device already exists in the database
    end_devices.each do |end_device|
      if end_device.address == address
        found_end_device = end_device
        break
      end
    end

    # Establish a rollback point in case anything fails to save
    ActiveRecord::Base.transaction do
      # Create a new end device if an existing one wasn't found
      if found_end_device.nil?
        found_end_device = @facility.end_devices.new(address: address)
        if not found_end_device.save
          render :new
        end
      end

      # Create a new point under the end device and assign the controllable device to it
      point = found_end_device.points.new(point_params)
      point.remote_id = remote_id
      point.pointable = @controllable_device

      if not point.save
        render :new
        raise ActiveRecord::Rollback
      end

      # Add any rules that came with the request
      if params.key?(:rules_attributes)
        params[:rules_attributes].each do |rule|
          new_rule = @controllable_device.rules.new(rule_params(rule))
          if not new_rule.save
            render :new
            raise ActiveRecord::Rollback
          end
        end
      end

      # Ensure the corresponding facility is connected before sending the 'add-point' command
      if PiLists.instance.accepted.key?(@facility.pi_id)
        PiLists.instance.accepted[@facility.pi_id][:ws].send({action: 'add-point', type: 'controllable_device', id: params[:remote_id]}.to_json)
      end

      # No failures if we got to this point, show the controllable device's page
      redirect_to [@facility, @controllable_device], notice: 'Controllable device was successfully created.'
    end
  end

  # PATCH/PUT /facilities/1/controllable_devices/1
  def update
    if @controllable_device.point.update(point_params)
      redirect_to [@facility, @controllable_device], notice: 'Controllable device was successfully updated.'
    else
      render :edit
    end
  end

  # DELETE /facilities/1/controllable_devices/1
  def destroy
    # Remove the associated end device if this point is its only associated point
    if @controllable_device.point.end_device.points.length == 1
      @controllable_device.point.end_device.destroy
    end

    # Ensure the corresponding facility is connected before sending the 'remove-point' command
    if PiLists.instance.accepted.key?(@facility.pi_id)
      remote_id = @controllable_device.point.end_device.address + ':' + @controllable_device.point.remote_id.to_s
      PiLists.instance.accepted[@facility.pi_id][:ws].send({action: 'remove-point', type: 'controllable_device', id: remote_id}.to_json)
    end

    @controllable_device.destroy
    redirect_to facility_url(@facility), notice: 'Controllable device was successfully destroyed.'
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_controllable_device
      @controllable_device = ControllableDevice.find(params[:id])
    end

    def set_facility
      @facility = Facility.find(params[:facility_id])
    end

    # Only allow a trusted parameter "white list" through
    def point_params
      params.require(:point).permit(:name, :description, :location)
    end

    def rule_params(rule)
      rule.permit(:is_active, :expression, :action)
    end
end
