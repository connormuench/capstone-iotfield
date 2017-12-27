class CreateFacilities < ActiveRecord::Migration[5.1]
  def change
    create_table :facilities do |t|
      t.string :network_address
      t.string :name
      t.string :description
      t.string :location
      t.integer :network_port

      t.timestamps
    end
  end
end
