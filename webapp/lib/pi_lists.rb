require 'singleton'
require 'concurrent'

class PiLists
  include Singleton

  attr_accessor :accepted, :not_accepted, :points

  def initialize()
    @accepted = Concurrent::Hash.new
    @not_accepted = Concurrent::Hash.new
    @points = Concurrent::Hash.new
  end
end