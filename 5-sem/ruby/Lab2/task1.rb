
class Point
  attr_accessor :x
  attr_accessor :y
  def initialize(x, y)
    @x = x
    @y = y
  end
end

def calc_trapezoid_square(point1, point2)
  ((point1.x + point2.x) * (point1.y - point2.y)).abs
end
def calculate_square(points)
  sum = 0
  if points.length < 3
    return sum
  end
  n = points.length
  (0...n-1).each do |i|
    sum += calc_trapezoid_square(points[i], points[i + 1])
  end
  sum += calc_trapezoid_square(points[n-1], points[0])
  sum / 2
end

input_str = "(34,145) (37,105) (41,66) (70,56) (99,49)
(134,41) (152,37) (185,35) (226,31) (282,30)
(334,31) (413,44) (450,63) (473,107) (490,138)
(500,217) (495,255) (470,278) (445,276) (401,255)
(396,216) (396,175) (381,139) (353,118) (310,117)
(289,130) (256,120) (240,99) (219,84) (172,82)
(152,90) (139,100) (113,116) (97,126) (68,143)"

points_array = input_str.scan(/\((\d+),(\d+)\)/).map { |x, y| Point.new(x.to_i, y.to_i) }

square = calculate_square(points_array)
puts "Square of the polygon is #{square}"
