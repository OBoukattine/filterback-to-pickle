# filterback-to-pickle
A python script to create a log of radio observations. 


## Example
For a single directory
```sh
python3 /path_to_script/fil_to_txtpickle.py -i /folder_to_filterbank_files -o /desired_output_folder -p name_of_pkl_file
```
```sh

Recursive example
```sh
python3 /path_to_script/fil_to_txtpickle.py -i /parent_folder -o /desired_output_folder -p name_of_pkl_file -k keyword -r
```
```sh

## Requirements

* readfile from [Presto](https://github.com/scottransom/presto)
* [Pandas](https://pandas.pydata.org/)
* [Astropy](https://www.astropy.org/)
* [tqdm](https://github.com/tqdm/tqdm)
* argparse, glob, pathlib
