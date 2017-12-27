class CreateControllableDevices < ActiveRecord::Migration[5.1]
  def change
    create_table :controllable_devices do |t|
      t.string :mode
      t.string :status

      t.timestamps
    end
  end
end
