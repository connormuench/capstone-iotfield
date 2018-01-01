class ControllableDevice < ApplicationRecord
  has_one :point, as: :pointable, dependent: :destroy
  has_many :rules, dependent: :destroy

  accepts_nested_attributes_for :rules, :point

  after_initialize :init

  # Initialize mode and status to default values
  def init
  	self.mode = "Manual"
  	self.status = "Off"
  end
end
