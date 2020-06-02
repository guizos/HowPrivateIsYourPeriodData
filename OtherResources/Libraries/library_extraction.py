import argparse
import json
import logging
import os
import subprocess

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)

argparser = argparse.ArgumentParser(
    description='Third Party Library Extractor')

argparser.add_argument(
    '-i',
    '--input',
    required=True,
    help='path to text file or folder containing the json files to analyse')

argparser.add_argument(
    '-o',
    '--output',
    required=True,
    default='output.json',
    help='path to output file')


def analyse_folder(path_to_folder):
    result = {}
    for filename in os.listdir(path_to_folder):
        if filename[0] != ".":
            result[filename] = analyse_file(path_to_folder, filename)
    return result


def analyse_file(path_to_folder, filename):
    print(filename)
    file_path = os.path.join(path_to_folder, filename)
    if not (os.path.isfile(file_path)):
        logger.log(logging.ERROR, 'File {0} is not a valid file'.format(filename))
        pass
    filename_no_ext, file_extension = os.path.splitext(file_path)
    if file_extension == 'json':
        json_data = json.load(open(file_path,'r'))
        libraries = json_data['lib_matches']
        return list(set([library['libName'] for library in libraries]))
    else:
        lines = open(file_path).readlines()
        libraries = [line.split('name: ')[-1].replace('\n','') for line in lines if ('ProfileMatch' in line or 'LibraryIdentifier' in line) and 'name: ' in line]
        return list(set(libraries))



def main():
    args = argparser.parse_args()
    result = {}
    if (os.path.isdir(args.input)):
        result = analyse_folder(args.input)
    elif (os.path.isfile(args.input)):
        result = analyse_file(os.path.dirname(os.path.abspath(args.input)),os.path.basename(args.input))
    else:
        logger.log(logging.DEBUG,'No file or dir provided.')
    json.dump(result,open(args.output,'w'),ensure_ascii=False, indent=4)
    return 0


if __name__ == "__main__":
    main()