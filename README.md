Markdown Documenter (mdoc)
==========================

  This program parses the INPUT markdown file into the OUTPUT markdown file
  and allows additional features that are not currently supported by GitHub
  as including a markdown file inside another and execute MATLAB code from
  the INPUT file.

  Features of the parser:
  1. Include text from other file
  2. Execute code
  3. Comment
  4. Remove double intro


For more information please contact fersann1@upv.es

# Installation


# Table of contents

* [Installation](#installation)
* [Table of contents](#table-of-contents)
* [Parse](#parse)
* [Filters](#filters)
	* [Include text filter](#include-text-filter)
	* [Execute code filter](#execute-code-filter)
	* [Comment filter](#comment-filter)
	* [Remove double intro filter](#remove-double-intro-filter)
	* [Table of contents filter](#table-of-contents-filter)


# Parse

  Parse the INPUT file through the pipeline and show the result in the
  stdout. There are options (-o, --md) for creating output  files with the
  result.

  The pipeline is set by the following filters:

       1. Comment filter
       2. Include file filter
       3. Table of contents filter
       4. Execute code filter

  The input file is first processed by the first filter, the output of that
  filter is used as an input for the second filter and so on.


# Filters

## Include text filter

  This filter includes text from other file.

       @[ini,end](/path/to/file)

  With "ini" and "end" options you can specify to only include a part of the
  text to include. For example,

       @[ini:%% 1,end=%%](./myMatlab.m)

  Will include only the text between the first appearance of "%% 1" and the
  next "%%".

## Execute code filter

  This filter executes code and write the output of the execution in the
  file.

       ```LANGUAGE exec [OPTIONS]
       [Code to be execute]
       ```

  Where LANGUAGE is the programming language of the code. Currently only
  MATLAB and BASH code are supported.

  Pro Tip: you can execute python code if you execute like a bash command:

       ```sh exec
       python3 myPythonProgramm.py
       ```

  OPTIONS

       --path /path/to/workspace 
                       Define the workspace path.
       --no-code       Do not return the code itself.
       --no-echo       Do not return the result of the code.
       --raw           Print the output of the command as it is, without the ```

  For example:

       ```sh exec --no-code --path /home/user/path/to/folder --raw
       ls
       ```

  This will print the contents of /home/user/path/to/folder as plain text
  without the code.


## Comment filter

  This filter removes all text between the "<!--" and "-->" marks. For
  example:

      Text to keep in the document.
      <!--
      Text to remove.
      More text to remove.
      -->
      Text to also keep in the document.

  , will become:

      Text to keep in the document.
      Text to also keep in the document.

## Remove double intro filter

  This filter removes extra intros in the document. For example:

      The following text:

      "This text has

      double intros"

  , will become:

      "This text has
      double intros"

## Table of contents filter

  This filter creates a table of contents from the headers defined in
  markdown style.

  To include a table of contents in your code you have to add:

       [TOC]

  , then it will search all the headers and subheaders and it will produce
  something like this:

       * [Introduction](#introduction)
       * [Table of contents](#table-of-contents)
       * [Installation](#installation)
               * [System requirement](#system-requirement)
       * [Usage](#usage)
