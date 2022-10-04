from enum import Enum, IntEnum

from marshmallow import fields, Schema, ValidationError, validates


class MentorsSearchSortBy(str, Enum):
  Score = 'score'
  Rating = 'rating'
  Price = 'mentorPrice'


class MentorsSearchSortOrder(IntEnum):
  Ask = 1
  Desk = -1


allowed_search_sort_order = [entry.value for entry in MentorsSearchSortOrder]

def validate_sort_order(value, allowed_values):
  if int(value) not in allowed_values:
    raise ValidationError("Sort order '%s' is not allowed!" % value)


class ListRequestSchema(Schema):
  page = fields.Number(load_default=1)
  perPage = fields.Number(load_default=20)
  sortBy = fields.String()
  sortOrder = fields.String(load_default=MentorsSearchSortOrder.Desk.value)

  @validates('sortOrder')
  def validates_sort_order(self, value, **kwargs):
    validate_sort_order(value, allowed_search_sort_order)


class MentorsSearchRequestSchema(Schema):
  query = fields.String()
  page = fields.Number(load_default=1)
  perPage = fields.Number(load_default=20)
  sortBy = fields.Enum(MentorsSearchSortBy, by_value=True, load_default=MentorsSearchSortBy.Score)
  sortOrder = fields.Number(load_default=MentorsSearchSortOrder.Desk)

  @validates('sortOrder')
  def validates_sort_order(self, value, **kwagrs):
    validate_sort_order(value, allowed_search_sort_order)


class ListResponseSchema(Schema):
  count = fields.Number(default=0)
  page = fields.Number()
  perPage = fields.Number()
  sortBy = fields.Enum(MentorsSearchSortBy, by_value=True)
  sortOrder = fields.Number()


class MentorsWeightedSearchRequestSchema(MentorsSearchRequestSchema):
  experienceDesignation = fields.List(fields.String())
  experienceCompanyName = fields.List(fields.String())
  educationUniversity = fields.List(fields.String())
  educationDegree = fields.List(fields.String())
  educationSpecialization = fields.List(fields.String())

  industry = fields.List(fields.String())
  fieldOfWork = fields.List(fields.String())
  language = fields.List(fields.String())
  mentorType = fields.List(fields.String())
  location = fields.List(fields.String())


class MentorExperienceSchema(Schema):
  company_name = fields.String(required=True)
  designation = fields.String(required=True)


class MentorTalentBoardProjectSchema(Schema):
  url = fields.String()
  thumbnail = fields.String()
  type = fields.String()


class MentorTalentBoardSchema(Schema):
  _id = fields.UUID()
  title = fields.String()
  description = fields.String()
  hifi = fields.List(fields.String) # TODO: fix in the future
  followers = fields.List(fields.String) # TODO: fix in the future
  project = fields.List(fields.Nested(MentorTalentBoardProjectSchema))


class MentorTalentBoardHostSchema(Schema):
  _id = fields.UUID()
  talent_boards = fields.List(fields.Nested(MentorTalentBoardSchema))


class MentorLanguageSchema(Schema):
  language = fields.String()


class MentorEducationSchema(Schema):
  specialization = fields.String()
  degree = fields.String()
  university_name = fields.String()


class MentorProfileSchema(Schema):
  user_id = fields.UUID(required=True)
  name = fields.String(required=True)
  mentorPrice = fields.Number(required=True)
  fieldOfWork = fields.String()
  experience = fields.List(fields.Nested(MentorExperienceSchema))
  education = fields.List(fields.Nested(MentorEducationSchema))
  industry = fields.String()
  mentorFor = fields.String()
  mentorType = fields.String()
  about = fields.String()
  current_location = fields.String()
  profilePic = fields.String()
  talent_board = fields.Nested(MentorTalentBoardHostSchema)
  # talent_board = fields.String()
  rating = fields.String()  # @TODO: change
  score = fields.Number()
  language = fields.List(fields.Nested(MentorLanguageSchema))


class MentorProfilesSearchResponseSchema(ListResponseSchema):
  data = fields.List(fields.Nested(MentorProfileSchema), default=[])


class MentorsAutocompleteSortBy(str, Enum):
  Score = 'score'

class MentorsAutocompleteRequestSchema(ListRequestSchema):
  query = fields.String(required=True, validate=fields.Length(3))
  perPage = fields.Number(load_default=100)
  sortBy = fields.Enum(MentorsAutocompleteSortBy, load_default=MentorsSearchSortBy.Score, by_value=True)


class MentorsAutocompleteItemSchema(Schema):
  value = fields.String()
  field_name = fields.String()


class MentorsAutocompleteResponseSchema(ListResponseSchema):
  data = fields.List(fields.Nested(MentorsAutocompleteItemSchema))
  sortBy = fields.Enum(MentorsAutocompleteSortBy, by_value=True)

class MentorsFilterRequestSchema(Schema):
  field_name = fields.String(required=True)

class MentorsFilterItemSchema(Schema):
  field_name = fields.String(required=True)
  value = fields.String(required=True)

class MentorsFilterResponseSchema(Schema):
  data = fields.List(fields.Nested(MentorsFilterItemSchema))