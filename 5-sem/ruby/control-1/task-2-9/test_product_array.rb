require 'minitest/autorun'
require_relative 'product'
require_relative 'product_array'

class TestProductArray < Minitest::Test
  def setup
    @product_array = ProductArray.new
    @product1 = Product.new(1, 'Product1', '123', 'Manufacturer1', 100, 30, 10)
    @product2 = Product.new(2, 'Product2', '456', 'Manufacturer2', 200, 60, 20)
    @product_array.add_product(@product1)
    @product_array.add_product(@product2)
  end

  def test_list_by_name
    assert_equal [@product1], @product_array.list_by_name('Product1')
    assert_equal [@product2], @product_array.list_by_name('Product2')
    assert_equal [], @product_array.list_by_name('Nonexistent')
  end

  def test_list_by_name_and_price
    assert_equal [@product1], @product_array.list_by_name_and_price('Product1', 150)
    assert_equal [], @product_array.list_by_name_and_price('Product1', 50)
    assert_equal [], @product_array.list_by_name_and_price('Nonexistent', 150)
  end

  def test_list_by_shelf_life
    assert_equal [@product2], @product_array.list_by_shelf_life(30)
    assert_equal [], @product_array.list_by_shelf_life(60)
  end
end
