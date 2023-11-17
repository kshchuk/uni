require_relative 'task'

print("A:")
a = gets.chomp.to_i
print("B:")
b = gets.chomp.to_i
print("X:")
x = gets.chomp.to_i

unless a.is_a? Integer
  raise "A has to be an integer"
end
unless b.is_a? Integer
  raise "B has to be an integer"
end

unless x.is_a? Integer
  raise "X has to be an integer"
end

puts "L = #{calculate(a, b, x)}"