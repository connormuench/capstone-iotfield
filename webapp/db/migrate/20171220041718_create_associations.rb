class CreateAssociations < ActiveRecord::Migration[5.1]
  def change
    change_table :access_levels do |t|
      t.belongs_to :user, index: true
      t.belongs_to :facility, index: true
    end

    change_column :facilities, :description, :text
    
    change_table :end_devices do |t|
      t.belongs_to :facility, index: true
    end

    change_table :points do |t|
      t.belongs_to :end_device, index: true
      t.references :pointable, polymorphic: true, index: true
    end
    
    change_table :records do |t|
      t.belongs_to :point, index: true
    end
    
    change_table :active_rules do |t|
      t.belongs_to :controllable_device, index: true
    end
    
    change_table :rules do |t|
      t.belongs_to :controllable_device, index: true
    end
    
  end
end
