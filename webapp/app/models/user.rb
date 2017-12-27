class User < ApplicationRecord
  # Include devise modules
  devise :database_authenticatable, :rememberable, :trackable

  has_many :access_levels, dependent: :destroy
  has_many :facilities, through: :access_levels

  validates_presence_of :username
  validates_presence_of :email
  validates_presence_of :name
end
