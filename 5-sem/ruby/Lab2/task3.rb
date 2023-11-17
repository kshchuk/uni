
def from_binary(b_string)
  i = 1
  res = 0
  b_string.reverse.each_char do |char|
    res += i if char == '1'
    i = i << 1
  end
  res
end

input = "10001001001001"
number = from_binary(input)

puts("Binary number #{input} is #{number} in decimal")