class UsersController < ApplicationController


   before_action :set_user, only: [:show, :update, :destroy]

   # GET /facilities/1/sensors/1
  def show
    
  end


  def create
    @user = User.new
    @user.id=params[:id]
    @user.username=params[:username]
    @user.email=params[:email]
    @user.is_admin=params[:is_admin]
    @user.name=params[:name]
    @user.save

  end


  # PATCH/PUT /facilities/1/sensors/1
  def update
    @user.id=params[:id]
    @user.username=params[:username]
    @user.email=params[:email]
    @user.is_admin=params[:is_admin]
    @user.name=params[:name]
    @user.save
  end





  def destroy
    #get rid of permissions

  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_user
      @user = User.find(params[:id])
    end

    def point_params
      params.require(:point).permit(:name, :description, :location)
    end
end