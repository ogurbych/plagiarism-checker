import numpy as np
import pandas as pd
import glob
import re
import os
from pathlib import Path
from argparse import ArgumentParser, Namespace
from tqdm import tqdm
import subprocess
import string
import Levenshtein
from difflib import SequenceMatcher
import jellyfish


def jupyter_to_python(path_to_files: str):
    bash_command = f"jupyter nbconvert --output-dir='{path_to_files}' --to python {path_to_files}*.ipynb"
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()


def remove_punctuations(txt, punct=string.punctuation):
    return ''.join([c for c in txt if c not in punct])


def clean_text(txt):
    # Remove comments
    txt = re.sub("([\#]).*?([\\n])", "", txt)

    # Remove variables
    txt = re.sub("([\\n]).*?([\=])", "\g<1>\g<2>", txt)

    # Remove escape characters
    txt = txt.replace('\n', ' ').replace('\r', ' ').replace('\'', '')

    txt = remove_punctuations(txt)
    return txt.lower()


def similarity_levenshtein(work_to_check, reference):
    distances = []
    for content in reference:
        dist = Levenshtein.distance(work_to_check, content)
        distances.append(dist)

    distances_list = [[d, max(len(work_to_check), len(reference[idx]))] for idx, d in enumerate(distances)]

    sim_ratios = []
    for index, distances in enumerate(distances_list):
        lev_dist = distances[0]
        len_text = distances[1]
        sim_ratios.append(round((len_text - lev_dist) * 100 / len_text, 0))

    return sim_ratios


def similarity_jaro(work_to_check, reference):
    sim_ratios = []
    for content in reference:
        dist = jellyfish.jaro_distance(work_to_check, content)
        sim_ratios.append(round(dist * 100, 0))

    return sim_ratios


def similarity_seq(work_to_check, reference):
    sim_ratios = []
    for content in reference:
        dist = SequenceMatcher(None, work_to_check, content).ratio()
        sim_ratios.append(round(dist * 100, 0))

    return sim_ratios


def plagiarism_checker(path_to_files: str, list_of_funcs: list, files_ext: str):
    result_path = f'{path_to_files}plagiarism_results' + os.path.sep
    Path(result_path).mkdir(parents=True, exist_ok=True)

    if files_ext == '':
        list_of_works = [filename for filename in glob.glob(path_to_files + '*.*') if not filename.endswith('ipynb')]
    else:
        list_of_works = glob.glob(path_to_files + f'*{files_ext}')
    list_of_works = sorted(list_of_works)

    works_txt = []
    for work in list_of_works:
        with open(work, 'r') as file:
            works_txt.append(clean_text(file.read()))

    for sim_func in list_of_funcs:
        print(f'Plagiarism checking with {sim_func} function')

        works_plag_info_dict = {}
        for work_idx, work in enumerate(tqdm(works_txt)):
            work_name = Path(list_of_works[work_idx]).name

            if sim_func == 'lev':
                plag_info = similarity_levenshtein(work, works_txt)
            elif sim_func == 'jaro':
                plag_info = similarity_jaro(work, works_txt)
            else:
                plag_info = similarity_seq(work, works_txt)

            # Plagiarism with itself
            plag_info[work_idx] = np.NaN

            works_plag_info_dict[work_name] = plag_info

        df = pd.DataFrame(works_plag_info_dict, columns=works_plag_info_dict.keys())
        df.index = works_plag_info_dict.keys()
        df = df.transpose()

        df['Plagiated'] = np.where((df > 90).any(axis=0), 'True', 'False')

        if sim_func == 'lev':
            df.to_csv(f'{result_path}LevenshteinDist.csv', index=True)
        elif sim_func == 'jaro':
            df.to_csv(f'{result_path}JaroDist.csv', index=True)
        else:
            df.to_csv(f'{result_path}SequenceMatcher.csv', index=True)


def main(path_to_files: str, func_to_check: str, files_ext: str):
    if not files_ext or files_ext == '.ipynb':
        jupyter_to_python(path_to_files)
        files_ext = ''

    if func_to_check == 'all':
        list_of_funcs = ['lev', 'jaro', 'seq']
    else:
        list_of_funcs = [func_to_check]

    plagiarism_checker(path_to_files, list_of_funcs, files_ext)


if __name__ == '__main__':
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument('-p', action='store', type=str, dest='path_to_files', required=True,
                        help='Path to the files to be checked')
    parser.add_argument('-f', action='store', type=str, dest="func_to_check", default='all',
                        help="Function by which check similarity")
    parser.add_argument('-e', action='store', type=str, dest="files_extension", default=None,
                        help="Files extension you want to check")
    args: Namespace = parser.parse_args()

    if not args.path_to_files.endswith(os.path.sep):
        args.path_to_files += os.path.sep

    if args.files_extension and args.files_extension[0] != '.':
        args.files_extension = '.' + args.files_extension

    main(args.path_to_files, args.func_to_check, args.files_extension)
