require 'matrix'
require 'minitest/autorun'
def multiply_by_num(matrix, n)
  matrix * n
end

def sum(matrix1, matrix2)
  matrix1 + matrix2
end

def transpose (matrix)
  matrix.transpose
end

def multiply (matrix1, matrix2)
  matrix1 * matrix2
end

def trace (matrix)
  matrix.trace
end

def vector_scalar_product(v1,v2)
  v1.inner_product(v2)
end

def vector_v_product(v1, v2)
  v1.cross(v2)
end

def vector_norm(v)
  v.r
end

def vector_by_matrix(v, a)
  a * v
end

def matrix_by_vector(a, v)
  a * v
end

def outer_product(v1, v2)
  n = v1.length
  m = v2.length
  result = Array.new(v1.length) { Array.new(v2.length, 0) }
  (0...n).each do |i|
    (0...m).each do |j|
      result[i][j] = v1[i] * v2[j]
    end
  end
  result
end


def array_transpose(arr)
  if arr.empty?
    return []
  end
  n = arr[0].length
  m = arr.length
  transposed = Array.new(n) { Array.new(m, 0) }
  (0...n).each do |i|
    (0...m).each do |j|
      transposed[i][j] = arr[j][i]
    end
  end
  transposed
end

def array_matrix_vector_mult(matrix, vector_col)
  if matrix[0].length != vector_col.length
    raise ArgumentError, "dimension error"
  end
  n = vector_col.length
  m = matrix.length
  product = Array.new(m)
  (0...m).each do |i|
    s = 0
    (0...n).each do |j|
      s += matrix[i][j] * vector_col[j]
    end
    product[i] = s
  end
  product
end

class TestMatrixOperations < MiniTest::Test
  def test_multiply_by_num
    matrix = Matrix[[1,2,3],[4,5,6],[7,8,9]]
    assert_equal(Matrix[[2, 4, 6], [8, 10, 12], [14, 16, 18]], multiply_by_num(matrix, 2))
  end

  def test_sum
    matrix_a = Matrix[[1,2],[4,5]]
    matrix_b = Matrix[[4,7],[8,2]]
    assert_equal(Matrix[[5,9],[12,7]], sum(matrix_a, matrix_b))
  end
  def test_transpose
    matrix = Matrix[[1,2],[3,4]]
    assert_equal(Matrix[[1,3],[2,4]], transpose(matrix))
  end

  def test_multiply
    matrix_a = Matrix[[1,2],[4,5]]
    matrix_b = Matrix[[4,7],[8,2]]
    assert_equal(Matrix[[20,11],[56,38]], multiply(matrix_a, matrix_b))
  end

  def test_trace
    matrix = Matrix[[2, 4, 6], [8, 10, 12], [14, 16, 18]]
    assert_equal(30, trace(matrix))
  end

  def test_vector_scalar_product
    v1 = Vector[2, 4, 6]
    v2 = Vector[1, 5, 9]
    assert_equal(76, vector_scalar_product(v1,v2))
  end

  def test_vector_product
    v1 = Vector[2, 4, 6]
    v2 = Vector[1, 5, 9]
    assert_equal(Vector[6, -12, 6], vector_v_product(v1, v2))
  end

  def test_vector_norm
    v1 = Vector[2, 4, 6]
    v2 = Vector[1, 5, 9]
    assert((7.48331477354788 - vector_norm(v1)).abs < 0.000001)
    assert((10.3440804327886 - vector_norm(v2)).abs < 0.000001)
  end

  def test_vector_by_matrix
    v = Vector[1, 5, 9]
    v2 = Matrix.column_vector([1, 2, 3])
    a = Matrix[[1,2,3],[4,5,6],[7,8,9]]
    assert_equal(Matrix[[14], [32], [50]], vector_by_matrix(v2, a))
    assert_equal(Vector[38, 83, 128], matrix_by_vector(a, v))
  end

  def test_array_transpose
    assert_equal([[1,4],[2,5],[3,6]], array_transpose([[1,2,3],[4,5,6]]))
    assert_equal([], array_transpose([]))
  end

  def test_array_matrix_vector_mult
    matrix = [[1,2,3],[4,5,6]]
    vector = [7,8]
    vector2 = [7,8, 9]
    assert_raises(ArgumentError) do
      array_matrix_vector_mult(matrix,vector)
    end
    assert_equal([50,122],  array_matrix_vector_mult(matrix,vector2))
  end

  def test_outer_product
    vector = [1,2,3]
    vector2 = [4,5,6]
    assert_equal([[4,5,6],[8,10,12],[12,15,18]], outer_product(vector,vector2))
  end
end
