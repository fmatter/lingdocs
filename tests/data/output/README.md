# Pylingdocs: A Demo

1.  [Introduction
    <a id>=‘sec:intro’\><a/>](#introduction-a-id-sec-intro-a)
2.  [Common markdown](#common-markdown)
3.  [Pylingdocs markdown
    <a id>=‘pld-md’\><a/>](#pylingdocs-markdown-a-id-pld-md-a)
4.  [Other linguistic data
    <a id>=‘sec:data’\><a/>](#other-linguistic-data-a-id-sec-data-a)
    1.  [Native CLDF components](#native-cldf-components)
    2.  [Non-native components](#non-native-components)
5.  [Interlinear examples](#interlinear-examples)
6.  [Citing literature
    <a id>=‘sec:sources’\><a/>](#citing-literature-a-id-sec-sources-a)
7.  [References](#references)

# Introduction <a id>=‘sec:intro’\><a/>

This document does double service as a test for `pylingdocs` and a
showcase of its capabilities. It aims to demonstrate every feature and
model currently available in `pylingdocs`.

# Common markdown

You can use all the familiar markdown components. Here is a link to the
[pylingdocs github repo](https://github.com/fmatter/pylingdocs/). Here
is some **bold** and *italic* and ***bold italic*** text.

1.  here
2.  is
3.  a
4.  numbered
5.  list

and of course here is

-   and one
-   with
-   bullet points[^1]

A quote:

> Locating an individual language on a given point of the
> ergativity-nominativity axis and the diachronic interpretation of this
> axis seem to be conceptually different concerns, even if we were to
> assume that there are principies favouring one direction over the
> other. ([Álvarez 1997](#source-alvarez1998split): 71)

# Pylingdocs markdown <a id>=‘pld-md’\><a/>

Apart from database references, discussed in
<a href='#sec:sources'>click</a>, there are a number of
`pylingdocs`-specific commands, all patterning like links:

-   cross-references: <a href='#common-markdown'>click</a> or
    <a href='#sec:intro'>click</a>, see corresponding `label` commands
-   example references:
    -   single \[ex:ekiri-13\]
    -   subexample \[ex:ekiri-10\]
    -   range: \[ex:ekiri-13–ekiri-11\]
    -   or bare: \[ex:ekiri-11\]
-   glosses: ACC
-   todos: \[todo: we need to talk about this\]
-   tables (with automatically generated table labels like \[Table\]):

|           | bilabial | alveolar | palatal | velar | glottal |
|:----------|:---------|:---------|:--------|:------|:--------|
| occlusive | /p /     | /t /     | /t͡ʃ/    | /k/   |         |
| nasal     | /m /     | /n /     | /j/     |       |         |
| fricative |          | /s /     |         |       | /j /    |
| liquid    |          | /r /     |         |       |         |
| glide     | /w /     |          | /y/     |       |         |

-   figures (with automatically generated table labels like
    <a href='#fig:cognates'>click</a>):

\[Cognate identification strategy: cognates.jpg\]

# Other linguistic data <a id>=‘sec:data’\><a/>

## Native CLDF components

-   Tiriyó pakoro se wae ‘I want a house’ ([Meira
    1999](#source-triomeira1999): 417)
-   Hixkaryána

louse-1

| Form    | Language | \-  | \-  | \-  | \-  | \-  |
|:--------|:---------|:----|:----|:----|:----|:----|
| *jamï*  | Tiriyó   | \-  | j   | a   | m   | o   |
| *azamo* | Apalaí   | a   | z   | a   | m   | o   |
| *əjamo* | Wayana   | ə   | j   | a   | m   | o   |

## Non-native components

Tiriyó *-e* ‘SUP’ is a variant of *-(s)e*. Neither occur on , because it
is a noun. They are related to *-se* and *-(h)e*. This is thus a cognate
set shared by Apalaí, Tiriyó, and Wayana.

-   If has too long a translation, try .

-   This dataset contains the Ikpeng text “The old man”.

# Interlinear examples

> (ekiri-13) Ikpeng
> <pre>
> nen        tan   nen        ɨ-wɨ-n  
> INAN.PROX  here  INAN.PROX  1POSS-machete-PERT  
> ‘“My machete is here.”’</pre>

()

1)  Ikpeng (ekiri-9)  
    otumunto  mun        eto     ɨ-wɨ-n              otumunto  
    where     INAN.DIST  UNCERT  1POSS-machete-PERT  where  
    ‘“Where might my machete be, where?”’

2)  Ikpeng (ekiri-10)  
    nen-to         nen-to         j-eŋ-lɨ      ɨ-wɨ-n  
    INAN.PROX-LOC  INAN.PROX-LOC  1\>3-put-HOD  1POSS-machete-PERT  
    ‘“Here, here I put my machete.”’

> (ekiri-11) Ikpeng
> <pre>
> an-k-aŋ         man  i-mu-n  
> 3-say-REM.CONT  AFF  3>3-son-PERT  
> ‘His son said:’</pre>

# Citing literature <a id>=‘sec:sources’\><a/>

-   see [Álvarez 1997](#source-alvarez1998split) or [Álvarez
    1997](#source-alvarez1998split): 133-134
-   with parentheses:
    -   “Locating an individual language on a given point of the
        ergativity-nominativity axis and the diachronic interpretation
        of this axis seem to be conceptually different concerns”
        ([Álvarez 1997](#source-alvarez1998split))
    -   “Locating an individual language on a given point of the
        ergativity-nominativity axis and the diachronic interpretation
        of this axis seem to be conceptually different concerns”
        ([Álvarez 1997](#source-alvarez1998split): 71)
-   multiple citations:
    -   [Álvarez 1997](#source-alvarez1998split): 133-134, [Meira
        1999](#source-triomeira1999): 218
    -   ([Álvarez 1997](#source-alvarez1998split): 133-134, [Meira
        1999](#source-triomeira1999): 218)

# References

-   <a id="source-alvarez1998split"> </a>Álvarez, José. 1997. Split
    Ergativity and Complementary Distribution of NP’s and Pronominal
    Affixes in Pemón (Cariban). Opción 13. 69–94.
-   <a id="source-triomeira1999"> </a>Meira, Sérgio. 1999. A Grammar of
    Tiriyó. (Doctoral dissertation).

[^1]: And here is a (foot)note. You can use markdown in here: see
    <a href='#sec:data'>click</a> for details about *-se* ‘SUP’.