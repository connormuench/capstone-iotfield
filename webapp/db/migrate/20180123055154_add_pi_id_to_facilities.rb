class AddPiIdToFacilities < ActiveRecord::Migration[5.1]
  def change
    add_column :facilities, 'pi_id', :string
  end
end
