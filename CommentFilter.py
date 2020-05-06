from Filter import Filter

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
