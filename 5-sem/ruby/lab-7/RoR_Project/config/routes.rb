Rails.application.routes.draw do
  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Defines the root path route ("/")
  get "up" => "rails/health#show", as: :rails_health_check
  # Defines the root path route ("/")
  root "students#index"

  resources :students
end
