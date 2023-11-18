require 'minitest/autorun'

def integral_rect(func, a, b, eps)
  n = 1.0 / eps
  h = (b - a).to_f / n
  res = 0
  (a+h/2.0).step(b,h) do|x|
    res += func.call(x)
  end
  h * res
end

def integral_trapezoid(func, a, b, eps)
  n = 1.0 / eps
  h = (b - a).to_f / n
  res = func.call(a) / 2
  (a+h).step(b-h,h) do|x|
    res += func.call(x)
  end
  res += func.call(b) / 2
  h * res
end

def func1
  lambda do |x|
    Math.sqrt(2 ** x - 1)
  end
end
def func2
  lambda do |x|
    1.0 / (1 + Math.sqrt(2 * x))
  end
end

def compare_doubles(a, b)
  (a - b).abs < 0.00001
end

puts "F1_rect = #{integral_rect(func1, 0.2, 1.0, 0.0001)}"
puts "F1_trap = #{integral_trapezoid(func1, 0.2, 1.0, 0.0001)}"

puts "F2_rect = #{integral_rect(func2, 0.2, 1.0, 0.0001)}"
puts "F2_trap = #{integral_trapezoid(func2, 0.2, 1.0, 0.0001)}"


class TestIntegral < MiniTest::Test
  def test_integral
    assert compare_doubles(integral_rect(func1, 0.2, 1.0, 0.0001), 0.5685120833170007)
    assert compare_doubles(integral_trapezoid(func1, 0.2, 1.0, 0.0001), 0.5685120833170007)
    assert compare_doubles(integral_rect(func2, 0.2, 1.0, 0.0001), 0.390469785934285)
    assert compare_doubles(integral_trapezoid(func2, 0.2, 1.0, 0.0001), 0.390469785934285)
  end
end