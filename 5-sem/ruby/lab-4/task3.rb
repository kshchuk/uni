
require 'minitest/autorun'
def create_matrix(dim, k)
  if dim < 3 || dim > 9
    raise ArgumentError, "dimension has to be inside [3,9] range"
  end
  diag = 2
  not_diag = k + 2
  matrix = []
  dim.times do |i|
    arr = []
    dim.times do |j|
      arr << (i == j ? diag : not_diag)
    end
    matrix << arr
  end
  matrix
end

def create_b_vector(dim)
  if dim < 3 || dim > 9
    raise ArgumentError, "dimension has to be inside [3,9] range"
  end
  (1..dim).to_a
end

def comp_double(d1, d2)
  (d1-d2).abs < 0.000001
end

def solve(a, b)
  matrix = a.dup
  vector = b.dup
  dim = vector.length
  if dim < 3 || dim > 9
    raise ArgumentError, "dimension has to be inside [3,9] range"
  end
  if matrix.length != dim || matrix[0].length != dim
    raise ArgumentError, "matrix and vector have different dimensions"
  end

  #forward elimination

  (0...dim).each do |index|
    diag = matrix[index][index]
    (index...dim).each do |i|
      matrix[index][i] /= diag.to_f
    end
    vector[index] /=diag.to_f
    (index+1...dim).each do |i|
      diff = matrix[i][index]
      (index...dim).each do |j|
        matrix[i][j] -= diff * matrix[index][j]
      end
      vector[i] -= diff * vector[index]
    end
  end

  # back substitution

  (dim-1).downto(0) do |index|
    bc = vector[index]
    (index-1).downto(0) do |i|
      ac = matrix[i][index]
      matrix[i][index] = 0
      vector[i] -= bc * ac
    end
  end
  vector
end

class TestSystemSolve < MiniTest::Test
  def test_matrix_creation
    assert_raises(ArgumentError) do
      create_matrix(2,12)
    end
    assert_raises(ArgumentError) do
      create_matrix(12,12)
    end
    assert_equal([[2, 4, 4], [4, 2, 4], [4, 4, 2]], create_matrix(3,2))
  end
  def test_vector_creation
    assert_raises(ArgumentError) do
      create_b_vector(2)
    end
    assert_raises(ArgumentError) do
      create_b_vector(12)
    end
    assert_equal([1,2,3,4,5], create_b_vector(5))
  end

  def test_solve
    matrix = create_matrix(5,12)
    b = create_b_vector(5)
    x = solve(matrix, b)
    assert(comp_double(x[0], 19.0/87.0), "x[0] = #{x[0]} != 47.0/348.0")
    assert(comp_double(x[1], 47.0/348.0), "x[1] = #{x[1]} != 47.0/348.0")
    assert(comp_double(x[2], 3.0/58.0), "x[2] = #{x[2]} != 3.0/58.0")
    assert(comp_double(x[3], -11.0/348.0), "x[3] = #{x[3]} != -11.0/348.0")
    assert(comp_double(x[4], -10.0/87.0), "x[4] = #{x[4]} != -10.0/87.0")

    matrix2 = create_matrix(4,12)
    b2 = create_b_vector(5)
    assert_raises(ArgumentError) do
      solve(matrix2, b2)
    end
  end
end
