#file: product.rb
require_relative 'product'

#file: product_array.rb
require_relative 'product_array'

product_array = ProductArray.new

loop do
  puts "1. Add product"
  puts "2. List by name"
  puts "3. List by name and price"
  puts "4. List by shelf life"
  puts "5. Exit"
  
  choice = gets.chomp.to_i
  
  case choice
  when 1
    puts "Enter product details (id, name, upc, manufacturer, price, shelf life, quantity):"
    details = gets.chomp.split(',')
    product_array.add_product(Product.new(*details.map(&:strip)))
  
  when 2
    puts "Enter product name:"
    name = gets.chomp.strip
    puts "Products:"
    puts product_array.list_by_name(name).map(&:to_s)
  
  when 3
    puts "Enter product name and maximum price:"
    name, price = gets.chomp.split(',').map(&:strip)
    puts "Products:"
    puts product_array.list_by_name_and_price(name, price.to_i).map(&:to_s)
  
  when 4
    puts "Enter minimum shelf life:"
    shelf_life = gets.chomp.to_i
    puts "Products:"
    puts product_array.list_by_shelf_life(shelf_life).map(&:to_s)
  
  when 5
    break
  
  else
    puts "Invalid choice. Please try again."
  
  end
  
end