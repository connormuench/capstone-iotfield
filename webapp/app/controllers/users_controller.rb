class UsersController < ApplicationController


   # GET /facilities/1/sensors/1
  def show
    @user = User.find(params[:id])
  end


  def create
    @user = User.new
  end


  # PATCH/PUT /facilities/1/sensors/1
  def update

  end





  def destroy
    #get rid of permissions
  end

  private
    # Use callbacks to share common setup or constraints between actions.


    def point_params
      params.require(:point).permit(:name, :description, :location)
    end
end