from Filter import Filter

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

        i = 0
        while i < len(opts):
            opts[i] = opts[i].strip()
            i += 1

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

        # Remove all the intros in the start of the file.
        while True:
            if text[1] == '\n':
                text = text[:1:]
            else:
                break

        # Remove all the intros in the end of the file.
        while True:
            if text[-1] == '\n':
                text = text[:-1:]
            else:
                break

        return text
 
