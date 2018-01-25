class RemovePortNumberFromFacilities < ActiveRecord::Migration[5.1]
  def change
    remove_column :facilities, "network_port"
  end
end
