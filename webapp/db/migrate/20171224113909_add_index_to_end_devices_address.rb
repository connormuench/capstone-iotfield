class AddIndexToEndDevicesAddress < ActiveRecord::Migration[5.1]
  def change
    add_index :end_devices, :address
  end
end
