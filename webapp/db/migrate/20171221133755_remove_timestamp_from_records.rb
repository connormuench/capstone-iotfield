class RemoveTimestampFromRecords < ActiveRecord::Migration[5.1]
  def change
    remove_column :records, :timestamp
  end
end
