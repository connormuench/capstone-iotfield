class CreateActiveRules < ActiveRecord::Migration[5.1]
  def change
    create_table :active_rules do |t|

      t.timestamps
    end
  end
end
