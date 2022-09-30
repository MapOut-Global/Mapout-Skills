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

def get_subpath(paths):
  # function that returns subpaths where weights will be lower based on search parameteres
  subpaths = []

  for path in paths :
    if (path=='education.degree' or path=='education.specialization' or path=='education.university'):
      subpath1 = 'experiencecorpus'
      subpath2 = 'educationcorpus'
      subpaths.append(subpath1)
      subpaths.append(subpath2)

    if (path=='experience.designation' or path=='experience.company_name'):
      subpath = 'experiencecorpus'
      subpaths.append(subpath)

    if (path=='industry'):
      subpath1 = 'field_of_work'
      subpath2 = 'experience.industry'
      subpaths.append(subpath1)
      subpaths.append(subpath2)

    if (path=='field_of_work'):
      subpath1 = 'industry'
      subpath2 = 'experience.industry'
      subpaths.append(subpath1)
      subpaths.append(subpath2)



  if len(list(set(subpaths))):
    return(list(set(subpaths)))

  else :
    return paths


def get_subgroup(paths):
  # function that returns subgroup where weights will be even lower based on search parameteres
  subgroups = []

  for path in paths :
    if (path=='experience.designation' or path=='experience.company_name'):
      subgroup = 'about'
      subgroups.append(subgroup)

    if (path=='industry' or path=='field_of_work'):
      subgroup = 'experiencecorpus'
      subgroups.append(subgroup)

  if len(list(set(subgroups))):
    return(list(set(subgroups)))

  else :
    return paths


def get(value, index, default = None):
  try:
    result = value[index]
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