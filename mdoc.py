import click
import os

@click.command()
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'))
def cli(input, output):
    """MATLAB-DOCUMENTER

    This program parses the INPUT markdown file into the OUTPUT markdown file and allows additional features that are not currently supported by GitHub as including a markdown file inside another and excuting MATLAB code from the INPUT file.
    """
    while True:
        # Read a line from input file.
        line = input.readline()
        # In no line is read, end loop.
        if not line:
            break

        line = includeFile(line);

        # Write line into outfile.
        output.write(line)
        output.flush()


def includeFile(line):
    # Look for markup of includind a file @[opts](path/file.md).
    if line.find("@[") == -1:
        return line

    # Get the options.
    opts = line[line.find("@[")+2:line.find("]")]
    opts = opts.replace('=',',')
    opts = opts.split(",")
    # Get the filepath.
    filepath = line[line.find("(")+1:line.find(")")]

    # Open the file to include.
    f = open(filepath,"r")

    line = "```"

    # Check if style is defined.
    if "style" in opts:
        line += opts[opts.index("style")+1]

    line += '\n'

    if "ini" in opts:
        ini = opts[opts.index("ini")+1]
        end = opts[opts.index("end")+1]
    else:
        ini = -1

    ini_found = -1
    cmd = ''

    while True:
        # Read a line from input file.
        aux = f.readline()
        # In no line is read, end loop.
        if not aux:
            break

        if ini != -1:
            if aux.find(end) != -1 and ini_found == 1:
                break

        if ini == -1 or ini_found == 1:
            line += aux
            cmd += aux

        if ini != -1:
            if aux.find(ini) != -1:
                ini_found = 1

    line += "```"

    if "exec" in opts:
        line += "\n```\n"

        cmd = cmd.split('\n')
        cmd = ','.join(cmd)
        cmd = '\"cd ' + os.path.dirname(filepath) +';' + cmd + ",exit;\""
        cmd = 'matlab -nosplash -nodesktop -nodisplay -r ' + cmd

        ans = os.popen(cmd).read()
        ans = ans.split('\n')
        ans = ans[11:]
        ans.pop()
        ans = '\n'.join(ans)
        line += ans

        line += "```"

    return line
