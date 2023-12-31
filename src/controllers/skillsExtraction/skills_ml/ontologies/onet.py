from .base import Competency, Occupation, CompetencyOntology
from .clustering import Clustering
from skills_ml.datasets.onet_cache import OnetSiteCache
# from descriptors import cachedproperty
from cached_property import cached_property as cachedproperty
import logging
from skills_ml import log
import pandas as pd

majorgroupname = {
    '11': 'Management',
    '13': 'Business and Financial Operations',
    '15': 'Computer and Mathematical',
    '17': 'Architecture and Engineering',
    '19': 'Life, Physical, and Social Science',
    '21': 'Community and Social Service',
    '23': 'Legal',
    '25': 'Education, Training, and Library',
    '27': 'Arts, Design, Entertainment, Sports, and Media',
    '29': 'Healthcare Practitioners and Technical',
    '31': 'Healthcare Support',
    '33': 'Protective Service',
    '35': 'Food Preparation and Serving Related',
    '37': 'Building and Grounds Cleaning and Maintenance',
    '39': 'Personal Care and Service',
    '41': 'Sales and Related',
    '43': 'Office and Administrative Support',
    '45': 'Farming, Fishing, and Forestry',
    '47': 'Construction and Extraction',
    '49': 'Installation, Maintenance, and Repair',
    '51': 'Production',
    '53': 'Transportation and Material Moving',
    '55': 'Military Specific'
}
list_file=['Abilities',
 'Alternate Titles',
 'Career Changers Matrix',
 'Career Starters Matrix',
 'Content Model Reference',
 'DWA Reference',
 'Education, Training, and Experience Categories',
 'Education, Training, and Experience',
 'Emerging Tasks',
 'Green DWA Reference',
 'Green Occupations',
 'Green Task Statements',
 'Interests',
 'IWA Reference',
 'Job Zone Reference',
 'Job Zones',
 'Knowledge',
 'Level Scale Anchors',
 'Occupation Data',
 'Occupation Level Metadata',
 'Read Me',
 'Sample of Reported Titles',
 'Scales Reference',
 'Skills',
 'Survey Booklet Locations',
 'Task Categories',
 'Task Ratings',
 'Task Statements',
 'Tasks to DWAs',
 'Tasks to Green DWAs',
 'Tools and Technology',
 'UNSPSC Reference',
 'Work Activities',
 'Work Context Categories',
 'Work Context',
 'Work Styles',
 'Work Values']


class Onet(CompetencyOntology):
    def __init__(self, onet_cache=None, manual_build=True):
        if manual_build:
            logging.info('Manual build specified. Building O*NET CompetencyOntology via direct querying from O*NET site, or local cache.')
            super().__init__()
            self.is_built = False
            self.onet_cache = onet_cache or OnetSiteCache()
            self.name = 'onet'
            self.competency_framework.name = 'onet_ksat'
            self.competency_framework.description = 'ONET Knowledge, Skills, Abilities, Tools, and Technology'
            self._build()
        else:
            logging.info('Building O*NET CompetencyOntology via Research Hub-hosted JSON-LD')
            super().__init__(research_hub_name='onet')
    
    def add_new_skills(self,data_input):
        if self.is_built:
            onet_cache = self.onet_cache
            self.name = 'onet'
            self.competency_framework.name = 'onet_ksat'
            self.competency_framework.description = 'ONET Knowledge, Skills, Abilities, Tools, and Technology'
            self.is_built = False
            df,path_=onet_cache.reader("skills_set",get_path=True)
            df=pd.DataFrame(df)
            keys=list(df.Type.unique())
            for i in data_input:
                data_input[i.upper()]=data_input.pop(i)
            input_keys=list(data_input.keys())
            input_keys
            new_keys=[]
            for i in input_keys:
                if i not in keys:
                    print(i,"not in list of",keys)
                    input_keys.remove(i)
                    new_keys.append(i)
            for type_to_change in input_keys:
                list_of_skills=data_input[type_to_change]
                if isinstance(list_of_skills, (list, tuple)):
                    for skill in list_of_skills:
                        temp=df[df['Element Name']==skill.upper()]
                        length=temp.shape[0]
                        if length==1 and df.iloc[temp.index[0]]['Type'] != type_to_change :
                            df.iloc[temp.index[0]]['Type']=type_to_change
                        elif length==0:
                            df.loc[len(df.index)]={"Element Name":skill.upper(),"Type":type_to_change}
                        else:
                            logging.warning("{} {} already present".format(skill.upper(),type_to_change))
                else:
                    logging.warning("{} not a iterable object".format(list_of_skills))
            if len(new_keys):
                flag=input("Are you aggre for add new skills type {} [y/n] :".format(new_keys))
                if flag.upper()=="Y":
                    for type_to_change in new_keys:
                        list_of_skills=data_input[type_to_change]
                        for skill in list_of_skills:
                            temp=df[df['Element Name']==skill.upper()]
                            length=temp.shape[0]
                            if length==1:
                                df.iloc[temp.index[0]]['Type']=type_to_change
                            elif length==0:
                                df.loc[len(df.index)]={"Element Name":skill.upper(),"Type":type_to_change}
            df.to_csv(path_,header=True, index=None, sep='\t')
            self._build()
            return True
        else:
            logging.warning('O*Net Ontology is not built!')


    def _build(self):
        if not self.is_built:
            onet_cache = self.onet_cache
            description_lookup = {}
            logging.info('Processing Content Model Reference')
            for row in onet_cache.reader('Content Model Reference'):
                description_lookup[row['Element ID']] = row['Description']

            # logging.info('Processing occupation data')
            # for row in onet_cache.reader('Occupation Data'):
            #     occupation = Occupation(
            #             identifier=row['O*NET-SOC Code'],
            #             name=row['Title'],
            #             description=row['Description'],
            #             categories=['O*NET-SOC Occupation'],
            #     )
            #     major_group_num = row['O*NET-SOC Code'][0:2]
            #     major_group = Occupation(
            #         identifier=major_group_num,
            #         name=majorgroupname[major_group_num],
            #         categories=['O*NET-SOC Major Group']
            #     )
            #     occupation.add_parent(major_group)
            #     self.add_occupation(occupation)
            #     self.add_occupation(major_group)

            logging.info('Processing skills set')
            for content_model_file in {"skills_set"}:
                for i,row in enumerate(onet_cache.reader(content_model_file)):
                    competency = Competency(
                    identifier=i,
                    name=row['Element Name'],
                    categories=[row['Type']])

                    self.add_competency(competency)
                    # occupation = Occupation(identifier=row['O*NET-SOC Code'])
                    # self.add_edge(competency=competency, occupation=occupation)


            # logging.info('Processing tools and technology')
            # for content_model_file in {'Tools and Technology'}:
            #     for row in onet_cache.reader(content_model_file):
            #         key = row['Commodity Code'] + '-' + row['T2 Example']
            #         commodity_competency = Competency(
            #             identifier=row['Commodity Code'],
            #             name=row['Commodity Title'],
            #             categories=[row['T2 Type'], 'UNSPSC Commodity'],
            #         )
            #         competency = Competency(
            #             identifier=key,
            #             name=row['T2 Example'],
            #             categories=[row['T2 Type'], 'O*NET T2'],
            #         )
            #         competency.add_parent(commodity_competency)
            #         self.add_competency(commodity_competency)
            #         self.add_competency(competency)
            #         # occupation = Occupation(identifier=row['O*NET-SOC Code'])
            #         # self.add_edge(competency=competency, occupation=occupation)

            self.is_built = True
        else:
            logging.warning('O*Net Ontology is already built!')

    @cachedproperty
    def all_soc(self):
        occupations = self.occupations
        soc = []
        for occ in occupations:
            if 'O*NET-SOC Occupation' in occ.other_attributes['categories']:
                soc.append(occ.identifier)
        return sorted(soc)

    @cachedproperty
    def all_major_groups(self):
        occupations = self.occupations
        major_groups = []
        for occ in occupations:
            if 'O*NET-SOC Major Group' in occ.other_attributes['categories']:
                major_groups.append(occ)
        return sorted(major_groups, key=lambda k: k.identifier)

    @cachedproperty
    def all_major_groups_occ(self):
        occ = self.filter_by(lambda edge: len(edge.occupation.identifier) == 2)
        return occ.occupations

    @cachedproperty
    def competency_categories(self):
        return set(c.categories[0] for c in self.competencies)

    @cachedproperty
    def major_group_occupation_name_clustering(self):
        d = Clustering(
                name="major_group_occupations_name",
                key_transform_fn=lambda concept: getattr(concept, "name"),
                value_item_transform_fn=lambda entity: (getattr(entity, "identifier"), getattr(entity, "name")),
        )
        for mg in self.all_major_groups_occ:
            d[mg] = [child for child in mg.children]
        return d

    @cachedproperty
    def major_group_occupation_description_clustering(self):
        d = Clustering(
                name="major_group_occupations_description",
                key_transform_fn=lambda concept: getattr(concept, "name"),
                value_item_transform_fn=lambda entity: (
                    getattr(entity, "identifier"),
                    ' '.join([str(getattr(entity, "name")), str(getattr(entity, "other_attributes").get("description"))])),
        )
        for mg in self.all_major_groups_occ:
            d[mg] = [child for child in mg.children]
        return d

    @cachedproperty
    def major_group_competencies_name_clustering(self):
        d = Clustering(
                name="major_group_competencies_name",
                key_transform_fn=lambda concept: getattr(concept, "name"),
                value_item_transform_fn=lambda entity: (getattr(entity, "identifier"), getattr(entity, "name")),
        )
        for mg in self.all_major_groups_occ:
            d[mg] = self.filter_by(lambda edge: edge.occupation.identifier[:2] == mg.identifier[:2]).competencies
        return d

    @cachedproperty
    def major_group_competencies_description_clustering(self):
        d = Clustering(
                name="major_group_competencies_description",
                key_transform_fn=lambda concept: getattr(concept, "name"),
                value_item_transform_fn=lambda entity: (
                    getattr(entity, "identifier"),
                    ' '.join([str(getattr(entity, "name")), str(getattr(entity, "other_attributes").get("competencyText"))])),
        )
        for mg in self.all_major_groups_occ:
            d[mg] = self.filter_by(lambda edge: edge.occupation.identifier[:2] == mg.identifier[:2]).competencies
        return d

    def generate_clusterings(self):
        return [
            self.major_group_occupation_name_clustering,
            self.major_group_occupation_description_clustering,
            self.major_group_competencies_name_clustering,
            self.major_group_competencies_description_clustering
        ]
