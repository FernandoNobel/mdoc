#!/usr/bin/env python3
import click
import os
import re
import io
from abc import ABC, abstractmethod

@click.command()
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'))
@click.option('--no-exec', is_flag=True, help="Do not execute code.")
@click.option('--intro', is_flag=True, help="Remove double intros.")
def cli(input, output, no_exec, intro):
    """MATLAB-DOCUMENTER

    This program parses the INPUT markdown file into the OUTPUT markdown file
    and allows additional features that are not currently supported by GitHub as
    including a markdown file inside another and execute MATLAB code from the
    INPUT file.
    
    \b
    Features of the parser:
    1. Include text from other file
    2. Execute code

    # INCLUDE TEXT FROM OTHER FILE

    You can include text from other file. 

    \t @[ini,end](/path/to/file)

    With "ini" and "end" options you can specify to only include a part of the
    text to include. For example,

    @[ini:%% 1,end=%%](./myMatlab.m)

    Will include only the text between the first appearance of "%% 1" and the
    next "%%".
    

    - Execute the code: \t ``` * exec /path/to/workplace
    """
    # Read all the file to process
    data = input.read()

    # Set up the pipeline of filters.
    pipeline = Pipeline()

    pipeline.addFilter( CommentFilter() )
    pipeline.addFilter( IncludeFileFilter() )
    pipeline.addFilter( ExecuteCodeFilter() )

    #if not no_exec:
        #pipeline.addFilter( ExecuteCodeFilter() )

    if intro:
        pipeline.addFilter( RemoveExtraIntroFilter() )

    # Run the pipeline.
    data = pipeline.run(data)

    # Write data into out file.
    output.write(data)
    output.flush()

class Pipeline:
    """ PIPLINE

    This class manages and set up all the filters we want to use in the
    pipeline.
    """
    def __init__(self):
        """
        @brief: Constructor of Pipeline.
        """

        self.filters = [];

    def addFilter(self,f):
        """ ADDFILTER
        @brief: Add a filter to the pipeline.
        
        @param: f Filter object to add.
                
        @return: void
        """
        
        self.filters.append(f)

                
    def run(self,data):
        """ RUN
        @brief: Run all the filters in the pipeline.
        
        @param: data Text to process in the pipeline.
                
        @return: data Text processed.
        """

        # Run each filter.
        for f in self.filters:
            # Use the output of a filter as the input for the following one.
            data = f.run(data)

        return data

class Filter(ABC):
    """ FILTER

    Abstract filter class.
    """
    def __init__(self):
        """
        @brief: Constructor of Filter class.
        """

        super().__init__()

    @abstractmethod
    def run(self,data):
        """ RUN
        @brief: Run the filter
        
        @param: data Input text to process.
                
        @return: data Output text processed.
        """

        # Override this method.

    def searchReg(self,data,reg):
        """ SEARCHREG
        @brief: Search occurrence of regular expression in the text.
        
        @param: data Input text to process.
              : reg Regular expression to match in data.
                
        @return: searchObj Result of the regular expression search.
        """

        searchObj = re.search(reg,data,re.M|re.I)

        return searchObj

    def replaceReg(self,data,reg,text):
        """ REPLACEREG
        @brief: Replace the occurrence of a regular expression with text.
        
        @param: data Input text to process.
              : reg Regular expression to match in data.
              : text Text to replace with the regular expression match.
                
        @return: data Output text processed.
        """
                
        data = re.sub(reg, text, data, 1)

        return data


class RemoveExtraIntroFilter(Filter):
    """ REMOVEEXTRAINTROFILTER(FILTER)

    Remove extra intro in the text.
    """

    def run(self,data):
        """ RUN
        @brief: Run the filter.
        
        @param: data Input text to process
                
        @return: date Ouput text processed
        """

        data = re.sub(r'\n\n','\n',data,0)

        return data
    
class IncludeFileFilter(Filter):
    """ INCLUDEFILEFILTER(FILTER)

    Include text from other file.
    """

    def run(self,data):
        """ RUN
        @brief: Run the filter.
        
        @param: data Input text to process.
                
        @return: data Output text processed.
        """

        reg = r'@\[(.*?)]\((.*?)\)'

        while True:
            searchObj = self.searchReg(data,reg);
            # Exit the loop if nothing is found.
            if not searchObj:
                break
            text = self.includeFile(searchObj)
            data = self.replaceReg(data,reg,text)

        return data
                
    def includeFile(self,searchObj):
        """ INCLUDEFILE
        @brief: Search and return text to be included.
        
        @param: searchObj Result of regular expression search.
                
        @return: text Text to include.
        """

        opts = searchObj.group(1)
        opts = opts.replace('=',',')
        opts = opts.split(",")

        filepath = searchObj.group(2)

        f = open(filepath,'r')

        if not "ini" in opts:
            text =  f.read()

        else:
            ini = opts[opts.index("ini")+1]
            end = opts[opts.index("end")+1]

            ini_found = -1
            text = ""
        
            while True:
                # Read a line from input file.
                aux = f.readline()
                # In no line is read, end loop.
                if not aux:
                    break
            
                if aux.find(end) != -1 and ini_found == 1:
                    break
            
                if ini_found == 1:
                    text += aux
            
                if aux.find(ini) != -1:
                    ini_found = 1

        # Remove last intro in the file.
        text = text[:-1:]

        return text
           
class CommentFilter(Filter):
    """ COMMENTFILTER

    Remove commented text and avoids its processing in the pipeline.
    """
    
    def run(self,data):
        """ RUN
        @brief: Run the filter.
        
        @param: data Input text to process.
                
        @return: void Output text processed.
        """
        
        while True:
            # Search comment tags.
            commentStart = self.searchReg(data,r'<!--')
            commentEnd = self.searchReg(data,r'-->')
            
            # If not found anything, break loop.
            if not commentStart:
                break

            # Get index interval to delete.
            indexStart = commentStart.span(0)[0]
            indexEnd = commentEnd.span(0)[1]

            # Delete index interval.
            data = data[0: indexStart:] + data[indexEnd: :]

        return data

    
class ExecuteCodeFilter(Filter):
    """ EXECUTECODEFILTER(FILTER)

    Execute code and append the ouptut of the execution.
    """
    
    def run(self,data):
        """ RUN
        @brief: Run the filter.
        
        @param: data Input text to process.
                
        @return: dataOut Output text processed.
        """

        # Set a buffer with the data to process.
        buff = io.StringIO(data)

        dataOut = ''
        
        while True:
            # We process the data line per line.
            line = buff.readline()

            # If buff is ended, break the loop.
            if not line:
                break

            # Save lines readed in dataOut.
            dataOut += line

            # Look for the start of a code to execute.
            codeStart = self.searchReg(line, r'```(.*?)exec(.*?)\n')

            if not codeStart:
                continue

            code = ''

            # Read the code to execute.
            if codeStart:
                while True:
                    line = buff.readline()
                    if not line:
                        break
                    dataOut += line

                    # Look for the end of code to execute.
                    codeEnd = self.searchReg(line, r'```\n')

                    if codeEnd:
                        # Execute the code.
                        language = codeStart.group(1)
                        path = codeStart.group(2)

                        codeOut = self.executeCode(code,language,path)
                        dataOut += codeOut
                        break
                    else:
                        code += line

        return dataOut

    def executeCode(self,code,language,path):
        """ EXECUTECODE
        @brief: Execute the code.
        
        @param: code Code to execute.
              : language Code language (Matlab, python, etc)
              : path Path to the folder where the code has to be executed.
                
        @return: codeOut Output of the code.
        """

        languages = {
                'matlab':self.executeMatlabCode,
                'MATLAB':self.executeMatlabCode,
                'Matlab':self.executeMatlabCode
                }

        fnc = languages.get(
            language[:-1], 
            lambda code, path:'ERROR: Code language is not supported.'
            )
        
        codeOut = '```\n'
        codeOut += fnc(code,path)
        codeOut += '\n```\n'

        return codeOut

                
    def executeMatlabCode(self,code,path):
        """ EXECUTEMATLABCODE
        @brief: Execute matlab code.
        
        @param: code Code to execute.
              : path Path to the workspace.
                
        @return: codeOut Output of the code.
        """


        code = code.split('\n')
        code = ','.join(code)
        code = '\"cd ' + path  +';' + code + ",exit;\""
        code = 'matlab -nosplash -nodesktop -nodisplay -r ' + code
        
        ans = os.popen(code).read()
        ans = ans.split('\n')
        ans = ans[11:]
        ans.pop()
        ans = '\n'.join(ans)
        
        codeOut = ans

        return codeOut
        
    
#class exec(Filter):
#    def process(self,data):
#        reg_ini = r'```(.*?)exec(.*?)\n'
#        reg_end = r'```\n'
#
#        out_data = ''
#        buf = io.StringIO(data)
#        code = ''
#
#        while True:
#            line = buf.readline()
#            if not line:
#                break
#            out_data += line
#
#            searchObj = re.search(reg_ini,line,re.M|re.I)
#            if searchObj:
#                while True:
#                    line = buf.readline()
#                    out_data += line
#                    if re.search(reg_end,line,re.M|re.I):
#                        out_data += '``` ANS\n'
#
#                        code = code.split('\n')
#                        code = ','.join(code)
#                        code = '\"cd ' + searchObj.group(2) +';' + code + ",exit;\""
#                        code = 'matlab -nosplash -nodesktop -nodisplay -r
#                        ' + code
#
#                        ans = os.popen(code).read()
#                        ans = ans.split('\n')
#                        ans = ans[11:]
#                        ans.pop()
#                        ans = '\n'.join(ans)
#
#                        out_data += ans
#
#                        out_data += '```\n'
#
#                        break
#
#                    else:
#                        code += line
#
#        return out_data

if __name__ == '__main__':
    cli(obj={})
