class EndDevice < ApplicationRecord
  belongs_to :facility
  has_many :points, dependent: :destroy
  has_many :sensors, through: :points, source: :pointable, source_type: 'Sensor'
  has_many :controllable_devices, through: :points, source: :pointable, source_type: 'ControllableDevice'

  validates_presence_of :address
end
