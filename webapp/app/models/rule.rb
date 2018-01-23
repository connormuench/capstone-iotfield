class Rule < ApplicationRecord
  belongs_to :controllable_device

  validates_presence_of :action
  validates_presence_of :expression
end
