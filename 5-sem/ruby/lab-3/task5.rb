

def calculate_y(x, n, c)
  n1 = (1.0 + x + x*x) / (2*x + x ** 1/(n-c))
  n2 = (1.0-x+x*x) / (2*x - x*x)
  n3 = 5 - 2 * x * x
  1.0 / (2 + n1 + n2) * n3
end

def calculate_z(x)
  n1 = Math.sin(2*x) ** 2
  n2 = Math.cos(Math::PI/3 - 2*x) * Math.sin(2*x - Math::PI/6)
  n3 = (1 / Math.tan((Math::PI + x) / (x + 1.0))) ** (2.0/x)
  n1 - n2 - n3
end

def tabulate_y(n, c)
  puts "Y"
  st = 1.0/(n+c)
  1.step(n, st) do |x|
    puts "y(#{x}) = #{calculate_y(x,n,c)}"
  end
end

def tabulate_z(n, c)
  puts "Z"
  st = 1.0 / ((3.0/2.0) * n + c)

  (Math::PI/n).step(Math::PI, st) do |x|
    puts "z(#{x}) = #{calculate_z(x)}"
  end
end

def tabulate_f(n, c)
  puts "F"
  st = 0.5 / n

  2.step(c, st) do |x|
    if x < n
      puts "f -> y(#{x}) = #{calculate_y(x,n,c)}"
    else
      puts "f -> z(#{x}) = #{calculate_z(x)}"
    end
  end
end


tabulate_y(5,10)
tabulate_z(5,10)
tabulate_f(5,10)
