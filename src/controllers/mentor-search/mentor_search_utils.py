import re

def remove_oid(string):
  # function that replace $oid to _id from collection.find() cursor
  while True:
      pattern = re.compile('{\s*"\$oid":\s*(\"[a-z0-9]{1,}\")\s*}')
      match = re.search(pattern, string)
      if match:
          string = string.replace(match.group(0), match.group(1))
      else:
          return string

def flatten(l):
    return [item for sublist in l for item in sublist]

# function that returns subpaths where weights will be lower based on search parameteres
def get_subpath(paths):
  subpaths = []

  for path in paths :
    if path == 'education.degree' or path == 'education.specialization' or path == 'education.university':
      subpaths.append('experiencecorpus')
      subpaths.append('educationcorpus')

    if path == 'experience.designation' or path == 'experience.company_name':
      subpaths.append('experiencecorpus')

    if path == 'industry':
      subpaths.append('field_of_work')
      subpaths.append('experience.industry')

    if path== 'field_of_work':
      subpaths.append('industry')
      subpaths.append('experience.industry')

  normalised_result = list(set(subpaths))

  if len(normalised_result):
    return normalised_result
  else :
    # return paths
    return None


# function that returns subgroup where weights will be even lower based on search parameteres
def get_subgroup(paths):
  subgroups = []

  for path in paths:
    if path == 'experience.designation' or path == 'experience.company_name':
      subgroups.append('about')

    if path == 'industry' or path == 'field_of_work':
      subgroups.append('experiencecorpus')

  normalised_result = list(set(subgroups))

  if len(normalised_result):
    return normalised_result
  else :
    # return paths
    return None


def get(value, path, default = None):
  try:
    result = value[path]
  except (IndexError, KeyError, TypeError) as error:
    print(error, flush=True)
    result = default

  return result

def transform_pagination_params(page, per_page):
  skip = (page - 1) * per_page
  limit = page * per_page
  return {
    skip,
    limit,
  }

def is_none(value):
  return value is None

def is_empty(value):
  return is_none(value) or any(value) is False

def filter_by(predicate, value):
  result = list()
  for index, keyed_value in enumerate(value):
    print("filter_by: key - " + str(index) + " value - " + str(keyed_value), flush=True)
    if predicate(keyed_value) is False:
      result.append(keyed_value)
  return result