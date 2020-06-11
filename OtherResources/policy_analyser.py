import argparse
import logging
import os
import en_core_web_lg
import spacy
from spacy.matcher.matcher import Matcher
from spacy.symbols import nsubj, VERB
from spacy_readability import Readability

ADJECTIVE = 'adjective'

VERB = "verb"

ADVERB = 'adverb'



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
    description='Privacy policy analyser')

argparser.add_argument(
    '-i',
    '--input',
    required=True,
    help='path to text file or folder containing privacy policies')

argparser.add_argument(
    '-adv',
    '--output_adverbs',
    required=False,
    default='.',
    help='path to output adverbs folder')

argparser.add_argument(
    '-adj',
    '--output_adverbs adjectives',
    required=False,
    default='.',
    help='path to output folder')

nlp = en_core_web_lg.load()

def analyse_folder(path_to_folder,output_adverbs,output_adjectives):
    for filename in os.listdir(path_to_folder):
        analyse_file(path_to_folder,filename,output_adverbs,output_adjectives)

def analyse_file(path,filename,output_adverbs,output_adjectives):
    file_path = os.path.join(path,filename)
    if not (os.path.isfile(file_path)):
        logger.log(logging.ERROR,"File {0} is not a valid file".format(filename))
    with open(file_path, 'r') as myfile:
        data = myfile.read()
        doc =  nlp(data)
        adj_pattern = [{'POS': 'ADJ'}]
        adv_pattern = [{'POS': 'ADV'}]
        matcher = Matcher(nlp.vocab)
        matcher.add("Adjectives", None, adj_pattern)
        matcher.add("Adverbs", None, adv_pattern)
        matches = matcher(doc)
        adverbs = {}
        adjectives = {}
        for match_id, start, end in matches:
            string_id = nlp.vocab.strings[match_id]  # Get string representation
            span = doc[start:end]  # The matched span
            text_to_check = span.text.lower()
            if doc[start].pos_ =="ADV":
                if text_to_check in adverbs.keys():
                    adverbs[text_to_check] +=1
                else:
                    adverbs[text_to_check] = 1
            elif doc[start].pos_ =="ADJ":
                if text_to_check in adjectives.keys():
                    adjectives[text_to_check] +=1
                else:
                    adjectives[text_to_check] = 1
        with open(os.path.join(output_adverbs,"{0}_adv.txt".format(filename)),'w') as adverb_file:
            for key in adverbs:
                adverb_file.write("{0}: {1}\n".format(key,adverbs[key]))
        with open(os.path.join(output_adjectives, "{0}_adj.txt".format(filename)), 'w') as adjective_file:
            for key in adjectives:
                adjective_file.write("{0}: {1}\n".format(key, adjectives[key]))
            #print(match_id, string_id, start, end, span.text, doc[start].pos_, doc[start].tag_)

def generate_list_of_words(folder_files, output_file):
    words = set()
    for filename in os.listdir(folder_files):
        if filename[0] != ".":
            with open(os.path.join(folder_files, filename), 'r') as myfile:
                print(filename)
                lines = myfile.readlines()
                words.update([line[0:line.index(":")] for line in lines if line[0] != "-"])
    with open(output_file, "w") as kept_file:
        for adverb in words:
            kept_file.write("{0}\n".format(adverb))

def generate_adverb_lists(adverb_folder,kept_output_file,removed_output_file):
    # Read all the files of privacy policies
    removed_adverbs = set()
    kept_adverbs = set()
    for filename in os.listdir(adverb_folder):
        if filename[0] != ".":
            with open(os.path.join(adverb_folder, filename), 'r') as myfile:
                print(filename)
                lines = myfile.readlines()
                removed_adverbs.update([line[1:line.index(": ")] for line in lines if line[0] == "-"])
                kept_adverbs.update([line[0:line.index(":")] for line in lines if line[0] != "-"])
    with open(kept_output_file, "w") as kept_adverbs_file:
        for adverb in kept_adverbs:
            kept_adverbs_file.write("{0}\n".format(adverb))
    with open(removed_output_file, "w") as removed_adverbs_file:
        for adverb in removed_adverbs:
            removed_adverbs_file.write("{0}\n".format(adverb))

def extract_readability_scores(policy_folder):
    read = Readability()
    nlp.add_pipe(read, last=True)
    print ("Policy, Grade, Ease")
    for filename in os.listdir(policy_folder):
        if filename[0] != ".":
            with open(os.path.join(policy_folder, filename), 'r') as myfile:
                data = myfile.read()
                doc = nlp(data)
                print("{0}, {1}, {2}".format(filename,doc._.flesch_kincaid_grade_level,doc._.flesch_kincaid_reading_ease))


def extract_sentences_for_words(word_file, policy_folder, output_file,stats_file):
    with open(word_file, 'r') as words, open(output_file, 'w') as output, open(stats_file,'w') as stats:
        words_and_kinds = [word.split(" : ") for word in words.readlines()]
        stats.write('policy, adverbs, adjectives, verbs, sentences, max_sentences\n')
        for filename in os.listdir(policy_folder):
            if filename[0]!=".":
                output.write("==================== {0} ====================\n".format(filename))
                with open(os.path.join(policy_folder,filename), 'r') as myfile:
                    adverb_stats = 0
                    adjective_stats = 0
                    verb_stats = 0
                    sentence_stats = 0
                    data = myfile.read()
                    doc = nlp(data)
                    for sent in doc.sents:
                        words = [row[0] for row in words_and_kinds]
                        kinds = [row[1].replace("\n","") for row in words_and_kinds]
                        if any(word in sent.text.split(' ') for word in words):
                            indices = [i for i, x in enumerate(words) if x in sent.text.split(' ')]
                            kinds_matched = list(map(lambda x: kinds[x],indices))
                            if VERB in kinds_matched:
                                for possible_subject in sent:
                                    if not (possible_subject.dep == nsubj and possible_subject.head.pos == VERB \
                                            and possible_subject.text.lower() in ['you', 'we', 'i', filename[
                                                                                                    filename.index(
                                                                                                        ' '):].strip().lower()]):
                                        indices = [x for x in indices if kinds[x] != VERB]
                            matches = [word for word in words if word in sent.text.split(' ')]
                            sentence_stats = sentence_stats + 1
                            output.write("== MATCHES: {0} ==\n{1}\n".format(matches, sent.text.replace("\n", "")))
                            for match in matches:
                                kind = kinds[words.index(match)]
                                if kind == VERB:
                                    verb_stats = verb_stats +1
                                elif kind == ADJECTIVE:
                                    adjective_stats = adjective_stats +1
                                elif kind == ADVERB:
                                    adverb_stats = adverb_stats + 1
                    stats.write("{0}, {1}, {2}, {3}, {4}, {5}\n".format(filename,adverb_stats,adjective_stats,verb_stats, sentence_stats, len(list(doc.sents))))


def extract_sentences_for_adjectives(advjectives_file,policy_folder,output_file):
    with open(advjectives_file, 'r') as kept_adverbs_file, open(output_file,'w') as output:
        kept_adverbs = [adv.replace("\n","") for adv in kept_adverbs_file.readlines() if adv[0]!='-']
        for filename in os.listdir(policy_folder):
            if filename[0]!=".":
                output.write("==================== {0} ====================\n".format(filename))
                with open(os.path.join(policy_folder,filename), 'r') as myfile:
                    data = myfile.read()
                    doc = nlp(data)
                    for sent in doc.sents:
                        if any(adverb in sent.text.split(' ') for adverb in kept_adverbs):
                            matches = [adverb for adverb in kept_adverbs if adverb in sent.text.split(' ')]
                            output.write("== MATCHES: {0} ==\n{1}\n".format(matches,sent.text.replace("\n","")))

def extract_sentences_for_verbs(verbs_file, policy_folder, output_file):
    with open(verbs_file, 'r') as kept_verbs_file, open(output_file, 'w') as output:
        kept_verbs = [adv.replace("\n","") for adv in kept_verbs_file.readlines() if adv[0]!='-']
        for filename in os.listdir(policy_folder):
            if filename[0]!=".":
                output.write("==================== {0} ====================\n".format(filename))
                with open(os.path.join(policy_folder,filename), 'r') as myfile:
                    data = myfile.read()
                    doc = nlp(data)
                    for sent in doc.sents:
                        if any(verb in sent.text.split(' ') for verb in kept_verbs):
                            for possible_subject in sent:
                                if possible_subject.dep == nsubj and possible_subject.head.pos == VERB \
                                        and possible_subject.text.lower() in ['you','we','i',filename[filename.index(' '):].strip().lower()]:
                                    matches = [verb for verb in kept_verbs if verb in sent.text.split(' ')]
                                    output.write("== MATCHES: {0} ==\n{1}\n".format(matches,sent.text.replace("\n","")))
                                    break

def extract_sentences_for_adverbs(adverbs_file,policy_folder,output_file):
    with open(adverbs_file, 'r') as kept_adverbs_file, open(output_file,'w') as output:
        kept_adverbs = [adv.replace("\n","") for adv in kept_adverbs_file.readlines() if adv[0]!='*']
        for filename in os.listdir(policy_folder):
            if filename[0]!=".":
                output.write("==================== {0} ====================\n".format(filename))
                with open(os.path.join(policy_folder,filename), 'r') as myfile:
                    data = myfile.read()
                    doc = nlp(data)
                    for sent in doc.sents:
                        if any(adverb in sent.text.split(' ') for adverb in kept_adverbs):
                            matches = [adverb for adverb in kept_adverbs if adverb in sent.text.split(' ')]
                            output.write("== MATCHES: {0} ==\n{1}\n".format(matches,sent.text.replace("\n","")))

def merge_relevant_word_files(adverb_files, adjective_files, verb_files, output_file):
    print("EnterHere")
    with open(output_file, 'w') as output:
        list(map(lambda x: map_words_with_kind(x,ADJECTIVE,output),adjective_files))
        list(map(lambda x: map_words_with_kind(x, ADVERB, output), adverb_files))
        list(map(lambda x: map_words_with_kind(x, VERB, output), verb_files))

def map_words_with_kind(filename, kind, output):
    print("{0},{1},{2}".format(filename,kind,output))
    with open(filename, 'r') as file_to_write:
        kept_words = [line.replace("\n", "") for line in file_to_write.readlines() if line[0] != '-' and line[0]!='-']
        list(map(lambda x: output.write("{0} : {1}\n".format(x,kind)), kept_words))

        #for token in doc:
        #    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
        #      token.shape_, token.is_alpha, token.is_stop)


def main():
    args = argparser.parse_args()
    if (os.path.isdir(args.input)):
        analyse_folder(args.input,os.path.abspath(args.output))
    elif (os.path.isfile(args.input)):
        analyse_file(os.path.dirname(os.path.abspath(args.input)),os.path.basename(args.input),os.path.abspath(args.output))
    else:
        logger.log(logging.DEBUG,"No file or dir provided.")
    return 0


if __name__ == "__main__":
    main()
