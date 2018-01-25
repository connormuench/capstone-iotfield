# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema.define(version: 20171224113909) do

  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "access_levels", force: :cascade do |t|
    t.string "level"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "user_id"
    t.bigint "facility_id"
    t.index ["facility_id"], name: "index_access_levels_on_facility_id"
    t.index ["user_id"], name: "index_access_levels_on_user_id"
  end

  create_table "controllable_devices", force: :cascade do |t|
    t.string "mode"
    t.string "status"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "end_devices", force: :cascade do |t|
    t.string "address"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "facility_id"
    t.index ["address"], name: "index_end_devices_on_address"
    t.index ["facility_id"], name: "index_end_devices_on_facility_id"
  end

  create_table "facilities", force: :cascade do |t|
    t.string "network_address"
    t.string "name"
    t.text "description"
    t.string "location"
    t.integer "network_port"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "points", force: :cascade do |t|
    t.integer "remote_id"
    t.string "name"
    t.text "description"
    t.string "location"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "end_device_id"
    t.string "pointable_type"
    t.bigint "pointable_id"
    t.index ["end_device_id"], name: "index_points_on_end_device_id"
    t.index ["pointable_type", "pointable_id"], name: "index_points_on_pointable_type_and_pointable_id"
  end

  create_table "records", force: :cascade do |t|
    t.decimal "value"
    t.string "unit"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "point_id"
    t.index ["point_id"], name: "index_records_on_point_id"
  end

  create_table "rules", force: :cascade do |t|
    t.string "expression"
    t.string "action"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "controllable_device_id"
    t.index ["controllable_device_id"], name: "index_rules_on_controllable_device_id"
  end

  create_table "sensors", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "users", force: :cascade do |t|
    t.string "username", default: "", null: false
    t.string "email", default: "", null: false
    t.string "encrypted_password", default: "", null: false
    t.boolean "is_admin", default: false
    t.string "name", default: ""
    t.datetime "remember_created_at"
    t.integer "sign_in_count", default: 0, null: false
    t.datetime "current_sign_in_at"
    t.datetime "last_sign_in_at"
    t.inet "current_sign_in_ip"
    t.inet "last_sign_in_ip"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["username"], name: "index_users_on_username"
  end

end
