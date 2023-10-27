require 'minitest/autorun'
require_relative 'function'

class TestFunction < Minitest::Test
  def setup
    @function = Function.new(1, 2, 3, 0, 10, 1)
  end

  def test_calculate_function_a_less_than_zero_and_x_not_zero
    @function.a = -1
    assert_equal 3, @function.calculate_function(1)
  end

  def test_calculate_function_else_condition
    assert_equal 1, @function.calculate_function(1)
  end

  def test_check_params_false
    assert_equal false, @function.check_params(4, 3, 2)
  end

  def test_calculate_function_with_negative_x
    @function.a = -1
    assert_equal -12, @function.calculate_function(-2)
  end

  def test_calculate_function_with_zero_a_and_non_zero_x
    @function.a = 0
    assert_equal 1, @function.calculate_function(2)
  end

  def test_check_params_with_negative_values
    assert_equal false, @function.check_params(-4, -3, -2)
  end

  def test_check_params_with_zero_values
    assert_equal false, @function.check_params(0, 0, 0)
  end

end
