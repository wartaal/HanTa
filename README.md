# HanTa - The Hanover Tagger 

HanTa is a pure Python package for lemmatization and POS tagging of Dutch, English and German sentences. The approach is to some extent language indpendent and language models for more langauges will be added in future.

Lemmatization and POS tagging are based on the morphological analysis of a word. The morphological analysis is done by an Hidden Markov Model that tries to find the best sequence of morphemes underlying each word.

## Usage

First a model has to be loaded:

```python

from HanTa import HanoverTagger as ht

tagger_de = ht.HanoverTagger('morphmodel_ger.pgz')
tagger_nl = ht.HanoverTagger('morphmodel_dutch.pgz')
tagger_en = ht.HanoverTagger('morphmodel_en.pgz')

```
Now we have three methods to anaylze words and sentences:

```python
tagger_en.tag_word('eating')
```

will give a list of all possible parts of speech (PoS) for the word *eating* together with a probability score.

```python
tagger_en.tag_word('eating')
```

The function analyze gives the most likely PoS and the lemma (VBG and *eat* in the exmaple below).

```python
tagger_en.analyze('unhappiest')
```

Using various optional parameters we can get more information like e.g. a list of morphemes:

```python
tagger_nl.analyze('huishoudhulpje',taglevel=3)
```

The last call producses the following output:

```
('huishoudhulp', [('huis', 'N(soort,onz)'), ('houd', 'WW'), ('hulp', 'N(soort,zijd)'), ('je', 'SUF_DIM')], 'N(soort,ev,dim,onz,stan)')
```

The package also contains a simple trigram based PoS tagger, that uses the probabilities from the morphological analysis for unknown words (and infrequent words from he training data).


```python
import nltk
from pprint import pprint

sent = "Die Europawahl in den Niederlanden findet immer donnerstags statt."

words = nltk.word_tokenize(sent)
lemmata = tagger.tag_sent(words)
pprint(lemmata)
```

## Further reading
For more information refer to the following resources:

* Demo.ipynb on GitHub (https://github.com/wartaal/HanTa)
* Manual - Coming soon
* Christian Wartena. A probabilistic morphology model for German lemmatization.
In *Proceedings of the 15th Conference on Natural Language Processing
(KONVENS 2019): Long Papers*, pages 40–49, Erlangen, Germany, 2019.
German Society for Computational Linguistics & Language Technology. [Online Available](https://doi.org/10.25968/opus-1527)