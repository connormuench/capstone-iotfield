class Point < ApplicationRecord
  belongs_to :end_device
  belongs_to :pointable, polymorphic: true
  has_many :records, dependent: :destroy

  validates_presence_of :name
  validates_presence_of :remote_id
end
