class Rule:
    def __init__(self, **kwargs):
        """
        Constructor for the Rule class
        
        kwargs: list of properties for the object. Can pass in a dictionary using double-splat
        """
        
        self.expression = str(kwargs['expression'])
        self.target_device = kwargs['target_device']
        self.action = str(kwargs['action'])
        self.is_active = kwargs['is_active']
        self.server_id = kwargs['server_id']
        
        # ID is optional, so use get() instead
        self.rowid = kwargs.get('rowid')
        
        
    def __repr__(self):
        """
        Returns a string representation of the Rule object
        """
        
        return 'Rule{{id={}, expression=\'{}\', target_device={}, action=\'{}\', is_active=\'{}\', server_id=\'{}\'}}'.format(self.rowid, self.expression, self.target_device, self.action, self.is_active, self.server_id)
