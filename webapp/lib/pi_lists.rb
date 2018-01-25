require 'singleton'
require 'concurrent'

class PiLists
  include Singleton

  attr_accessor :accepted, :not_accepted, :points

  def initialize()
    @accepted = Concurrent::Map.new
    @not_accepted = Concurrent::Map.new
    @points = Concurrent::Map.new
  end
end