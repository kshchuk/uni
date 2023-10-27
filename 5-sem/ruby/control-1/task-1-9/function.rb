
class Function
    attr_accessor :a, :b, :c, :x_start, :x_end, :dx
  
    def initialize(a, b, c, x_start, x_end, dx)
      @a = a
      @b = b
      @c = c
      @x_start = x_start
      @x_end = x_end
      @dx = dx
    end

    def calculate_function(x)
        f = if @a < 0 && x != 0
            @a * x**2 + @b**2 * x
          elsif @a > 0 && x == 0
            x - @a / (@x - @c)
          else
            1 + x / @c
          end
    end
    
    def check_params(a, b, c)
        to_i = ~((@a.to_i | @c.to_i) & (@b.to_i | @c.to_i)) == 0
    end
  
    def calculate
        x = @x_start

        to_i = check_params(@a, @b, @c)

        while x <= @x_end
            f = calculate_function(x)
            f = f.to_i if to_i
        
            puts "X: #{x}, F: #{f}"
            x += @dx
        end
    end
end
  