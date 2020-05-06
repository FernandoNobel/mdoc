from Filter import Filter

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
