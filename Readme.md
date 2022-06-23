# Plagiarism checker

This is a helping tool to check on plagiarism on different works, for example students' works assignments. One of the
advantages is that you do not need to edit .ipynb files manually. The program will handle them itself.

To use it u just need to run the program as shown below:

    python plagiarism_checker.py -p <path_to_files> -f <func_to_check> -e <files_extension>

This program will create a folder *path_to_files/plagiarism_result*s in which will store results as .csv files.

Arguments explanation:
- _**path_to_files**_ - The path to the directory where are the files you want to check

- _**func_to_check**_ - Specify the function by which you want to check plagiarism. Possible options:
    - _lev_ - Levenshtein distance;
    - _jaro_ - Jaro distance;
    - _seq_ - Sequence matcher;
    - _all_ - **by default**, so actually you can just skip this option;

- **_files_extension_** - Specify files extension, which you want to check. **By default** it will check all files in the given directory

Example of usage:

`python plagiarism_checker.py -p D:\files_path` (this will process all the files in the given directory by all possible
functions)

`python plagiarism_checker.py -p D:\files_path -f lev -e py` (this will process all the files with .py extension in the
given directory byLevenshtein distance functions)