import sys
import json
import shutil

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
            print("DRYRUN: mkdir \"{}\"".format(path))
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
                print("DRYRUN: mkdir \"{}\"".format(arc_path))
        else:
            print("Directory \"{}\" already exists, moving on...".format(folder_name))
    
    print("Successfully generated file structure in directory")

def copy_tvdb(directory, dry_run=False):
    #check if directory exists
    directory = join(directory, "One Piece [tvdb4-81797]")
    if not isdir(directory):
        sys.stderr.write("Directory \"{}\" doesn't exist".format(directory))
        sys.stderr.flush()
        raise NotADirectoryError(directory)
    
    print("Copying TVDB file to all subdirectories in \"{}\"".format(directory))
    
    #get all subdirectories
    subdirs = [x[0] for x in walk(directory)]
    #print(subdirs)
    
    #copy tvdb file to all subdirectories
    for dir in subdirs[1:]:
        if not dry_run:
            shutil.copy("tvdb4.mapping", dir)
        else:
            print("DRYRUN: copy \"tvdb4.mapping\" -> \"{}\"".format(dir))

def generate_tvdb(file, dry_run=False):
    print("Generating TVDB file from episodes-reference.json")

    episode_mapping = load_json_file(file)

    index = 1
    start_episode = 1
    end_episode = 1
    tvdb_mapping = []
    for arc in episode_mapping:
        tvdb_line = "{:02d}".format(index) + "|"
        max = -2 #assume positive episode numbers
        min = 99999
        
        for i in episode_mapping[arc].items():
            val = get_biggest_number_from_ref(i[1])
            if val > max:
                max = val
            val = get_smallest_number_from_ref(i[1])
            if val < min:
                min = val

        start_episode = min
        end_episode = max
        
        tvdb_line += "{:04d}".format(start_episode) + "|"

        if index == 1:
            end_episode = 3 #special case for first arc

        tvdb_line += "{:04d}".format(end_episode) + "|" + f"{arc} Arc"
        tvdb_mapping.append(tvdb_line)
        index += 1
        final_arc = f"{arc} Arc"
        #episode += 1

    finalLine = "{:02d}".format(index-1) + "|" + "{:04d}".format(start_episode) + "|"+"{:04d}".format(start_episode)+f"|{final_arc} (unknown length)"
    tvdb_mapping[-1] = finalLine
    
    if not dry_run:
        with open("tvdb4.mapping", "w") as f:
            for line in tvdb_mapping:
                f.write(line + "\n")
    else:
        print("DRYRUN: New \"tvdb4.mapping\" would be:")
        for line in tvdb_mapping:
            print(line)

############################
### Supporting Functions ###
############################

#get the biggest number from an episode number reference string
def get_biggest_number_from_ref(string):
    if string == "" or string is None:
        return -1
    string = string.split("-")[-1] #assume following episode will always be bigger
    
    
    val = string.split("E")[-1] #get value after "E"
    if val.isdigit():
        return int(val)
    else:
        return -1

#get the smallest number from an episode number reference string
def get_smallest_number_from_ref(string):
    if string == "" or string is None:
        return 9999
    string = string.split("-")[0] #assume following episode will always be bigger
    
    
    val = string.split("E")[-1] #get value after "E"
    if val.isdigit():
        return int(val)
    else:
        return 9999

if __name__ == "__main__":
    print("Don't run this file... Try RTFM!")
    sys.exit()