

def calc_term
  lambda do |x, i|
    x ** i * Math.cos(Math::PI * i / 3.0) / i.to_f
  end
end

def calc_sum(series, x, n)
  sum = 0
  (1..n).each do |i|
    sum += series.call(x, i)
  end
  sum
end
def calc_sum_inf(series, x, eps)
  sum = 0
  i = 1
  loop do
    prev = sum
    sum += series.call(x, i)
    break if (sum - prev).abs < eps
    i += 1
  end
  sum
end


print"Enter X value [0.1, 0.8]:\n>"
x = gets.chomp.to_f

if x < 0.1 || x > 0.8
  raise ArgumentError, "X is not in specified range"
end

print"Enter N value [18, 58] for limited sum, otherwise it will be calculated for eps=0.001:\n>"
n = gets.chomp.to_i

if n < 18 || n > 58
  puts calc_sum_inf(calc_term,x,0.001)
else
  puts calc_sum(calc_term,x,n)
end





