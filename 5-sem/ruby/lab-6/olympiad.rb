require_relative "student"

class Olympiad
  attr_accessor :students

  def initialize
    @students = []
  end

  def add_student(student)
    @students << student
  end

  def schools_with_prizes
    @students.select { |student| student.placement <= 3 }.map(&:school_number).uniq
  end

  def school_with_most_prizes
    schools = @students.group_by(&:school_number)
    school_with_most_prizes = schools.max_by { |_, students| students.count }&.first
    school_with_most_prizes.nil? ? "No students participated" : school_with_most_prizes
  end

  def first_place_students
    @students.select { |student| student.placement == 1 }.map { |student| "#{student.surname} - #{student.class_level}" }
  end
end

# Example Usage:
olympiad = Olympiad.new

# Adding students to the olympiad
olympiad.add_student(Student.new("Smith", 1, 10, 1))
olympiad.add_student(Student.new("Johnson", 2, 11, 2))
olympiad.add_student(Student.new("Williams", 1, 10, 3))
olympiad.add_student(Student.new("Brown", 3, 9, 1))
olympiad.add_student(Student.new("Jones", 2, 11, 1))

# 1) List of schools that won prizes
puts "Schools with prize-winning students: #{olympiad.schools_with_prizes}"

# 2) School with the most prize-winning students
puts "School with the most prize-winning students: #{olympiad.school_with_most_prizes}"

# 3) List of students who secured the first place and their classes
puts "Students who secured the first place and their classes: #{olympiad.first_place_students}"
