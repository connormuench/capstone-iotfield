class Record < ApplicationRecord
  belongs_to :point

  validates_numericality_of :value
  validates_presence_of :unit
end
