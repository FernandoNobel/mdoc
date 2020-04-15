import click
import os
import re
import io

@click.command()
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'))
@click.option('--no-exec', is_flag=True, help="Do not execute code.")
def cli(input, output, no_exec):
    """MATLAB-DOCUMENTER

    This program parses the INPUT markdown file into the OUTPUT markdown file and allows additional features that are not currently supported by GitHub as including a markdown file inside another and excuting MATLAB code from the INPUT file.

    Include a external file. \t @[]()

    Execute the code: \t ``` * exec /path/to/workplace
    """
    # Read a line from input file.
    data = input.read()

    # Set up the pipeline of filters.
    pipeline = Pipeline()

    pipeline.addFilter( IncludeFileFilter() )

    if not no_exec:
        pipeline.addFilter( ExecuteCodeFilter() )

    pipeline.addFilter( RemoveExtraIntroFilter() )

    # Run the pipeline.
    data = pipeline.run(data)

    # Write data into outfile.
    output.write(data)
    output.flush()

class Pipeline:
    def __init__(self):
        self.filters = []

    def addFilter(self,f):
        # Add a new filter to the pipeline.
        self.filters.append(f)

    def run(self, data):
        for f in self.filters:
            data = f.process(data)

        return data

class Filter:
    def process(self,data):
        while True:
            searchObj = re.search(self.reg,data,re.M|re.I)
            if not searchObj:
                break
            handle = self.run(searchObj)
            data = re.sub(self.reg, handle, data, 1)
        return data

class IncludeFileFilter(Filter):
    def __init__(self):
        self.reg = r'@\[(.*?)]\((.*?)\)'

    def run(self, searchObj):
        opts = searchObj.group(1)
        opts = opts.replace('=',',')
        opts = opts.split(",")

        filepath = searchObj.group(2)

        f = open(filepath,'r')

        if not "ini" in opts:
            return  f.read()

        ini = opts[opts.index("ini")+1]
        end = opts[opts.index("end")+1]

        ini_found = -1
        handle = ""
        
        while True:
            # Read a line from input file.
            aux = f.readline()
            # In no line is read, end loop.
            if not aux:
                break
        
            if aux.find(end) != -1 and ini_found == 1:
                break
        
            if ini_found == 1:
                handle += aux
        
            if aux.find(ini) != -1:
                ini_found = 1

        return handle

class ExecuteCodeFilter(Filter):
    def process(self,data):
        reg_ini = r'```(.*?)exec(.*?)\n'
        reg_end = r'```\n'

        out_data = ''
        buf = io.StringIO(data)
        cmd = ''

        while True:
            line = buf.readline()
            if not line:
                break
            out_data += line

            searchObj = re.search(reg_ini,line,re.M|re.I)
            if searchObj:
                while True:
                    line = buf.readline()
                    out_data += line
                    if re.search(reg_end,line,re.M|re.I):
                        out_data += '``` ANS\n'

                        cmd = cmd.split('\n')
                        cmd = ','.join(cmd)
                        cmd = '\"cd ' + searchObj.group(2) +';' + cmd + ",exit;\""
                        cmd = 'matlab -nosplash -nodesktop -nodisplay -r ' + cmd

                        ans = os.popen(cmd).read()
                        ans = ans.split('\n')
                        ans = ans[11:]
                        ans.pop()
                        ans = '\n'.join(ans)

                        out_data += ans

                        out_data += '```\n'

                        break

                    else:
                        cmd += line

        return out_data

class RemoveExtraIntroFilter(Filter):
    def process(self,data):
        data = re.sub(r'\n\n', '\n', data, 0)
        return data
