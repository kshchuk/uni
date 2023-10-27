#file: function.rb
require_relative 'function'

  puts "Enter a, b, c, X start, X end and dX (in column):"
  a = gets.chomp.to_f
  b = gets.chomp.to_f
  c = gets.chomp.to_f
  x_start = gets.chomp.to_f
  x_end = gets.chomp.to_f
  dx = gets.chomp.to_f
  
  function = Function.new(a, b, c, x_start, x_end, dx)
  function.calculate
  