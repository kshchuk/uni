#logic predicates
def predicate_a(a, b)
  !(a || b) && (a && !b)
end

def predicate_b(a, b, c, x, y, z)
  z != y <= (6 >= y) && a || b && c && x >= 1.5
end

def predicate_c(x, y, z)
  (8 - x * 2 <= z) && (x*x <=> y*y) || (z >= 15)
end

def predicate_d(x,y,z)
  x > 0 && y < 0 || z >= (x*y + (-y/x)) - (-z)*2
end

def predicate_e(a,b,c)
  !(a || b && !(c || (!a || b)))
end

def predicate_f(x,y)
  x*x+y*y >= 1 && x >= 0 && y >= 0
end

def predicate_g(a,b,c)
  (a && (c && b <=> b || a) || c) && b
end

def predicate_h(x, p)
  ((Math.log(x) / Math.log(1/3) > Math.log(0.7)/Math.log(1/3))) and (Math.sqrt(x) > x*x) && !p
end


a = false
b = true
c = true
x = -24
y = 4
z = 8
x1 = 3
p = true

puts("A: #{predicate_a(a,b)}")
begin
  predicate_b(a,b,c,x,y,z)
rescue
  puts("B cannot be calculated due to invalid comparison: z != y <= (6 >= y)")
end
puts("C: #{predicate_c(x,y,z)}")
puts("D: #{predicate_d(x,y,z)}")
puts("E: #{predicate_e(a,b,c)}")
puts("F: #{predicate_f(x,y)}")
puts("G: #{predicate_g(a,b,c)}")
puts("H: #{predicate_h(x1,p)}")