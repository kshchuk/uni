require 'minitest/autorun'

require_relative 'ContactList'
require_relative 'PhoneContact'
require_relative 'SocialContact'

class TestContactList < Minitest::Test
  def setup
    @contact_list = ContactList.new

    @contact1 = PhoneContact.new("John", "Doe", "123-456-7890")
    @contact2 = SocialContact.new("Jane", "Smith", "@jane_smith")
  end

  def test_add_contact
    @contact_list.add_contact(@contact1)
    assert_equal 1, @contact_list.instance_variable_get(:@contacts).size
  end

  def test_search_by_name
    @contact_list.add_contact(@contact1)
    @contact_list.add_contact(@contact2)

    results = @contact_list.search(name: "John")
    assert_equal [@contact1], results

    results = @contact_list.search(name: "Jane")
    assert_equal [@contact2], results
  end

  def test_search_by_multiple_criteria
    @contact_list.add_contact(@contact1)
    @contact_list.add_contact(@contact2)

    results = @contact_list.search(name: "John", phone_number: "123-456-7890")
    assert_equal [@contact1], results

    results = @contact_list.search(name: "Jane", social_media_account: "@jane_smith")
    assert_equal [@contact2], results
  end

  def test_sort_by_name
    @contact_list.add_contact(@contact2)
    @contact_list.add_contact(@contact1)

    sorted_contacts = @contact_list.sort_by_name
    assert_equal [@contact1, @contact2], sorted_contacts
  end

end
