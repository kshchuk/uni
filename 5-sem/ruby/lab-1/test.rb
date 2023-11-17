require 'minitest/autorun'

require "minitest/spec"
require_relative "task"
def comp_float(f1, f2)
  (f1 - f2).abs < 0.00001
end
class TestCalculateFunction < MiniTest::Test
  def test_calculate
    assert comp_float(calculate(1,1,1), 1144.1310305)
    assert comp_float(calculate(1,1,2), 423.02359776)
    assert comp_float(calculate(3,0,0), 1.57079632679)
    assert comp_float(calculate(1,0.02,2), -7157.58900444)
    assert_raises(ZeroDivisionError) do
      calculate(0, 0, 0)
    end
  end
end