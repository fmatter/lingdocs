# Configuration

By default, `pylingdocs` uses the config file shown below. The values in
it can be overridden by creating a file `pylingdocs.cfg` in the
directory where you are executing `pylingdocs`.


{!src/pylingdocs/data/config.yaml!}


## Configuring examples

While pylingdocs takes care of the formatting of examples, there are
some parameters you might want to modify. The following table shows the
basic layout; `[]` mark optional content.


  (exno)    |[LANGUAGE/TITLE   [(SOURCE)]]
  --------- |---------------------------------------
            |[PRIMARY TEXT]
            |OBJECT LINE
            |GLOSS LINE
            |'TRANSLATION'  [(COMMENT)]  [(SOURCE)]

-   show primary text?
-   show language?
-   title?
-   show source?
-   show source where?
-   show comment?

default language from config override by example basis multiple lgs in
one ex -\> always label templates get values from central method
