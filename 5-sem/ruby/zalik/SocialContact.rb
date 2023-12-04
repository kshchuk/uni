require_relative 'Contact'

class SocialContact < Contact
  attr_accessor :social_media_account

  def initialize(name, surname, social_media_account)
    super(name, surname)
    @social_media_account = social_media_account
  end

  def merge_with(other)
    merged_contact = SocialContact.new(self.name, self.surname, self.social_media_account)
    merged_contact.social_media_account ||= other.social_media_account
    merged_contact
  end
end