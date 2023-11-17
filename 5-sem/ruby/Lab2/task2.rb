
#calculate max number, which can be represented using t+1 digits, where r - the integer part of number (mod P)
def range_calculator(p, t, r)
  (p ** r) * (1.0 - p ** (-t))
end


p = 5
t = 8
r = 0
range = range_calculator(5, 8, 0)

puts "For p = #{p}, t = #{t}, r = #{r} range is [0, #{range}]"