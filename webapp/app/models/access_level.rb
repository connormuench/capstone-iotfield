class AccessLevel < ApplicationRecord
  belongs_to :user
  belongs_to :facility

  validates_presence_of :level
end
