class Facility < ApplicationRecord
  has_many :access_levels, dependent: :destroy
  has_many :end_devices, dependent: :destroy
  has_many :points, through: :end_devices

  validates_presence_of :network_address
  validates_presence_of :name
end
