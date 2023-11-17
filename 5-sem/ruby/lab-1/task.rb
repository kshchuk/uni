

#Variant 12
def calculate(a, b, x)
  n1 = 6.2 * 10 ** 2.7 + Math.tan(Math::PI - x ** 3)
  n2 = Math.exp(x/a) + Math.log((b*b).abs)
  n3 = Math.atan(1000 * Math.sqrt(a) / (2*x - b))
  n1 / n2 + n3
end

