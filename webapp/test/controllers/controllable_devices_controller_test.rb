require 'test_helper'

class ControllableDevicesControllerTest < ActionDispatch::IntegrationTest
  setup do
    @controllable_device = controllable_devices(:one)
  end

  test "should get index" do
    get controllable_devices_url
    assert_response :success
  end

  test "should get new" do
    get new_controllable_device_url
    assert_response :success
  end

  test "should create controllable_device" do
    assert_difference('ControllableDevice.count') do
      post controllable_devices_url, params: { controllable_device: {  } }
    end

    assert_redirected_to controllable_device_url(ControllableDevice.last)
  end

  test "should show controllable_device" do
    get controllable_device_url(@controllable_device)
    assert_response :success
  end

  test "should get edit" do
    get edit_controllable_device_url(@controllable_device)
    assert_response :success
  end

  test "should update controllable_device" do
    patch controllable_device_url(@controllable_device), params: { controllable_device: {  } }
    assert_redirected_to controllable_device_url(@controllable_device)
  end

  test "should destroy controllable_device" do
    assert_difference('ControllableDevice.count', -1) do
      delete controllable_device_url(@controllable_device)
    end

    assert_redirected_to controllable_devices_url
  end
end
