from Filter import Filter
import os
import io
import subprocess
import re

class ExecuteCodeFilter(Filter):
    """ EXECUTECODEFILTER(FILTER)

    Execute code and append the ouptut of the execution.
    """

    def __init__(self,opts):
        """ __INIT__
        @brief: Init of the ExecuteCodeFilter.

        @params: opts General options from the execution of mdoc.
        """

        super().__init__(opts)
        self.matlabProcess = -1 # -1 if process is shutdown.
        self.workspacePath = os.getcwd()
    
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


            # Look for the start of a code to execute.
            codeStart = self.searchReg(line, r'```(.*?)exec(.*?)\n')

            if not codeStart:
                # Save lines readed in dataOut.
                dataOut += line
                continue

            code = ''

            # Read the code to execute.
            if codeStart:
                while True:
                    line = buff.readline()
                    if not line:
                        break
                    #dataOut += line

                    # Look for the end of code to execute.
                    codeEnd = self.searchReg(line, r'```\n')

                    if codeEnd:
                        # Execute the code.
                        language = codeStart.group(1)
                        # Local options extracted from the file.
                        opts = codeStart.group(2).split()

                        # Combine both local and global options. 
                        codeOut = self.executeCode(code,language,opts+self.opts)
                        dataOut += codeOut

                        break
                    else:
                        code += line

        if not self.matlabProcess == -1:
            self.stopMatlabProcess()

        return dataOut

    def executeCode(self,code,language,opts):
        """ EXECUTECODE
        @brief: Execute the code.
        
        @param: code Code to execute.
              : language Code language (Matlab, python, etc)
              : opts Options for executing the code.
                
        @return: codeOut Output of the code.
        """

        languages = {
                'matlab':self.executeMatlabCode,
                'MATLAB':self.executeMatlabCode,
                'Matlab':self.executeMatlabCode,
                'sh':self.executeBashCode
                }

        fnc = languages.get(
            language[:-1], 
            lambda code, opts:'ERROR: Code language is not supported.'
            )
        
        codeOut = ''

        if not '--no-code' in opts:
            codeOut += '```' + language[:-1] + '\n'
            codeOut += code
            codeOut += '```\n\n'

        # Change workspace path to the one needed for the command.
        if '--path' in opts:
            os.chdir(opts[opts.index('--path')+1])

        # Check if we want to execute the code.
        no_exec = opts[opts.index("no_exec")+1]
        if not no_exec:
            codeResult = fnc(code,opts)
            if not '--no-echo' in opts:
                if not '--raw' in opts:
                    codeOut += '```\n'
                codeOut += codeResult
                if not '--raw' in opts:
                    codeOut += '\n```\n'
    
        # Change workspace path to the original.
        os.chdir(self.workspacePath)

        return codeOut

    def startMatlabProcess(self):
        """ STARTMATLABPROCESS
        @brief: Start MATLAB as a subprocess for executing code.
        
        @return: void
        """

        self.matlabProcess = subprocess.Popen(
                args=['matlab', '-nosplash', '-nodesktop', '-nodisplay'],
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                encoding = 'utf8'
                )

        self.verbosePrint('Waiting for MATLAB to start')
        
        self.matlabProcess.stdin.write('disp(\"#########\")\n')
        self.matlabProcess.stdin.flush()

        while True:
            line = self.matlabProcess.stdout.readline()
            # print(line,end='')
            searchObj = re.search(r'>> #########',line,re.M|re.I)
            if searchObj: 
                break

        self.verbosePrint('MATLAB started')
                
    def stopMatlabProcess(self):
        """ STOPMATLABPROCESS
        @brief: Stop the MATLAB process.
        
        @return: void
        """

        self.verbosePrint('Closing Matlab')

        stdout_value = self.matlabProcess.communicate()[0]
        # print(stdout_value)

        self.verbosePrint('Matlab closed')
        self.matlabProcess = -1       
        
    def executeMatlabCode(self,code,opts):
        """ EXECUTEMATLABCODE
        @brief: Execute matlab code.
        
        @param: code Code to execute.
              : opts Options for executing the code.
                
        @return: codeOut Output of the code.
        """

        if self.matlabProcess == -1:
            self.startMatlabProcess()

        buff = io.StringIO(code)
        code = ''

        # Matlab is executed as a process that is reused in each execution.
        # So the code in executeCode only works one time to change the path.
        # Therefore it is necesary to change the path if needed.
        if '--path' in opts:
            os.chdir(self.workspacePath)
            pathRelative = opts[opts.index('--path')+1]
            pathAbsolute = os.path.abspath(pathRelative)

            code = code + "cd %s," % pathAbsolute

        while True:
            line = buff.readline()
            if not line:
                break
            # Search for Matlab comments in the code to execute.
            searchOb = self.searchReg(line, r'%(.*?)\n')
            if not searchOb:
                code += line
                continue
            # Remove the comments.
            line = self.replaceReg(line,r'%(.*?)\n','')
            code += line

        code = code.split('\n')
        code = ','.join(code)

        # We dont need to change the path anymore.
        #if '--path' in opts:
            #code = 'cd ' + opts[opts.index('--path')+1]  +';'+ code

        self.verbosePrint('Code to execute in MATLAB:')
        self.verbosePrint(code)  
        self.verbosePrint('Send command to MATLAB')

        self.matlabProcess.stdin.write(code+'\n')
        self.matlabProcess.stdin.flush()

        self.matlabProcess.stdin.write('disp(\"#########\")\n')
        self.matlabProcess.stdin.flush()

        self.verbosePrint('Command output')

        
        codeOut = ''
        while True:
            line = self.matlabProcess.stdout.readline()
            self.verbosePrint(line,end='')
            searchObj = re.search(r'>> #########',line,re.M|re.I)
            if searchObj: 
                break
            # Do not include the promt in the output of the command.
            if not re.search(r'>>',line,re.M|re.I):
                codeOut += line

        codeOut = codeOut[:-2]

        self.verbosePrint('End of command output')

        return codeOut
         
    def executeBashCode(self,code,opts):
        """ EXECUTEBASHCODE
        @brief: Execute bash code.
        
        @param: code Code to execute.
              : opts Options for executing the code.
                
        @return: codeOut Output of the code.
        """

        code = code.split('\n')
        # Remove empty strings in the code
        aux = []
        for line in code:
            if (line != ""):
                aux.append(line)

        code = aux

        code = '&&'.join(code)

        self.verbosePrint('Code to execute in the shell:')
        self.verbosePrint(code)  

        ans = os.popen(code).read()

        codeOut = ans

        return codeOut
