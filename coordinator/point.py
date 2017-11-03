class Point():
    def __init__(self, **kwargs):
        """
        Constructor for the Point class
        
        kwargs: list of properties for the object. Can pass in a dictionary using double-splat
        """
        
        self.long_address = kwargs['long_address']
        
        # ID is optional, so use get() instead
        self.point_id = kwargs.get('rowid')
        
    
    def __repr__(self):
        """
        Returns a string representation of the Point object
        """
        
        return 'Point{{id={}, long_address=\'{}\'}}'.format(self.point_id, self.long_address)
