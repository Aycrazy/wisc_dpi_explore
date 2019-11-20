#%%
import pandas as pd
import numpy as np
import os
import sys
import re
import altair as alt
import bokeh as bk
#%%

ENROLLPATH = '/Users/ayaspan/Documents/Personal/wisconsin_enrollment'

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
                    type1_df = type1_df.append(pd.read_csv("{0}/{1}".format(dir,f)))
        else:
            type2_df =type2_df.append(pd.read_csv("{0}/{1}".format(dir,f)))

    #type1 df school select
    type1_ss_df = type1_df[type1_df['school_name'].isin(schools)]

    type2_df.rename(columns={ c:c.lower() for c in type2_df.columns}, inplace=True)
    
    print(type2_df.columns)

    type2_ss_df = type2_df[type2_df['school_name'].isin(schools)]

    
    return type1_ss_df, type2_ss_df
#%%

print(os.path)

wash1_df, wash2_df = collect_enrollments(ENROLLPATH+'/enrollment_data', ['Washington Hi','WHS Information Technology'], 'race')

#%%

#To get needed cols from type2
wash2_conf_df = wash2_df[wash2_df['group_by'].isin(['Race/Ethnicity','All Students'])][['school_year','group_by_value','student_count']].pivot(index='school_year', columns='group_by_value', values='student_count')

rep_cols2 = {c:c.lower().replace(' ','_') for c in wash2_conf_df.columns}

rep_cols2['All Students'] = 'total_enrollment'

wash2_conf_df.rename(columns=rep_cols2, inplace=True)

wash2_conf_df.reset_index(inplace=True)

wash2_conf_df['school_year'] = wash2_conf_df.school_year.apply(lambda x: re.search(r'\d+',x).group(0))


wash2_conf_df.columns

#%%

wash1_conf_df = wash1_df[['year','school_name', 'black_count', 'amer_indian_count', 'asian_count','hisp_count','pac_isle_count','white_count','two_or_more_count','total_enrollment_prek-12' ]]

rep_cols = {c:re.search(r'[a-z]+',c).group(0) for c in wash1_conf_df.columns if c not in ['school_name']}

rep_cols['amer_indian_count'] = 'amer_indian'
rep_cols['pac_isle_count'] = 'pacific_islander'
rep_cols['two_or_more_count'] = 'two_or_more'
rep_cols['hisp_count'] = 'hispanic'
rep_cols['year'] = 'school_year'

rep_cols['total_enrollment_prek-12'] = 'total_enrollment'

wash1_conf_df.rename(columns=rep_cols, inplace=True)

wash1_conf_df.columns

# %%

wash_df = wash1_conf_df.append(wash2_conf_df)

wash_df.school_year = wash_df.school_year.astype(int)

wash_df['school_name'] = 'Washington High School'

# %%

wash_df = wash_df[['amer_indian', 'asian', 'black', 'hispanic', 'pacific_islander','two_or_more', 'white']].fillna(0).astype(int)

wash_df['total_calc'] = wash_df[['amer_indian', 'asian', 'black', 'hispanic', 'pacific_islander','two_or_more', 'white']].apply(sum,axis=1)

# %%
