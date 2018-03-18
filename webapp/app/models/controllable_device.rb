class ControllableDevice < ApplicationRecord
  has_one :point, as: :pointable, dependent: :destroy
  has_many :rules, dependent: :destroy

  accepts_nested_attributes_for :rules, :point

  before_validation :init

  # Initialize mode and status to default values
  def init
    if !self.mode
  	  self.mode = "Manual"
    end
    if !self.status
  	  self.status = "Off"
    end
  end
end
