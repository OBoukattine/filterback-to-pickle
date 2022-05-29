# filterback-to-pickle
Instead of relying on observing schedules you can use this script to create an accurate log of your observations based on your created filterbank files. 
You point the script to your folder with filterbanks files and the script will create a pandas dataframe based on the output from Presto's readfile function. All outputted information from Presto's readfile is converted into a pandas .pkl file. Based on the MJD_start_time and observation length (Time_per_file), a MJD_stop_time is calculated using Astropy. Per filterbank a .txt file is saved and all observations are converted into a pickle file. For future reference, the complete filename including path is appended to the pandas dataframe. 

## Functionalities

- Script will skip filterbank files which are empty and throw an error. 
- Recursivly search through folders for filterbank files (-r).
- Use a keyword in order to constrain the processed filterbank files (-k).
- Tar the final folder of files (-t).

## Usage/Examples
### Help 
```
python /path_to_script/fil_to_txtpickle.py --help
```
### Process filterbank files in a single directory and createa a pickle log
```
python3 /path_to_script/fil_to_txtpickle.py -i /folder_to_filterbank_files -o /desired_output_folder -p name_of_pkl_file
```
### Recursive example 
```
python3 /path_to_script/fil_to_txtpickle.py -i /parent_folder -o /desired_output_folder -p name_of_pkl_file -k keyword -r
```

## Dependencies 
* Readfile function from [Presto](https://github.com/scottransom/presto)
* [Pandas](https://pandas.pydata.org/)
* [Astropy](https://www.astropy.org/)
* [tqdm](https://github.com/tqdm/tqdm)
* argparse, glob, pathlib
