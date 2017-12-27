class CreateRecords < ActiveRecord::Migration[5.1]
  def change
    create_table :records do |t|
      t.decimal :value
      t.string :unit
      t.timestamp :timestamp

      t.timestamps
    end
  end
end
