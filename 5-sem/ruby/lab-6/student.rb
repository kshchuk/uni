class Student
  attr_accessor :surname, :school_number, :class_level, :placement

  def initialize(surname, school_number, class_level, placement)
    @surname = surname
    @school_number = school_number
    @class_level = class_level
    @placement = placement
  end
end
