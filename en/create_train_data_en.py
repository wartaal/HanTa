import argparse
from bnc_sampler_io import extract_bnc_sentences, write_morph_csv
from morph_utils import make_morph_lists, MorphemeAnalyzer
from tag_mappings import convert_bnc_sampler_to_claws5


def read_sentences(file_path):
    sentences = []
    sentence = []
    lastsnr = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            snr, word, pos, lemma = line.strip().split()
            if int(snr) != lastsnr and len(sentence) > 0:
                sentences.append(sentence)
                sentence = []
                lastsnr = int(snr)
            sentence.append((word, pos, lemma))
            
    return sentences

def main():
    parser = argparse.ArgumentParser(description='Build labeled morpheme CSV from BNC XML')
    parser.add_argument('--sampler-dir', default='./BNCSampler/XML/', help='Path to BNC Sampler XML directory')
    parser.add_argument('--bnc-dir', default='./BNC/Texts/', help='Path to BNC Texts directory')
    parser.add_argument('--brown-file', default=None, help='File with Brown Corpus')
    parser.add_argument('--max-files', type=int, default=200, help='Max number of XML files to process')
    parser.add_argument('--out', default='labeledmorph_en_bncs.csv', help='Output TSV file')
    args = parser.parse_args()

    sentences = extract_bnc_sentences(sampler_dir=args.sampler_dir, bnc_dir=args.bnc_dir, max_files=args.max_files)

    if sentences:
        total_tokens = sum(len(sent) for sent in sentences)
        print(f"\nTotal tokens: {total_tokens}")
        print(f"Total sentences: {len(sentences)}\n")
        

    sentences = convert_bnc_sampler_to_claws5(sentences)


    if args.brown_file:
        brown_sentences = read_sentences(args.brown_file)
        sentences.extend(brown_sentences)
    
    data = make_morph_lists(sentences)
    analyzer = MorphemeAnalyzer()
    analyzer.collect_morphemes(data)
    data = analyzer.postprocess_morphemes(data)


    write_morph_csv(args.out, data)
    print(f"Wrote output to {args.out}")


if __name__ == '__main__':
    main()
