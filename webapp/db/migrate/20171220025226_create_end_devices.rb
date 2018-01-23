class CreateEndDevices < ActiveRecord::Migration[5.1]
  def change
    create_table :end_devices do |t|
      t.string :address

      t.timestamps
    end
  end
end
