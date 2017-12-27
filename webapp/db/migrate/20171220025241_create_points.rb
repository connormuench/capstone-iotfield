class CreatePoints < ActiveRecord::Migration[5.1]
  def change
    create_table :points do |t|
      t.integer :remote_id
      t.string :name
      t.text :description
      t.string :location

      t.timestamps
    end
  end
end
