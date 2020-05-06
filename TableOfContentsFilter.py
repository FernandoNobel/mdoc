from Filter import Filter
import io

class TableOfContentsFilter(Filter):
    """ TABLEOFCONTENTSFILTER(FILTER)

    This filter creates a table of contents based on markdown titles and
    subtitles.
    """
    
    def run(self,data):
        """ RUN
        @brief: Run the filter
        
        @param: data Input data to process.
                
        @return: data Output data processed.
        """

        searchObj = self.searchReg(data,r'\[TOC\]')

        if searchObj:
            print("TOC found")
            titles = self.findTitles(data)
            toc = self.tocGithub(titles)
            data = self.replaceReg(data,r'\[TOC\]',toc)

        return data

    def findTitles(self,data):
        """ FINDTITLES
        @brief: Finds all the titles in the document and the depth of each one.
        
        @param: data Input data to process.
                
        @return: titles List with the titles and subtitles.
        """

        buff = io.StringIO(data)

        titles = ()

        # Read data line by line.
        while True:
            line = buff.readline()

            if not line:
                break

            h1 = self.searchReg(line, r'(?m)^#{1} (?!#)(.*)')
            h2 = self.searchReg(line, r'(?m)^#{2} (?!#)(.*)')
            h3 = self.searchReg(line, r'(?m)^#{3} (?!#)(.*)')
            h4 = self.searchReg(line, r'(?m)^#{4} (?!#)(.*)')
            h5 = self.searchReg(line, r'(?m)^#{5} (?!#)(.*)')

            if h1:
                titles = titles + ('1',h1.group(1))
            if h2:
                titles = titles + ('2',h2.group(1))
            if h3:
                titles = titles + ('3',h3.group(1))
            if h4:
                titles = titles + ('4',h4.group(1))
            if h5:
                titles = titles + ('5',h5.group(1))
        
        return titles

    def tocGithub(self,titles):
        """ TOCGITHUB
        @brief: Creates a the table of contents with GitHub format.
        
        @param: titles List of titles.
                
        @return: toc String with the table of contents.
        """

        toc = ''

        nTitles = int(len(titles)/2)
        for i in range(nTitles):
            for j in range(int(titles[2*i])-1):
                toc += '\t'
            toc += '* [' + titles[2*i+1] + ']'
            toc += '(#' + titles[2*i+1].replace(' ','-').replace('.','').lower() + ')'
            toc += '\n'

        return toc
 
