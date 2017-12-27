class Sensor < ApplicationRecord
  has_one :point, as: :pointable, dependent: :destroy

  accepts_nested_attributes_for :point
end
