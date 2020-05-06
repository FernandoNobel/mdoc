#!/usr/bin/env python3
import click
import os
import re
import io
from abc import ABC, abstractmethod
import subprocess
import time

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
@click.argument('output', type=click.File('w'))
@click.option('--no-exec', is_flag=True, help="Do not execute code.")
@click.option('--intro', is_flag=True, help="Remove double intros.")
def parse(input, output, no_exec, intro):
    """ Parse the INPUT file through the pipeline and generate the OUTPUT file
    """
    # Read all the file to process
    data = input.read()

    # Set up the pipeline of filters.
    pipeline = Pipeline()

    pipeline.addFilter( CommentFilter() )
    pipeline.addFilter( IncludeFileFilter() )
    pipeline.addFilter( TableOfContentsFilter() )

    pipeline.addFilter( ExecuteCodeFilter(no_exec) )

    if intro:
        pipeline.addFilter( RemoveExtraIntroFilter() )

    # Run the pipeline.
    data = pipeline.run(data)

    # Write data into out file.
    output.write(data)
    output.flush()

@cli.command(short_help='Include file filter')
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'))
def include(input,output):
    """ Parse the INPUT file through the include filter and generate the OUTPUT
    file

    INCLUDE TEXT FROM OTHER FILE

    You can include text from other file. 

    \t @[ini,end](/path/to/file)

    With "ini" and "end" options you can specify to only include a part of the
    text to include. For example,

    @[ini:%% 1,end=%%](./myMatlab.m)

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

    EXECUTE CODE

    You can execute code and write the output of the execution.

    \b
    \t ``` LANGUAGE exec [OPTIONS]
    \t [Code to be execute]
    \t ```

    OPTIONS

    \b
    --path /path/to/workspace \t Define the workspace path.
    --no-code \t Do not return the code itself.
    --no-echo \t Do not return the result of the code.
    --raw \t Print the output of the command as it is, without the ```
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

    \twill become:

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
          
   
       
       
if __name__ == '__main__':
    cli(obj={})
