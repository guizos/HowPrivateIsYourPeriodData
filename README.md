# How Private Is Your Period? 
This repository holds the data used for the paper:

```
How private is your period?: A systematic analysis of menstrual app privacy policies
Laura Shipp (Royal Holloway, University of London) and Jorge Blasco (Royal Holloway, University of London). 
Proceedings on Privacy Enhancing Technologies 2020 (PoPETs 2020)(link to be added)
```

The data includes the following:

- `PrivacyPolicyTextFiles`: Includes txt files with the privacy policies analysed in the paper. Several apps didn't had privacy policies and a few apps shared privacy policies.
- `OtherResources`: Includes other resources we used in the paper. 
  - `apps_sha256.txt`: The sha256 hash of all the apps analysed in the paper. They should be available from common Android app repositories such as Androzoo, etc.
  - `LanguageAnalysis.xlsx`: File with language statistics extracted from the privacy policy files.
  - `Libraries`: Folder with the results from executing LibScout and a few scripts to interpret the obtained results.
  - `policy_analyser.py`: Code that checks for presence of words and extracts readability scores from the policy files. It has a main method but it should be used via an ipython console. The relevant methods are `extract_sentences_for_words` and `extract_readability_scores`.
  - `RelevantWords.txt`: Words used for the analysis of ambiguous language.


