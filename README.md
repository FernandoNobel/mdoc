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
* [Filters](#filters)
	* [Include text filter](#include-text-filter)
	* [Execute code filter](#execute-code-filter)
	* [Comment filter](#comment-filter)
	* [Remove double intro filter](#remove-double-intro-filter)


# Filters

## Include text filter

  INCLUDE TEXT FROM OTHER FILE

  You can include text from other file.

       @[ini,end](/path/to/file)

  With "ini" and "end" options you can specify to only include a part of the
  text to include. For example,

  @[ini:%% 1,end=%%](./myMatlab.m)

  Will include only the text between the first appearance of "%% 1" and the
  next "%%".

## Execute code filter

  EXECUTE CODE

  You can execute code and write the output of the execution.

       ``` LANGUAGE exec [OPTIONS]
       [Code to be execute]
       ```

  OPTIONS

  --path /path/to/workspace    Define the workspace path.
  --no-code    Do not return the code itself.
  --no-echo    Do not return the result of the code.


## Comment filter

  This filter removes all text between the "<!--" and "-->" marks. For
  example:

      Text to keep in the document.
      <!--
      Text to remove.
      More text to remove.
      -->
      Text to also keep in the document.

## Remove double intro filter

  This filter removes extra intros in the document. For example:

      The following text:

      "This text has

      double intros"

      will become:

      "This text has
      double intros"
