from pathlib import Path
from xml.etree import ElementTree as ET
from typing import List, Tuple
import re


def extract_bnc_sentences(sampler_dir: str = "./BNCSampler/XML/", bnc_dir: str = "./BNC/Texts/", max_files: int = None) -> List[List[Tuple[str, str, str]]]:
    """Extract sentences from BNC XML files.

    Only keeps sentences where all words have unambiguous POS tags.

    Args:
        bnc_dir: Path to the BNC Texts directory
        max_files: Maximum number of files to process (None for all files)

    Returns:
        List of sentences, where each sentence is a list of (word, pos, lemma, pos2) tuples pos2 is the c5 pos tag from the corresponding sentence in  the full BNC Corpus. 
    """
    sentences = []
    files_processed = 0
    nr_missing_sentences = 0

    bnc_path = Path(sampler_dir)
    xml_files = list(bnc_path.rglob("*.xml"))

    if max_files is not None:
        xml_files = xml_files[:max_files]

    for xml_file in xml_files:
        alt_file = get_corresponding_file(xml_file, bnc_dir)
        #print(alt_file)
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            alttree = ET.parse(alt_file)
            altroot = alttree.getroot()

            c5tags  = {}
            for wtext in altroot.iter('p'):
                for sentence in wtext.iter('s'):
                    key = ""
                    for elem in sentence:
                        if elem.tag == 'w':
                            key+= elem.text
                        elif elem.tag == 'mw':
                                for word_elem in elem.iter('w'):
                                    key+= word_elem.text
                    key = ''.join(c.lower() for c in key if c.isalpha())   
                    c5tags[key] = sentence     


            for wtext in root.iter('p'):
                for sentence in wtext.iter('s'):
                    snr = sentence.get('n', '0')
                    match = re.fullmatch(r'([0-9]*\()?0*([1-9][0-9]*)\)?', snr)
                    if match:
                        snr = match.group(2)
                    #altsent = altroot.find(f'wtext/div/p/s[@n="{snr}"]')
                    #altsent_words = []
                    sent_words = []
                    key = ""

                    for elem in sentence:
                        if elem.tag == 'w':
                            word_text = elem.text.strip()
                            key+= word_text
                            if " " in word_text:
                                sub_words = word_text.split()
                                for sub_word in sub_words:
                                    sent_words.append((sub_word.strip(), None, '')) 
                            else:
                                pos_tag = elem.get('type', '')
                                lemma = '' 
                                sent_words.append((word_text, pos_tag.strip(), lemma.strip()))

                        elif elem.tag == 'c':
                            punct_text = elem.text.strip()
                            pos_tag = elem.get('type', '')
                            lemma = punct_text

                            sent_words.append((punct_text.strip(), pos_tag.strip(), lemma.strip()))


                    key = ''.join(c.lower() for c in key if c.isalpha())
                    altsent = c5tags.get(key, None)
                    altsent_words = []
                    if altsent is  None:
                        nr_missing_sentences += 1
                        #print(f"Warning: No corresponding sentence found for SNR {snr} in file {alt_file}")
                    else:
                        for elem in altsent:
                            if elem.tag == 'w':
                                word_text = elem.text.strip()
                                pos_tag = elem.get('c5', '').split('-')[0]  # take only the first tag if multiple are present
                                lemma = elem.get('hw', '')
                                if pos_tag == 'NP0' and lemma.strip().lower() == word_text.strip().lower():
                                    lemma = word_text

                                if word_text:
                                    altsent_words.append((word_text, pos_tag.strip(), lemma.strip()))

                            elif elem.tag == 'c':
                                punct_text = elem.text.strip()
                                pos_tag = elem.get('c5', 'PUN').split('-')[0]
  
                                if punct_text:
                                    altsent_words.append((punct_text, pos_tag.strip(), punct_text))

                            elif elem.tag == 'mw':
                                for word_elem in elem.iter('w'):
                                    word_text = word_elem.text.strip()
                                    pos_tag = word_elem.get('c5', '').split('-')[0]
                                    lemma = word_elem.get('hw', '').strip()

                                    if word_text:
                                        altsent_words.append((word_text, pos_tag.strip(), lemma))
                                
                    
                    if len(sent_words) == len(altsent_words):
                        updated_sent_words = []
                          
                        for w1, w2 in zip(sent_words, altsent_words):
                            word = w1[0]
                            pos = w1[1] 
                            lemma = w2[2]
                            c5 = w2[1]
                            updated_sent_words.append((word,pos,lemma,c5))  # use lemma from alsent and add C5 tag from altsent
                            #updated_sent_words.append((w2[0], w2[1], w2[2])) 
                        sentences.append(updated_sent_words)
                    else:
                        nr_missing_sentences += 1

                    
            files_processed += 1
            if files_processed % 100 == 0:
                print(f"Processed {files_processed} files, {len(sentences)} sentences extracted.")

        except Exception as e:
            print(f"Error processing {xml_file}: {e}")
            continue

    print(f"Finished: Processed {files_processed} files")
    print(f"Extracted {len(sentences)}  sentences")
    print(f"Could not find corresponding sentences for {nr_missing_sentences} sentences in the sampler XML files.")

    return sentences


def get_corresponding_file(xml_file, bnc_dir):
    name = xml_file.stem
    subdir = Path(bnc_dir) / name[0] / name[:2]
    return subdir / (name + ".xml")


def write_morph_csv(path: str, data):
    """Write labeled morpheme data to a TSV file using the same format as the original script.

    Args:
        path: output file path
        data: iterable of tuples representing processed words
    """
    with open(path, "w", encoding="utf-8") as fout:
        for word in data:
            if len(word[-1]) == 3:
                print(*word, sep='\t', end='\n', file=fout)
            else:
                print(*word[:-1], sep='\t', end='\n', file=fout)
