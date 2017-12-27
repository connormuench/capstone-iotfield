class FacilitiesController < ApplicationController
  before_action :set_facility, only: [:show, :edit, :update, :destroy]
  before_action :authenticate_user!

  # GET /facilities
  # GET /facilities.json
  def index
    @facilities = Facility.all
  end

  # GET /facilities/1
  def show
  end

  # POST /facilities
  def create
    @facility = Facility.new(facility_params)

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
    @facility.destroy

    redirect_to facilities_url, notice: 'Facility was successfully destroyed.'
    head :no_content
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_facility
      @facility = Facility.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def facility_params
      params.require(:facility).permit(:name, :description, :location, :network_port, :network_address)
    end
end
