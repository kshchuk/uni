
class Contact
  attr_accessor :name, :surname

  def initialize(name, surname)
    @name = name
    @surname = surname
  end

  def merge_with(other)
    raise NotImplementedError, "Subclasses must implement the 'merge_with' method"
  end

  def to_s
    "#{@name} #{@surname}"
  end
end

