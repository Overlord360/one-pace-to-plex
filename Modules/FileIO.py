import sys
import json

from os import listdir, walk, mkdir
from os.path import isfile, join, abspath, isdir

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


#################################
### File Generation Functions ###
#################################

# Generate directory structure based on the TVDB file
def generate_file_structure(directory, dry_run=False):
    #check if directory exists
    if not isdir(directory):
        sys.stderr.write("Directory \"{}\" doesn't exist".format(directory))
        sys.stderr.flush()
        raise NotADirectoryError(directory)
    
    print("Generating file structure in directory \"{}\"".format(directory))

    #load the TVDB file
    with open("tvdb4.mapping") as f:
        tvdb_mapping = []
        for line in f:
            tvdb_mapping.append(line.strip().split("|"))
    
    path = join(directory, "One Piece [tvdb4-81797]")
    
    #create parent directory
    if not isdir(path):
        if not dry_run:
            mkdir(path)
        else:
            print("mkdir \"{}\"".format(path))
    else:
        print("Directory \"{}\" already exists, moving on...".format(path))
    
    #generate arc folders
    for arc in tvdb_mapping:
        
        arc_name = arc[-1].split(" Arc")[0] #get arc name without " Arc" at the end
        folder_name = f"Arc {arc[0]} - {arc_name}"

        arc_path = join(path, folder_name)
        if not isdir(arc_path):
            if not dry_run:
                mkdir(arc_path)
            else:
                print("mkdir \"{}\"".format(arc_path))
        else:
            print("Directory \"{}\" already exists, moving on...".format(folder_name))
    
    print("Successfully generated file structure in directory")


if __name__ == "__main__":
    print("Don't run this file... Try RTFM!")
    sys.exit()