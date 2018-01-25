class ApplicationController < ActionController::Base
  protect_from_forgery with: :exception

  # Check if the current user is an administrator
  def check_admin(url)
    if !current_user.is_admin
      redirect_to(url, alert: 'You need administrator privileges to perform that task.')
    end
  end
end
