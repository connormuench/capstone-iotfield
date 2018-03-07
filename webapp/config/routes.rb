Rails.application.routes.draw do
  devise_for :users
  root to: 'facilities#index'
  get '/search', to: 'main#search', as: 'search'
  get '/visualization', to: 'main#visualization', as: 'visualization'
  get '/points', to: 'main#points', as: 'points'
  get '/admin_panel', to: 'main#admin_panel', as: 'admin_panel'

  get '/facilities/addable', to: 'facilities#addable_facilities'
  get '/facilities/:id/addable', to: 'facilities#addable_points'

  resources :users
  resources :facilities do
    resources :sensors, :controllable_devices
  end

  post '/users/:id/set_permissions', to: 'users#set_permissions', as: 'set_user_permissions'
  post '/facilities/:id/set_permissions', to: 'facilities#set_permissions', as: 'set_facility_permissions'

  mount ActionCable.server => '/cable'

  # For details on the DSL available within this file, see http://guides.rubyonrails.org/routing.html
end
