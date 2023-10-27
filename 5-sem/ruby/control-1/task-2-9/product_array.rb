#file: product.rb
require_relative 'product'

class ProductArray
    def initialize
      @products = []
    end
  
    def add_product(product)
      @products << product
    end
  
    def list_by_name(name)
      @products.select { |product| product.name == name }
    end
  
    def list_by_name_and_price(name, price)
      @products.select { |product| product.name == name && product.price <= price }
    end
  
    def list_by_shelf_life(shelf_life)
      @products.select { |product| product.shelf_life > shelf_life }
    end
  end