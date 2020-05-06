class Pipeline:
    """ PIPELINE

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
            f.debugInfo()
            data = f.run(data)
            print("Done")

        return data
