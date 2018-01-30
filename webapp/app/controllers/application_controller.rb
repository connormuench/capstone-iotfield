class ApplicationController < ActionController::Base
  protect_from_forgery with: :exception

  # Check if the current user is an administrator
  def check_admin(url)
    if !current_user.is_admin
      redirect_to(url, alert: 'You need administrator privileges to perform that task.')
    end
  end

  def chart_data_from_points(points)
    data = []
    points.each do |point|
      series = {id: point.id, name: point.name}
      series_data = []
      point.records.each do |record|
        series_data.push([record.created_at, record.value])
      end
      series[:data] = series_data
      data.push(series)
    end
    return data
  end
end
