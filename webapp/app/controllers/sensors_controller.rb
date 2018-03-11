class SensorsController < PointsController
  require 'pi_lists'
  
  before_action :set_sensor, only: [:show, :update, :destroy]
  before_action :set_facility, only: [:show, :create, :update, :destroy]
  before_action :authenticate_user!
  before_action only: [:create, :update, :destroy] { check_admin(facility_url(Facility.find(params[:facility_id]))) }
  before_action only: [:update, :show] { authorize_user '/' }

  # GET /facilities/1/sensors/1
  def show
    records = @sensor.point.records
    @data = chart_data_from_points [@sensor.point]
    if records.count > 0
      @unit = records.first.unit
    else
      @unit = 'dimensionless'
    end
  end

  # POST /facilities/1/sensors
  def create
    @sensor = Sensor.new

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

      # Create a new point under the end device and assign the sensor to it
      point = found_end_device.points.new(point_params)
      point.remote_id = remote_id
      point.pointable = @sensor

      if point.save
        # Ensure the corresponding facility is connected before sending the 'add-point' command
        if PiLists.instance.accepted.key?(@facility.pi_id)
          PiLists.instance.accepted[@facility.pi_id][:ws].send({action: 'add-point', type: 'sensor', id: params[:remote_id]}.to_json)
        end
        redirect_to [@facility, @sensor], notice: 'Sensor was successfully created.'
      else
        render :new
        raise ActiveRecord::Rollback
      end
    end
  end

  # PATCH/PUT /facilities/1/sensors/1
  def update
    if @sensor.point.update(point_params)
      redirect_to [@facility, @sensor], notice: 'Sensor was successfully updated.'
    else
      render :edit
    end
  end

  # DELETE /facilities/1/sensors/1
  def destroy
    # Remove the associated end device if this point is its only associated point
    if @sensor.point.end_device.points.length == 1
      @sensor.point.end_device.destroy
    end

    # Ensure the corresponding facility is connected before sending the 'remove-point' command
    if PiLists.instance.accepted.key?(@facility.pi_id)
      remote_id = @sensor.point.end_device.address + ':' + @sensor.point.remote_id.to_s
      PiLists.instance.accepted[@facility.pi_id][:ws].send({action: 'remove-point', type: 'sensor', id: remote_id}.to_json)
    end

    @sensor.destroy
    redirect_to facility_url(@facility), notice: 'Sensor was successfully destroyed.'
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_sensor
      @sensor = Sensor.find(params[:id])
    end

    def set_facility
      @facility = Facility.find(params[:facility_id])
    end

    def point_params
      params.require(:point).permit(:name, :description, :location)
    end

    def authorize_user(url)
      current_user.access_levels.each do |access_level|
        if access_level.facility_id == @sensor.point.end_device.facility.id
          return
        end
      end
      redirect_to(url, alert: 'You are not authorized to access this page.')
    end
end
