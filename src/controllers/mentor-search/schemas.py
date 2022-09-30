from enum import Enum, IntEnum

import marshmallow as ma


class MentorsSearchSortBy(str, Enum):
  Score = 'score'
  Rating = 'rating'
  Price = 'price'


class MentorsSearchSortOrder(IntEnum):
  Ask = 1
  Desk = -1


class MentorsSearchRequestSchema(ma.Schema):
  query = ma.fields.String()
  page = ma.fields.Number(load_default=1)
  perPage = ma.fields.Number(load_default=20)
  sortBy = ma.fields.Enum(MentorsSearchSortBy, by_value=True, load_default=MentorsSearchSortBy.Score)
  sortOrder = ma.fields.Number(load_default=MentorsSearchSortOrder.Desk)

  @ma.validates('sortOrder')
  def validate_sort_order(self, value, **kwagrs):
    normalised_value = value or MentorsSearchSortOrder.Desk
    allowed_values = [entry.value for entry in MentorsSearchSortOrder]
    if int(normalised_value) not in allowed_values:
      raise ma.ValidationError("Sort order '%s' is not allowed!" % value)


class MentorExperienceSchema(ma.Schema):
  company_name = ma.fields.String(required=True)
  designation = ma.fields.String(required=True)


class MentorTalentBoardSchema(ma.Schema):
  title = ma.fields.String()
  description = ma.fields.String()


class MentorProfileSchema(ma.Schema):
  user_id = ma.fields.UUID(required=True)
  name = ma.fields.String(required=True)
  mentorPrice = ma.fields.Number(required=True)
  experience = ma.fields.Nested(MentorExperienceSchema)
  mentorFor = ma.fields.String()
  about = ma.fields.String()
  current_location = ma.fields.String()
  profilePic = ma.fields.String()
  talent_board = ma.fields.Nested(MentorTalentBoardSchema)
  rating = ma.fields.String()  # @TODO: change
  score = ma.fields.Number()


class MentorProfilesSearchResponseSchema(ma.Schema):
  count = ma.fields.Number(default=0)
  data = ma.fields.List(ma.fields.Nested(MentorProfileSchema), default=[])
  page = ma.fields.Number()
  perPage = ma.fields.Number()
  sortBy = ma.fields.Enum(MentorsSearchSortBy, by_value=True)
  sortOrder = ma.fields.Number()
