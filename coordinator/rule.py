class Rule:
    def __init__(self, **kwargs):
        """
        Constructor for the Rule class
        
        kwargs: list of properties for the object. Can pass in a dictionary using double-splat
        """
        
        self.expression = kwargs['expression']
        self.target_device = kwargs['target_device']
        self.action = kwargs['action']
        
        # ID is optional, so use get() instead
        self.rule_id = kwargs.get('rowid')
        
        
    def __repr__(self):
        """
        Returns a string representation of the Rule object
        """
        
        return 'Rule{{id={}, expression=\'{}\', target_device={}, action=\'{}\'}}'.format(self.rule_id, self.expression, self.target_device, self.action)
