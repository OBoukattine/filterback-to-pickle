import glob, os
import argparse
import pathlib
from tqdm import tqdm
from astropy.time import Time
from astropy import units as u
import pandas as pd

def options():
    parser = argparse.ArgumentParser()
    general = parser.add_argument_group('Arguments')
    general.add_argument('-i', '--input', type=str, required=True,
                         help='Required, directory where the .fil files are stored. Usage: path/to/fil, do not append *.fil at the end of the string')
    general.add_argument('-o', '--output', type=str, required=True,
                         help='Required, directory where the txt documents are written to. if the folder does not exist, the script will create it.')
    general.add_argument('-p', '-pandas-pickle', type=str, required=False, help=
'Required to create pandas dataframe. specifiy the output pickle name. Do not append .pkl, only the name.')
    general.add_argument('-r', '-recursive', action='store_true',
                        help='Not-Required, This option will enable a recursive search for all .fil files in your input folder. Note: the recursive search is over all folders and files in your input path (not only subdirectories)')
    general.add_argument('-k', '-keyword-rec', type=str, help='Not-Required, use this option if you want to limit the recursive search to a certain keyword in the filename. Example: pr145 or lsi. Do not add *, only give the specific keyword.')

    general.add_argument('-t', '-tar-boolean', action='store_true',
                         help='Not-Required, option to tar the output files in the same folder. Default = False. The name of the tar-file is the name of the final output folder.')
    general.add_argument('-T', '--telescope', type=str, required=False, help=
'Not-Required, option to overwrite the telescope name when parsing into pickle file. Old telescope name will be stored in the .txt files. Option is mainly used when Telescope name is FAKE in filterbank.')
    general.add_argument('-test', action='store_true', help='Not-required, testing-modus. No command is given to system, but prints the commands that will be used.')
    
    return parser.parse_args()

def file_names(path_to_files, rec_bool=False, keyword=None, file_ex='.fil'):
    #Glob the directory and return are list with file names, standard is all fil, 
    #but can be overwritten to return txt files

    path_to_files = check_slash(path_to_files)
    
    if rec_bool:
        files = glob.glob(path_to_files + "**/*" + file_ex, recursive=True)

    else:
        files = glob.glob(path_to_files + "*" + file_ex )
    files.sort()

    #Drop files that do not contain the keyword.
    if keyword != None:
        files = [s for s in files if keyword in s]

    return(files)

def ex_command(cmd, test_function):
    "Check if test modus is given, then print. Otherwise excecute"
    if test_function:
        print(cmd)
    else:
        os.system(cmd)

def check_slash(path):
    "Check if the last character of a path is a slash, if not, then slash is appended"
    if path[-1] != "/":
        path = path + "/"
    return path

def create_dir(path_to_txt):
    "check if output folder is created, if not, create it"
    pathlib.Path(path_to_txt).mkdir(parents=True, exist_ok=True)

def str_to_int_or_float(val):
    try:
        return int(val)
    except:
        try:
            return float(val)
        except:
            return str(val)

def check_lenght_txt(txt_list, path_to_txt, test_function):
    "Function to check lenght of txt file, if not longer than 20 lines. The file is moved to another folder"
    
    for txt_file in txt_list:
        dummy_counter = 0
        with open(txt_file) as f:
            for line in f:
                dummy_counter += 1

        #number is chosen based on trial and error, 40 seems okay. so we filter anything below 20.
        if dummy_counter < 20:
            print("ATTENTION, something wrong with file", txt_file)
            print("file is moved to folder: /incomplete_files")
            create_dir(path_to_txt + "incomplete_files")
            
            mv_file_loc = path_to_txt +  "incomplete_files/" + os.path.basename(txt_file)
            mv_command = f"mv {txt_file} {mv_file_loc}"
            os.system(mv_command)

def txt_making(fil_list, path_to_txt, test_function):
    #Function to create txt files from filterbanks

    for f in tqdm(fil_list):
        #Remove ending type and append txt
        desfile = f.split("/")[-1][:-3] + 'txt'
        desfile = desfile.replace("./", "")

        #add / at the end of path to create correct folder structure
        path_to_txt = check_slash(path_to_txt)

        cmd = f"readfile {f} > {path_to_txt}{desfile}"
        ex_command(cmd, test_function)
            
    #Check lenght of txt files.
    txt_files = file_names(path_to_txt, file_ex ='.txt')
    check_lenght_txt(txt_files, path_to_txt, test_function)

def pickler(path_to_txt, output_name):

    txt_files = file_names(path_to_txt, file_ex ='.txt')
    dict_list = []
    
    print('----Creating pandas dataframe----')
    for file_name in tqdm(txt_files):
        #dummy dictionary which gets appended each loop
        d_dummy = {}

        #extract info out of file_name
        obs_info_list = (file_name.split("/")[-1]).split("_")
        scanname = obs_info_list[0]
        telescope_id = obs_info_list[1]
        scanname_id = obs_info_list[2]
    
        d_dummy["scan_name"] = scanname
        d_dummy["scan_no"] = scanname_id

        with open(file_name) as f:
            for line in f:
                
                if "=" in line:
                    what = line.split("=")[0]
                    what = what.lstrip().rstrip()

                    val = line.split("=")[-1]
                    val = val.lstrip().rstrip()

                    if what == "Telescope":
                        val = telescope_id

                        #When arg Telescope is True, and the name of the telescope in de pd will be changed
                        if args.telescope:
                            val = args.telescope

                    what = what.replace(" ", "_")       
                    val = val.replace(" ", "_")
                    d_dummy[what] = str_to_int_or_float(val)
        
        tempmjd = d_dummy["MJD_start_time"]
        tempscanl = d_dummy["Time_per_file_(sec)"]
        mjd_end = (Time(tempmjd, format='mjd') + tempscanl * u.second).value
        d_dummy["MJD_end_time"] = mjd_end
        
        #Append full file_name, for easy reference if there are duplicates or different resolutions.
        d_dummy["complete_filename"] = os.path.basename(file_name)
        dict_list.append(d_dummy)

    #create pandas dataframe
    df = pd.DataFrame(dict_list)

    #Saving
    path_to_pickle = check_slash(path_to_txt)   

    if output_name == None:
        output_name = scanname
 
    df.to_pickle(path_to_pickle + output_name + '.pkl')
    print(df)

def tar_making(path_to_txt, test_function):
    "Create a tarbal of the pkl+.txt file"

    #Define the place where the tar file must end up.
    tar_name = path_to_txt.split("/")[-1]  
    tar_place = path_to_txt + f"/{tar_name}.tar.gz"

    #split the path in a way to execute the tar command
    splitted_path_tar = path_to_txt.rsplit("/", 2)
    pwd_folder = splitted_path_tar[0] +'/' + splitted_path_tar[1] + "/"
    des_folder = splitted_path_tar[2] + "/"
    
    tar_cmd = f"tar -czf {tar_place} -C {pwd_folder} {des_folder}"
    ex_command(tar_cmd, test_function)
    
def main(args):
    #list of fil names
    fil_list = file_names(args.input, args.r, args.k, file_ex='.fil')
    
    #create directories 
    create_dir(args.output)
    
    #execute readfile and make a tar file
    txt_making(fil_list, args.output, args.test)
    
    #Make a pandas dataframe from all txt files 
    #Output is given as an argument, since all .txt files are already written to final location
    if not args.test and args.p != None:
        pickler(args.output, args.p)

    if args.t:
        tar_making(args.output, args.test)

if __name__ == "__main__":
    args=options()
    main(args)
