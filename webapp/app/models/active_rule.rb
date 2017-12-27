class ActiveRule < ApplicationRecord
  belongs_to :rule
  belongs_to :controllable_device
end
