import sys
import json

from os import listdir, walk
from os.path import isfile, join, abspath

def hello():
    print("Hello World!")

# load_json_file takes a JSON file path
# and returns a JSON object of it.
def load_json_file(file):
    with open(file) as f:
        try:
            episode_mapping = json.load(f)
        except ValueError as e:
            print("Failed to load the file \"{}\": {}".format(file, e))
            exit

    return episode_mapping

def get_files_from_directories(directory, recurse=False):
    video_files = list_mkv_files_in_directory(directory)
    if recurse: # check if subdirectories should be searched
        subdirs = [x[0] for x in walk(directory)] #recursively get all subdirectories
        #print(subdirs)
        for dir in subdirs[1:]: # loop through directories, skipping the first one (the root directory) as it's already done
            video_files += list_mkv_files_in_directory(dir)
    return video_files

# list_mkv_files_in_directory returns all the files in the specified
# directory that have the .mkv extention
def list_mkv_files_in_directory(directory):
    #get all filepaths for files in directory
    files = [f for f in listdir(directory) if (isfile(join(directory, f)) and "mkv" in f)]
    paths = []
    for f in files:
        paths.append(abspath(join(directory,f))) #get absolute path for each file
    return paths
    #return [f for f in listdir(directory) if (isfile(join(directory, f)) and "mkv" in f)]

if __name__ == "__main__":
    print("Don't run this file... Try RTFM!")
    sys.exit()