class RemoveActiveRule < ActiveRecord::Migration[5.1]
  def change
    drop_table :active_rules
    add_column :rules, :is_active, :boolean
  end
end
