class PointsChannel < ApplicationCable::Channel
  def subscribed
    puts params[:point_id]
    point = Point.find(params[:point_id])
    stream_for(point) if current_user.facilities.include? point.end_device.facility
  end

  def unsubscribed
    # Any cleanup needed when channel is unsubscribed
  end
end
