import os
import sys
import gzip 
import re
import shutil
import bs4
import requests as req
from zipfile import ZipFile
from add_new_data import crawl_directory

#Background
#-----------------------////////-------------------------
# Until 2013, the Wisconsin Information Network for Successful Schools (WINSS) was an important data resource used by
#  education stakeholders to help all students meet and exceed expectations. A wide variety of data about academic performance,
#   attendance and behavior, staff and other school resources, and student demographics were provided through WINSS Data Analysis tools.

# In 2013, the Department of Public Instruction (DPI) unveiled the successor to WINSS, the Wisconsin Information System
#  for Education Data Dashboard (WISEdash). Between 2013 and 2015, WINSS data for more recent years gradually migrated to
#   WISEdash and another DPI data tool called the School District Performance Report (SDPR). As of September 2015, the WINSS
#    Data Analysis tool was no longer available.
# Data previously available on WINSS for earlier school years not covered by WISEdash and SDPR will continue to be accessible
#  in WINSS Historical Data Files. See "Where to Find Data for Specific Years"

#-----------------------////////-------------------------

def organize_files(fileName):
    pattern = r'[a-z]+'
    #for f in os.listdir(inner_dir):
    file_type = re.search(pattern, fileName).group(0)
    folder_name = '{0}_data'.format(file_type)
    if not os.path.isdir(folder_name):
        print('making folder name:{0}'.format(file_type))
        os.mkdir(folder_name)
    if not os.path.exists(folder_name+'/'+fileName):
        zipObj.extract(fileName, '.')
        shutil.move(fileName,folder_name+'/'+fileName)

if __name__ == "__main__":
    outpath = 'zips'
    records = req.get('https://dpi.wi.gov/wisedash/download-files/year')
    soup = bs4.BeautifulSoup(records.content, 'html.parser')
    mbyte=1024*1024

    for _link in soup.findAll("span", class_="file"):
        zipurl = _link.a['href']
        print(_link.a['href'])
        r = req.get(zipurl, stream=True)
        outfname = zipurl.split('/')[-1]
        if( r.status_code == req.codes.ok ) :
            fsize = int(r.headers['content-length'])
            print('Downloading {0} ({1}Mb)'.format( outfname, fsize/mbyte ))
            with open(outfname, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024): # chuck size can be larger
                    if chunk: # ignore keep-alive requests
                        fd.write(chunk)
                fd.close()
            with ZipFile(outfname, 'r') as zipObj:

                listOfFileNames = zipObj.namelist()
                    # Iterate over the file names
                for fileName in listOfFileNames:
                    # Check filename endswith csv
                    organize_files(fileName)
            os.remove(outfname)
                        