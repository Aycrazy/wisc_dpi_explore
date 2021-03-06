#%%
import pandas as pd
import numpy as np
import os
import sys
import re
import altair as alt
import bokeh as bk
#%%

'''
To start this script was made to:
-Select data based on desired data category (i.e. enrollment, attendance,etc), 
which will reside in the directory <category>_data.  
-Select rows based on school name(s)
-Conform data to row-per-school year depending on the original data format
-Append data in conformed formats
-Merge with other data of interest
-Observe trends
'''

#workstation version
ENROLLPATH = '/Users/ayaspan/Documents/Personal/wisconsin_enrollment'
#home version
#ENROLLPATH = '/Users/yaz/Documents/wisconsin_schools_enrollment/wisconsin_enrollment/'


def collect_enrollments(dir, schools, cat=None):
    '''
    dir - dir to loop through
    schools- list type of schools of interest
    '''

    type1_df = pd.DataFrame()
    type2_df = pd.DataFrame()

    for f in os.listdir(dir):
        years_type1 = [str(y) for y in  range(1995,2005)]
        year1 = re.search(r'\d+',f).group(0)
        if year1 in years_type1:
            if cat:
                if cat in f:
                    print(f,' filename')
                    type1_df = type1_df.append(pd.read_csv("{0}/{1}".format(dir,f)))
        else:
            type2_df =type2_df.append(pd.read_csv("{0}/{1}".format(dir,f)))

    #type1 df school select

    print(type1_df.columns)

    type1_ss_df = type1_df[type1_df['school_name'].isin(schools)]

    type2_df.rename(columns={ c:c.lower() for c in type2_df.columns}, inplace=True)
    
    #print(type2_df.columns)

    type2_ss_df = type2_df[type2_df['school_name'].isin(schools)]

    
    return type1_ss_df, type2_ss_df

def conform2_to_df(df_type2,_filter_by):
    ''' 
        _fitler_by: category of interest as a string or list
        df : datset type 2
    '''

    if isinstance(_filter_by,str):
        conf_df = df_type2[df_type2['group_by'].isin([_filter_by,'All Students'])]\
            [['school_year','group_by_value','student_count']].pivot(index='school_year', columns='group_by_value', values='student_count')
    else:
        _filter_by.append('All Students')
        conf_df = df_type2[df_type2['group_by'].isin(_filter_by)]\
            [['school_year','group_by_value','student_count']].pivot(index='school_year', columns='group_by_value', values='student_count')

    rep_cols2 = {c:c.lower().replace(' ','_') for c in conf_df.columns}

    rep_cols2['All Students'] = 'total_enrollment'

    conf_df.rename(columns=rep_cols2, inplace=True)

    conf_df.reset_index(inplace=True)

    conf_df['school_year'] = conf_df.school_year.apply(lambda x: re.search(r'\d+',x).group(0))

    return conf_df

def race_prepare_type1_df(df_type1):


    df_type1 = df_type1[['year','school_name', 'black_count', 'amer_indian_count', 'asian_count','hisp_count','pac_isle_count','white_count','two_or_more_count','total_enrollment_prek-12' ]]


    rep_cols = {c:re.search(r'[a-z]+',c).group(0) for c in df_type1.columns if c not in ['school_name']}

    rep_cols['amer_indian_count'] = 'amer_indian'
    rep_cols['pac_isle_count'] = 'pacific_islander'
    rep_cols['two_or_more_count'] = 'two_or_more'
    rep_cols['hisp_count'] = 'hispanic'
    rep_cols['year'] = 'school_year'

    rep_cols['total_enrollment_prek-12'] = 'total_enrollment'

    df_type1.rename(columns=rep_cols, inplace=True)

    return df_type1

def race_join_both_types(df_type1, df_type2, standard_school_name):

    comb_df = df_type1.append(df_type2)

    comb_df.school_year = comb_df.school_year.astype(int)

    comb_df['school_name'] = standard_school_name

    comb_df = comb_df[['amer_indian', 'asian', 'black', 'hispanic', 'pacific_islander','two_or_more', 'white','school_year']].fillna(0).astype(int)

    comb_df['total_calc'] = comb_df[['amer_indian', 'asian', 'black', 'hispanic', 'pacific_islander','two_or_more', 'white']].apply(sum,axis=1)

    return comb_df 

# def econ_conform2_to_df(df_type2):

#     econ2_cols = {c:c.lower().replace(' ','_') for c in wash2_conf_df.columns}

#     ses_conf_df.rename(columns =econ2_cols, inplace=True)

#     ses_conf_df.reset_index(inplace=True)

#     ses_conf_df['school_year'] = ses_conf_df.school_year.apply(lambda x: re.search(r'\d+',x).group(0))

#     return ses_conf_df

def econ_prepare_type1(df_type1):

    df_type1 = df_type1[df_type1.columns[10:].to_list()+['year']]

    econ1_cols = {c:c.replace('_count','') for c in df_type1.columns if c not in ['school_name']}

    #econ1_cols={}
    econ1_cols['not_econd_disadv_count'] = 'not_econ_disadv'
    econ1_cols['total_enrollment_prek-12'] = 'all_students'
    econ1_cols['year'] = 'school_year'


    df_type1.rename(columns = econ1_cols, inplace=True)

    return df_type1

def econ_join_both_types(df_type1, df_type2, standard_school_name):

    joined_ses_df = df_type1.append(df_type2)
    joined_ses_df['school_name'] = standard_school_name
    joined_ses_df.school_year = joined_ses_df.school_year.astype(int)
    joined_ses_df.reset_index(inplace=True)

    joined_ses_df= joined_ses_df[['econ_disadv','not_econ_disadv','all_students','school_year']].fillna(0).astype(int)

    # joined_ses_df['econ_disadv_percent'] = (joined_ses_df.econ_disadv.astype(int)/joined_ses_df.all_students) *100


    # joined_ses_df['not_econ_disadv_percent'] = (joined_ses_df.not_econ_disadv.astype(int)/joined_ses_df.all_students) *100

    joined_ses_df['total_calc'] = joined_ses_df[['econ_disadv','not_econ_disadv']].apply(sum,axis=1)

    return joined_ses_df

def get_percents(joined_df, category, demos = ['white','black','hispanic']):

    for demo in demos:
        joined_df[category+'{0}_percent'.format(demo)] = (joined_df[demo]/ joined_df['total_calc']) * 100
    return joined_df 

def join_many_cat_dfs(cat1_df, cat2_df):

    cat1_and_2_df = pd.merge(cat1_df, cat2_df, how='left',on='school_year')

    return cat1_and_2_df

#%%

def dict_to_query(_dict):

    return ' and '.join(['{0} == "{1}"'.format(k,v) for k,v in _dict.items()])

def attend_prepare_type1(df_type1, cat_dict):

    #_filter_by.append('All Students')

    filter  = dict_to_query(cat_dict)

    print(filter)

    df_type1 = df_type1.query(filter)
    # df_type1 = df_type1[(df_type1['race_ethnicity'].isin(['All Groups Combined'])) &\
    #      (df_type1['economic_status'].isin(['Both Groups Combined'])) &\
    #       (df_type1['gender'].isin(['Both Groups Combined']))]\
    #         [['year','economic_status','race_ethnicity',\
    #             'actual_days_of_attendance','possible_days_of_attendance']].pivot(index='year',
    #              columns='economic_status', values=['actual_days_of_attendance','possible_days_of_attendance'])

    #attend1_cols = {c:c.replace('_count','') for c in df_type1.columns if c not in ['school_name']}

    attend1_cols={}
    # attend1_cols['amer_indian_count'] = 'amer_indian'
    # attend1_cols['pac_isle_count'] = 'pacific_islander'
    # attend1_cols['two_or_more_count'] = 'two_or_more'
    # attend1_cols['hisp_count'] = 'hispanic'
    # attend1_cols['year'] = 'school_year'
    # attend1_cols['not_econd_disadv_count'] = 'not_econ_disadv'
    # attend1_cols['total_enrollment_prek-12'] = 'all_students'
    attend1_cols['year'] = 'school_year'


    df_type1.rename(columns = attend1_cols, inplace=True)

    return df_type1

#%%
wash = ['Washington Hi', 'WHS Information Technology']

wash_rc1_df, wash_rc2_df = collect_enrollments(ENROLLPATH+'/enrollment_data', wash, 'race')

# %%

wash_rc2_df = conform2_to_df(wash_rc2_df, 'Race/Ethnicity')

# %%

wash_rc1_df = race_prepare_type1_df(wash_rc1_df)

# %%

wash_rc_df = race_join_both_types(wash_rc1_df, wash_rc2_df, 'Washington High School')

wash_rc_df = get_percents(wash_rc_df, '')

# %%

wash_ec1_df, wash_ec2_df = collect_enrollments(ENROLLPATH+'/enrollment_data', wash, 'economic')

wash_ec2_df = conform2_to_df(wash_ec2_df, 'Economic Status')

wash_ec1_df = econ_prepare_type1(wash_ec1_df)

#There are 2 different counts/percentages for 2005 and 2006 --> why?
wash_ec_df = econ_join_both_types(wash_ec1_df,
                                        wash_ec2_df,
                                        'Washington High School')

#riverside_ec_df['total_calc'] = riverside_ec_df[['econ_disadv','not_econ_disadv']].apply(sum,axis=1)

wash_ec_df = get_percents(wash_ec_df, '', ['econ_disadv','not_econ_disadv'])

#%%
# riverside_ec_df.drop([5], axis =0)

#%%

#For Econ disadv the 585 Not Disadv, 976 Disadv data is represented in wisedash
#From df type 2
wash_race_ses_df = join_many_cat_dfs(wash_rc_df,wash_ec_df)

# %%
riverside = ['Riverside High', 'Riverside Hi']

riverside_rc1_df, riverside_rc2_df = collect_enrollments(ENROLLPATH+'/enrollment_data', riverside, 'race')

# %%

riverside_rc2_df = conform2_to_df(riverside_rc2_df, 'Race/Ethnicity')

# %%

riverside_rc1_df = race_prepare_type1_df(riverside_rc1_df)

# %%

riverside_rc_df = race_join_both_types(riverside_rc1_df, riverside_rc2_df, 'Riverside High School')

riverside_rc_df = get_percents(riverside_rc_df, '')

# %%

riverside_ec1_df, riverside_ec2_df = collect_enrollments(ENROLLPATH+'/enrollment_data', riverside, 'economic')

riverside_ec2_df = conform2_to_df(riverside_ec2_df, 'Economic Status')

riverside_ec1_df = econ_prepare_type1(riverside_ec1_df)

#There are 2 different counts/percentages for 2005 and 2006 --> why?
riverside_ec_df = econ_join_both_types(riverside_ec1_df,
                                        riverside_ec2_df,
                                        'Riverside High School')

#riverside_ec_df['total_calc'] = riverside_ec_df[['econ_disadv','not_econ_disadv']].apply(sum,axis=1)

riverside_ec_df = get_percents(riverside_ec_df, '', ['econ_disadv','not_econ_disadv'])

#%%
# riverside_ec_df.drop([5], axis =0)

#%%

#For Econ disadv the 585 Not Disadv, 976 Disadv data is represented in wisedash
#From df type 2
riverside_race_ses_df = join_many_cat_dfs(riverside_rc_df.drop([1272],axis=0),riverside_ec_df.drop([4], axis =0))
# %%

#LOAD IN ATTENDANCE DATA FILES
#MAYBE SPLIT FILES BY MEASURE CATEGORY
    #COULD MAKE CLASSES?

#LOAD IN DATA

wash = ['Washington Hi', 'WHS Information Technology']

wash_ac1_df, wash_ac2_df = collect_enrollments(ENROLLPATH+'/attendance_data', wash, 'attendance')

#%%
#Race/Ethnicity and Economic Stauts?
#Need to adapt the functiont to handle multiple categories
wash_ac2_df = conform2_to_df(wash_ac2_df,['Race/Ethnicity','Economic Status'])

#Need a bunch of functions just for attendance

# %%

ac_dict = {'race_ethnicity':'All Groups Combined',
            'economic_status': 'Both Groups Combined',
            'gender':'Both Groups Combined',
            'grade':'Grades PreK-12',
            'english_proficiency_status':'Both Groups Combined',
            'disability_status': 'Both Groups Combined'}

wash_ac1_df = attend_prepare_type1(wash_ac1_df, ac_dict)

# %%


#  wash_ac1_df[(wash_ac1_df['race_ethnicity'].isin(['All Groups Combined'])) &\
#           (wash_ac1_df['economic_status'].isin(['Both Groups Combined']))&\
#           ( wash_ac1_df['gender'].isin(['Both Groups Combined'])) &\
#            ( wash_ac1_df['grade'].isin(['Grades PreK-12'])) &\
#             ( wash_ac1_df['english_proficiency_status'].isin(['Both Groups Combined'])) &\
#              ( wash_ac1_df['disability_status'].isin(['Both Groups Combined']))   ]# %%


# %%
