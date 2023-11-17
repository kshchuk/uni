def factorial(num)
  (1..(num.zero? ? 1:num)).inject(:*)
end


def do_until_eps(exec, initial, eps)
  sum = 0
  n = initial
  begin
    m = exec.call(n)
    n += 1
    prev = sum
    sum += m
  end until (sum - prev).abs < eps
  sum
end

def calculate_series(eps)
  lambda = lambda { |n|
    (factorial(n-1).to_f/factorial(n+1)) ** (n*(n+1))
  }
  do_until_eps(lambda, 2, eps)
end
def calculate_series2(eps)
  lambda = lambda { |n|
    factorial(4*n).to_f * factorial(2*n-1) / ((factorial(4*n+1) * (4 ** (2*n)) * factorial(2*n)))
  }
  do_until_eps(lambda, 1, eps)
end

def calculate_pi_quot(eps)
  lambda = lambda { |n|
    sign = n.odd? ? 1 : -1
    sign * 1.0 / (2 * n - 1)
  }
  do_until_eps(lambda, 1, eps)
end

pi_q = Math::PI / 4


puts "Series 1 = #{calculate_series(0.00001)}"
puts "Series 2 = #{calculate_series2(0.00001)}"
puts "PI / 4 (actual) = #{calculate_pi_quot(0.00001)}"
puts "PI / 4 (expected) = #{pi_q}"
