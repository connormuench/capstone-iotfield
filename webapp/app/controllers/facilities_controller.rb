class FacilitiesController < ApplicationController
  require 'pi_lists'
  require 'securerandom'

  before_action :set_facility, only: [:show, :edit, :update, :destroy, :addable_points]
  before_action only: [:create, :update, :destroy] { check_admin facilities_url }
  before_action :authenticate_user!

  # GET /facilities
  def index
    @facilities = current_user.facilities
    puts "Not accepted: #{PiLists.instance.not_accepted.size}"
  end

  # GET /facilities/1
  def show
    @controllable_devices = []
    @sensors = []

    @facility.end_devices.each do |end_device|
      @controllable_devices.concat(end_device.controllable_devices)
      @sensors.concat(end_device.sensors)
    end

    @access_level = current_user.access_levels.where(facility_id: @facility.id).first
  end

  # POST /facilities
  def create
    @facility = Facility.new(facility_params)
    pi_id = params[:facility][:pi_id]
    @facility.pi_id = pi_id
    @facility.network_address = PiLists.instance.not_accepted[pi_id][:ws].remote_ip
    PiLists.instance.accepted[pi_id] = PiLists.instance.not_accepted[pi_id]
    PiLists.instance.not_accepted.delete(pi_id)

    # Make all admins controllers of any new facility
    User.all.select { |user| user.is_admin }.each do |admin|
      @facility.access_levels.new(user_id: admin.id, level: 'Controller')
    end

    if @facility.save
      redirect_to @facility, notice: 'Facility was successfully created.'
    else
      render :new
    end
  end

  # PATCH/PUT /facilities/1
  def update
    if @facility.update(facility_params)
      redirect_to @facility, notice: 'Facility was successfully updated.'
    else
      render :edit
    end
  end

  # DELETE /facilities/1
  def destroy
    pi_id = @facility.pi_id
    @facility.destroy
    if PiLists.instance.accepted.key?(pi_id)
      PiLists.instance.not_accepted[pi_id] = PiLists.instance.accepted[pi_id]
      PiLists.instance.accepted.delete(pi_id)
    end

    redirect_to facilities_url, notice: 'Facility was successfully destroyed.'
  end

  # GET /facilities/addable
  def addable_facilities
    addable_facilities_list = []
    PiLists.instance.not_accepted.each_pair do |k, v|
      pi_hash = {id: k}
      pi_hash['name'] = v[:hs].headers_downcased['name'] if v[:hs].headers_downcased.key?('name')
      addable_facilities_list << pi_hash
    end
    render json: {facilities: addable_facilities_list}
  end

  # GET /facilities/1/addable
  def addable_points
    request_id = SecureRandom.hex(8)
    pi_lists = PiLists.instance
    pi_lists.accepted[@facility.pi_id][:ws].send({action: 'request-points', request_id: request_id}.to_json)
    while !pi_lists.points.key?(request_id)
      sleep(0.01)
    end
    points = pi_lists.points[request_id]
    puts points
    pi_lists.points.delete(request_id)
    render json: points
  end

  private
    def set_facility
      @facility = Facility.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through
    def facility_params
      params.require(:facility).permit(:name, :description, :location)
    end
end
