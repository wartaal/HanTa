# English Morpheme Training Data Builder

This repository contains scripts to build labeled morpheme training data for an English morphological analyzer. The data is derived from two corpora: the **BNC Sampler** (British English) and the **Brown Corpus** (American English). Words are segmented into stems and morphological suffixes/prefixes, each annotated with a morpheme type tag, producing a CSV file suitable for training  HanTa

## Prerequisites

Install the required Python packages:

```bash
pip install nltk hanta uwotm8
```

Also download the required NLTK data:

```python
import nltk
nltk.download('wordnet')
nltk.download('brown')
```

## Corpora

### BNC Sampler (required)

The BNC Sampler is a 2-million word sample of the British National Corpus, tagged with CLAWS7 POS tags. Download it from the Oxford Text Archive:

- **BNC Sampler**: https://hdl.handle.net/20.500.14106/2551

Extract the XML files into a directory, e.g. `./BNCSampler/XML/`.

### BNC Full Corpus (required)

The full BNC is needed to obtain gold-standard CLAWS5 tags and lemmas, which are used to cross-check and correct the Sampler annotations. Download it from the Oxford Text Archive:

- **BNC XML Edition**: https://hdl.handle.net/20.500.14106/2554

Both resources are freely available but require acceptance of the BNC User Licence. Extract the texts into a directory, e.g. `./BNC/Texts/`, preserving the original subdirectory structure (e.g. `Texts/A/A0/A00.xml`).

### Brown Corpus (optional)

The Brown Corpus is included in NLTK and does not need to be downloaded separately. It is used to add American English data to the training set. If you want to include it, run `retagbrown.py` first (see below).

## Usage

### Step 1 (optional): Retag the Brown Corpus

This script reads the Brown Corpus from NLTK, converts its Penn Treebank tags to CLAWS5, assigns lemmas, and writes a tagged file that can be passed to the main script. It requires a HanTa model trained on BNC (`morphmodel_en_gb.pgz`):

```bash
python retagbrown.py
```

Output: `BrownC5.txt`

### Step 2: Build the morpheme training data

This is the main script. It extracts sentences from the BNC Sampler XML, aligns them with the full BNC to obtain gold-standard tags and lemmas, converts CLAWS7 tags to CLAWS5, performs morphological segmentation (stems, suffixes, prefixes), and writes the labeled output.

```bash
python create_train_data_en.py \
    --sampler-dir ./BNCSampler/XML/ \
    --bnc-dir ./BNC/Texts/ \
    --out labeledmorph_en.csv
```

To include the Brown Corpus data:

```bash
python create_train_data_en.py \
    --sampler-dir ./BNCSampler/XML/ \
    --bnc-dir ./BNC/Texts/ \
    --brown-file BrownC5.txt \
    --out labeledmorph_en.csv
```

Run `python create_train_data_en.py --help` for all options.

## Output format

The output is a tab-separated file. Each row represents one morpheme token with the following fields:

```
sentence_nr  word  lemma  stem  pos_tag  morphemes  substitution
```

## File overview

| File | Description |
|------|-------------|
| `create_train_data_en.py` | Main pipeline script |
| `bnc_sampler_io.py` | Reads and aligns BNC Sampler and full BNC XML files |
| `bnc_sampler.py` | Converts CLAWS7 tags to CLAWS5 and normalizes lemmas for BNC Sampler data |
| `tag_mappings.py` | CLAWS7-to-CLAWS5 tag mapping table and related utilities |
| `lemmatize.py` | Rule-based lemmatizer for English |
| `morph_utils.py` | Morphological segmentation into stems, suffixes, and prefixes |
| `retagbrown.py` | Retags the Brown Corpus with CLAWS5 tags and lemmas |
