require_relative 'Contact'

class PhoneContact < Contact
  attr_accessor :phone_number

  def initialize(name, surname, phone_number)
    super(name, surname)
    @phone_number = phone_number
  end
end
