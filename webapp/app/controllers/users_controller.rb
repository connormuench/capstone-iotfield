class UsersController < ApplicationController


  before_action :set_user, only: [:show, :update, :destroy, :set_permissions]
  before_action :authenticate_user!
  before_action only: [:create, :destroy, :set_permissions] { check_admin '/' }
  before_action only: [:update, :show] { authorize_user '/' }

   # GET /users/1
  def show
  end

  def create
    if params[:user][:password] != params[:user][:password_confirmation] || params[:user][:password] == ''
      return
    end
    @user = User.new(user_params)
    @user.password = params[:password]
    @user.password_confirmation = params[:password_confirmation] 
    if @user.save
      redirect_to @user, notice: 'User was successfully created.'
    end

  end

  # PATCH/PUT /users/1
  def update
    if params[:user][:password] == params[:user][:password_confirmation] && params[:user][:password] != ''
      @user.password = params[:user][:password]
      @user.password_confirmation = params[:user][:password_confirmation]
    elsif params[:user][:password] != params[:user][:password_confirmation]
      flash.now[:alert] = 'The passwords did not match.'
      render :show
      return
    end

    if @user.update(user_params)
      redirect_to @user, notice: 'User was successfully updated.'
    else
      flash.now[:alert] = 'There was an error updating the user.'
      render :show
    end
  end

  # DELETE /users/1
  def destroy
    @user.destroy
    redirect_to admin_panel_path, notice: 'User was successfully destroyed.'
  end

  def set_permissions
    facilities = params[:facility]

    access_levels =  {}
    @user.access_levels.each do |access_level|
      access_levels[access_level.facility_id] = access_level
    end

    facilities.each do |facility_s, access_level|
      facility = facility_s.to_i
      if access_level.downcase == 'none' && access_levels.include?(facility)
        access_levels[facility].destroy
      elsif access_levels.include?(facility)
        access_levels[facility].level = access_level.titleize
      elsif access_level.downcase != 'none' && !access_levels.include?(facility)
        @user.access_levels.create(facility_id: facility, level: access_level.titleize)
      end
    end

    redirect_to admin_panel_path, notice: 'User permissions were successfully updated.'
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_user
      @user = User.find(params[:id])
    end

    def user_params
      params.require(:user).permit(:name, :email, :is_admin, :username)
    end

    def authorize_user(url)
      if !(current_user.is_admin || current_user.id == @user.id)
        redirect_to(url, alert: 'You are not authorized to access this page.')
      end
    end
end