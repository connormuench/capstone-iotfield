class Record < ApplicationRecord
  belongs_to :point

  validates_numericality_of :value
  validates_presence_of :unit

  def save_and_broadcast
    puts('debug13')
    if self.save
    puts('debug14')
      data = {created_at: self.created_at, value: self.value, point_id: self.point.id}
      PointsChannel.broadcast_to(self.point, self)
    puts('debug15')
    end
  end
end
