class CreateActiveRuleRuleAssociation < ActiveRecord::Migration[5.1]
  def change
    change_table :active_rules do |t|
      t.belongs_to :rule, index: true
    end
  end
end
