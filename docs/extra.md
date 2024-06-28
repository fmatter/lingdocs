# Extra

## Defining (glossing) abbreviations
In addition to abbreviations defined in the CLDF dataset, abbreviations can be provided in an `extra/abbreviations.csv` file, with `ID` and `Description` columns.
If the abbreviation cannot be represented as a bare `ID`, for instance s_a_, a `Name` column can be added.

## Creating an index

To create an index of topics, provide a file `topic_index.csv`,
containing a list of topics and corresponding (optionally
comma-separated) section tags:

  Topic               Sections
  ------------------- --------------------------------
  Spatial semantics   sec:locatives
  Possession          sec:possession,sec:nounphrases

