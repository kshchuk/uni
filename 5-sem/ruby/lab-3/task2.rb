def func1(x)
  ((x-2).abs / (x*x*Math.cos(x))) ** (1/7)
end

def func2(x)
  ((Math.tan(x+Math.exp(-x)))/Math.sin(x)**2) ** (-7/2)
end

def func3(x)
  1.0/(1.0+x/(1.0+x/(1.0+x)))
end
def func_if_impl(x)
  if -4 < x && x <= 0
    y = func1(x)
  elsif 0 < x && x <= 12
    y = func2(x)
  else
    y = func3(x)
  end
  y
end

def func_case_impl(x)

  case
    when -4 < x && x <= 0
    y = func1(x)
    when 0 < x && x <= 12
    y = func2(x)
    else
    y = func3(x)
  end
  y
end

x = 15
f = func_if_impl(x)
g = func_if_impl(x)
if (f-g).abs > 0.00001
  raise "F and G must return equal values"
end
puts "When x = #{x}, y = #{g} "