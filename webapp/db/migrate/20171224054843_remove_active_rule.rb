class RemoveActiveRule < ActiveRecord::Migration[5.1]
  def change
    add_column :rules, :is_active, :boolean
  end
end