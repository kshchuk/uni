require_relative 'Contact'

class ContactList
    def initialize
      @contacts = []
    end
  
    def add_contact(contact)
      @contacts << contact
    end
  
    def search(criteria)
      results = @contacts.select do |contact|
        criteria.all? do |key, value|
          contact.send(key).to_s.downcase.include?(value.to_s.downcase)
        end
      end
      results
    end

    def sort_by_name
      @contacts.sort_by { |contact| [contact.surname, contact.name] }
    end
  
    def merge_contacts(contact1, contact2)
      merged_contact = Contact.new(contact1.name, contact1.surname)
      merged_contact.phone_number = contact1.phone_number if contact1.is_a?(PhoneContact)
      merged_contact.social_media_account = contact1.social_media_account if contact1.is_a?(SocialContact)
  
      merged_contact.phone_number ||= contact2.phone_number if contact2.is_a?(PhoneContact)
      merged_contact.social_media_account ||= contact2.social_media_account if contact2.is_a?(SocialContact)
  
      merged_contact
    end

    def merge_contacts(contact1, contact2)
      raise NotImplementedError, "Subclasses must implement the 'merge_with' method" unless contact1.is_a?(Contact) && contact2.is_a?(Contact)
      
      contact1.merge_with(contact2)
    end
  
    def merge_and_add_contacts(contact1, contact2)
      raise NotImplementedError, "Subclasses must implement the 'merge_with' method" unless contact1.is_a?(Contact) && contact2.is_a?(Contact)
      
      merged_contact = merge_contacts(contact1, contact2)
      add_contact(merged_contact)
    end
  end
  