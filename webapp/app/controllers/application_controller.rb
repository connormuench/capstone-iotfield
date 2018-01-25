class ApplicationController < ActionController::Base
  protect_from_forgery with: :exception

  def check_admin(url)
    if !current_user.is_admin
      redirect_to(url)
    end
  end
end
