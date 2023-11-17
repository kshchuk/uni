def to_binary(num)
  binary = ""
  if num == 0
    return "0"
  end
  until num == 0
    if num % 2 == 0
      binary = '0' + binary
    else
      binary = '1' + binary
    end
    num = num >> 1
  end
  binary
end


input = 192
binary = to_binary(input)
puts("Number #{input} is #{binary} in binary form")