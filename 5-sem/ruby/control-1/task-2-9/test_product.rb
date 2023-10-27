require 'minitest/autorun'
require_relative 'product'

class TestProduct < Minitest::Test
  def setup
    @product = Product.new(1, 'Product1', '123', 'Manufacturer1', 100, 30, 10)
  end

  def test_id
    assert_equal 1, @product.get_id
    @product.set_id(2)
    assert_equal 2, @product.get_id
  end

  def test_name
    assert_equal 'Product1', @product.get_name
    @product.set_name('Product2')
    assert_equal 'Product2', @product.get_name
  end

  def test_upc
    assert_equal '123', @product.get_upc
    @product.set_upc('456')
    assert_equal '456', @product.get_upc
  end

  def test_manufacturer
    assert_equal 'Manufacturer1', @product.get_manufacturer
    @product.set_manufacturer('Manufacturer2')
    assert_equal 'Manufacturer2', @product.get_manufacturer
  end

  def test_price
    assert_equal 100, @product.get_price
    @product.set_price(200)
    assert_equal 200, @product.get_price
  end

  def test_shelf_life
    assert_equal 30, @product.get_shelf_life
    @product.set_shelf_life(60)
    assert_equal 60, @product.get_shelf_life
  end

  def test_quantity
    assert_equal 10, @product.get_quantity
    @product.set_quantity(20)
    assert_equal 20, @product.get_quantity
  end

  def test_to_string
    expected_string = "ID: #{@product.id}, Name: #{@product.name}, UPC: #{@product.upc}, Manufacturer: #{@product.manufacturer}, Price: #{@product.price}, Shelf Life: #{@product.shelf_life}, Quantity: #{@product.quantity}"
    assert_equal expected_string, @product.toString
  end
end
