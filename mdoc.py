#!/usr/bin/env python3
import click
import os
import glob # For searching files in path.
import re

from Pipeline import Pipeline
from Filter import Filter
from IncludeFileFilter import IncludeFileFilter
from RemoveExtraIntroFilter import RemoveExtraIntroFilter
from CommentFilter import CommentFilter
from ExecuteCodeFilter import ExecuteCodeFilter
from TableOfContentsFilter import TableOfContentsFilter

class NaturalOrderGroup(click.Group):
    def list_commands(self, ctx):
        return self.commands.keys()

@click.group(cls=NaturalOrderGroup)
def cli():
    """MATLAB-DOCUMENTER

    This program parses the INPUT markdown file into the OUTPUT markdown file
    and allows additional features that are not currently supported by GitHub as
    including a markdown file inside another and execute MATLAB code from the
    INPUT file.
    
    \b
    Features of the parser:
    1. Include text from other file
    2. Execute code
    3. Comment
    4. Remove double intro
    """

@cli.command(short_help='Parse a file through the pipeline')
@click.argument('input', type=click.File('r'))
@click.option('-o','--output', type=click.File('w'), help="Generate an output file.")
@click.option('-m','--md', is_flag=True, help="Output a markdown file.")
@click.option('--no-exec', is_flag=True, help="Do not execute code.")
@click.option('--intro', is_flag=True, help="Remove double intros.")
@click.option('-v','--verbose', is_flag=True, help="Verbose output.")
def parse(input, output, md, no_exec, intro, verbose):
    """ Parse the INPUT file through the pipeline and show the result in the
    stdout. There are options (-o, --md) for creating output files with the result.

    The pipeline is set by the following filters:

    \b
    \t 1. Comment filter
    \t 2. Include file filter
    \t 3. Table of contents filter
    \t 4. Execute code filter

    The input file is first processed by the first filter, the output of that
    filter is used as an input for the second filter and so on.
    """
    # Prepare the options to pass for the filters.
    opts = [
            'no_exec', no_exec,
            'verbose', verbose
            ]

    # Read all the file to process.
    data = input.read()

    # Set up the pipeline of filters.
    pipeline = Pipeline()

    pipeline.addFilter( CommentFilter(opts) )
    pipeline.addFilter( IncludeFileFilter(opts) )
    pipeline.addFilter( TableOfContentsFilter(opts) )

    pipeline.addFilter( ExecuteCodeFilter(opts) )

    if intro:
        pipeline.addFilter( RemoveExtraIntroFilter(opts) )

    # Run the pipeline.
    data = pipeline.run(data)

    # If markdown flag is used, output the file as a originalName.md.
    if md:
        defaultName = os.path.splitext(input.name)[0] + '.md'
        output = open(defaultName,'w')

    if output:
        # Write data into out file.
        output.write(data)
        output.flush()
        return

    print(data)

@cli.command(short_help='Parse all the .mdoc files in the path provided.')
@click.argument('path',  type=click.Path(exists=True))
@click.option('-r','--recursive', is_flag=True, help="Find .mdoc recursively in the path.")
@click.option('--no-exec', is_flag=True, help="Do not execute code.")
@click.option('--intro', is_flag=True, help="Remove double intros.")
@click.option('-e','--exclude', help="Exclude the files from making.", multiple=True)
@click.pass_context
def make(ctx, path, recursive, no_exec, intro, exclude):
    """ Parse all the .mdoc files present in the PATH through the pipeline into
    .md files.

    The pipeline is set by the following filters:

    \b
    \t 1. Comment filter
    \t 2. Include file filter
    \t 3. Table of contents filter
    \t 4. Execute code filter

    The files are first processed by the first filter, the output of that
    filter is used as an input for the second filter and so on.
    """

    # Get the absolute path to avoid problems with relatives ones.
    path = os.path.abspath(path)

    # Move to the path chosed by user.
    os.chdir(path)

    # Get all the .mdoc files to parse.
    if recursive:
        files = glob.glob('./**/*.mdoc', recursive = True)
    else:
        files = glob.glob('./*.mdoc', recursive = False)


    # Remove exclude files from being processed.
    for expr in exclude:
        print(expr)
        pattern = re.compile(expr)

        result = []

        for file in files:
            filename = os.path.basename(file)

            if not pattern.match(filename):
                result.append(file)

        files = result

    print('Files to be parsed:')
    print(files)

    # Execute parse for all files.
    for file in files:
        print('Parsing %s' % file)

        # Change chdir to the one needed for the parse command.
        os.chdir(os.path.dirname(file))

        fd = open(os.path.basename(file),'r')
        ctx.invoke(parse, input = fd, output = False, md = True, no_exec
                = no_exec, intro = intro, verbose = True)

        # Change back the chdir to the main one.
        os.chdir(path)

@cli.command(short_help='Include text filter')
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'))
def include(input,output):
    """ Parse the INPUT file through the include text filter and generate the 
    OUTPUT file

    This filter includes text from other file. 

    \t @[ini,end](/path/to/file)

    With "ini" and "end" options you can specify to only include a part of the
    text to include. For example,

    \t @[ini:%% 1,end=%%](./myMatlab.m)

    Will include only the text between the first appearance of "%% 1" and the
    next "%%".
    
    """

    # Read all the file to process
    data = input.read()

    # Set up the pipeline of filters.
    pipeline = Pipeline()

    pipeline.addFilter( IncludeFileFilter() )

    # Run the pipeline.
    data = pipeline.run(data)

    # Write data into out file.
    output.write(data)
    output.flush()

@cli.command(short_help='Execute code filter')
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'))
@click.option('--no-exec', is_flag=True, help="Do not execute code.")
def exec(input,output,no_exec):
    """ Parse the INPUT file through the execute code filter and generate the
    OUTPUT file

    This filter executes code and write the output of the execution in the file.

    \b
    \t ```LANGUAGE exec [OPTIONS]
    \t [Code to be execute]
    \t ```

    Where LANGUAGE is the programming language of the code. Currently only
    MATLAB and BASH code are supported. 

    Pro Tip: you can execute python code if you execute like a bash command:

    \b
    \t ```sh exec
    \t python3 myPythonProgramm.py
    \t ```

    OPTIONS

    \b
    \t --path /path/to/workspace 
    \t\t\t Define the workspace path.
    \t --no-code \t Do not return the code itself.
    \t --no-echo \t Do not return the result of the code.
    \t --raw \t\t Print the output of the command as it is, without the ```

    For example:

    \b
    \t ```sh exec --no-code --path /home/user/path/to/folder --raw
    \t ls
    \t ```

    This will print the contents of /home/user/path/to/folder as plain text
    without the code.
    """

    # Read all the file to process
    data = input.read()

    # Set up the pipeline of filters.
    pipeline = Pipeline()

    pipeline.addFilter( ExecuteCodeFilter(no_exec) )

    # Run the pipeline.
    data = pipeline.run(data)

    # Write data into out file.
    output.write(data)
    output.flush()

@cli.command(short_help='Comment filter')
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'))
def comment(input,output):
    """ Parse the INPUT file through the comment filter and generate the OUTPUT
    file

    This filter removes all text between the "<!--" and "-->" marks. For
    example:

    \b
    \tText to keep in the document.
    \t<!--
    \tText to remove.
    \tMore text to remove.
    \t-->
    \tText to also keep in the document.

    , will become:

    \b
    \tText to keep in the document.
    \tText to also keep in the document.
    """

    # Read all the file to process
    data = input.read()

    # Set up the pipeline of filters.
    pipeline = Pipeline()

    pipeline.addFilter( CommentFilter() )

    # Run the pipeline.
    data = pipeline.run(data)

    # Write data into out file.
    output.write(data)
    output.flush()

@cli.command(short_help='Remove double intros filter')
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'))
def remove_intro(input,output):
    """ Parse the INPUT file through the remove double intros filter and
    generate the OUTPUT file

    This filter removes extra intros in the document. For example:

    \b
    \tThe following text:

    \t"This text has

    \tdouble intros"

    , will become:

    \b
    \t"This text has
    \tdouble intros"

    """

    # Read all the file to process
    data = input.read()

    # Set up the pipeline of filters.
    pipeline = Pipeline()

    pipeline.addFilter( RemoveExtraIntroFilter() )

    # Run the pipeline.
    data = pipeline.run(data)

    # Write data into out file.
    output.write(data)
    output.flush()
          
@cli.command(short_help='Create a table of contents')
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'))
def toc(input,output):
    """ Parse the INPUT file through the table of contents filter and
    generate the OUTPUT file

    This filter creates a table of contents from the headers defined in markdown
    style.

    To include a table of contents in your code you have to add:

    \t [TOC]

    , then it will search all the headers and subheaders and it will produce
    something like this:

    \b
    \t * [Introduction](#introduction)
    \t * [Table of contents](#table-of-contents)
    \t * [Installation](#installation)
    \t \t * [System requirement](#system-requirement)
    \t * [Usage](#usage)
    """

    # Read all the file to process
    data = input.read()

    # Set up the pipeline of filters.
    pipeline = Pipeline()

    pipeline.addFilter( TableOfContentsFilter() )

    # Run the pipeline.
    data = pipeline.run(data)

    # Write data into out file.
    output.write(data)
    output.flush()
       
if __name__ == '__main__':
    cli(obj={})
