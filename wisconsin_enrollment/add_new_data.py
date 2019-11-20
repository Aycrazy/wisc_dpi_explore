import os
import sys
import gzip 
import re
import shutil

ENROLLPATH = '/Users/ayaspan/Documents/Personal/wisconsin_enrollment'

#Add recursive element to find all csvs and orgnize accordingly?
def crawl_directory(inner_dir):
    #Crawl current directory for files, categorize by description pre "_"
    pattern = r'[a-z]+'
    for f in os.listdir(inner_dir):
        file_type = re.search(pattern, f).group(0)
        folder_name = ENROLLPATH+'/{0}_data'.format(file_type)
        if not os.path.isdir(folder_name):
            print('making folder name:{0}'.format(file_type))
            os.mkdir(folder_name)
        if os.path.exists(folder_name+'/'+f):
                continue 
        shutil.move(inner_dir+'/'+f,folder_name+'/'+f)


def crawl_all_dirs_with(dir, dir_start):
    #check all directories in outter director for inner directories that start with string

    rel_dirs = [inner_dir for inner_dir in os.listdir(dir) if inner_dir.startswith(dir_start)]

    for inner_dir in rel_dirs:
        if not inner_dir.endswith('.zip'):
            crawl_directory(dir+'/'+inner_dir)

if __name__ == "__main__":

    dir = sys.argv[1]

    dir_start = sys.argv[2]

    print(dir, dir_start)

    crawl_all_dirs_with(dir,dir_start)