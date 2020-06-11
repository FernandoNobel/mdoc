from abc import ABC, abstractmethod
import re

class Filter(ABC):
    """ FILTER

    Abstract filter class.
    """
    def __init__(self,opts):
        """
        @brief: Constructor of Filter class.
        
        @params: opts General options from the execution of mdoc.
        """

        super().__init__()
        self.opts = opts

    def verbosePrint(self,string, end='\n'):
        """ VERBOSEPRINT
        @brief: Prints to the terminal only if the verbose flag is set.
        
        @param: string String to print.
                
        @return: void
        """

        if self.opts[self.opts.index("verbose")+1]:
            print(string,end=end)

    def debugInfo(self):
        """ RUNWRAPPER
        @brief: This mehtod wraps the run method and provides debug info.
        
        @param: data Input text to process.
                
        @return: data Output text processed.
        """

        self.verbosePrint("\t=== " + self.__class__.__name__.upper()+ " ===")
        self.verbosePrint("Start")

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
