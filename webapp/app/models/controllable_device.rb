class ControllableDevice < ApplicationRecord
  has_one :point, as: :pointable, dependent: :destroy
  has_many :rules, dependent: :destroy

  accepts_nested_attributes_for :rules, :point
end
