require_relative 'student'
def count_students_need_dorm(students)
  students.count do |student|
    student.dorm?
  end
end

def find_students_worked_teacher(students, years)
  students.filter do |student|
    student.experience >= years
  end
end

def find_students_graduated_from(students, uni)
  students.filter do |student|
    student.graduated == uni
  end
end

def to_language_map(students)
  to_pairs = students.flat_map do |student|
    student.languages.map do
      |lang| [lang, student]
    end
  end
  to_pairs.group_by(&:first).transform_values do |pairs|
    pairs.map(&:last)
  end
end

students = Student::StudentGenerator.new.generate

students.each do |student|
  puts student
end


puts "#{count_students_need_dorm(students).inspect} students need a dormitory room"
puts "#{find_students_worked_teacher(students, 2).inspect } are students, who worked as teacher for 2+ years"
puts "#{find_students_graduated_from(students, 'ped').inspect} are students, who graduated from pedagogic school"
puts "Language map:\n#{to_language_map(students)}"