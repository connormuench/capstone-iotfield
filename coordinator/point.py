class Point():
    def __init__(self, **kwargs):
        """
        Constructor for the Point class
        
        kwargs: list of properties for the object. Can pass in a dictionary using double-splat
        """
        
        self.point_id = str(kwargs['point_id'])
        self.name = str(kwargs['name'])
        self.point_type = str(kwargs['point_type'])
        self.mode = str(kwargs.get('mode', 'manual'))
        
        # ID is optional, so use get() instead
        self.rowid = kwargs.get('rowid')
        
    
    def __repr__(self):
        """
        Returns a string representation of the Point object
        """
        
        return 'Point{{id={}, point_id=\'{}\', name=\'{}\', point_type=\'{}\', mode=\'{}\'}}'.format(self.rowid, self.point_id, self.name, self.point_type, self.mode)
