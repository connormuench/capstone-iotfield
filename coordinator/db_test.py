from db_man import DatabaseManager
from point import Point
from rule import Rule

man = DatabaseManager('coordinator.db')

points = []
points.append(Point(point_id='1234567890:0', name='', point_type='sensor', mode='n/a'))
points.append(Point(point_id='0987654321:0', name='', point_type='controllable_device'))
print points
man.add_point(points[0])
man.add_point(points[1])

rules = []
rules.append(Rule(expression='{Temperature sensor|1234567890:0} < 1', target_device=points[1], action='on', is_active=True, server_id=54))
print rules
man.add_rule(rules[0])

print man.get_rules_for_controllable_device(points[1])
print man.get_rules_for_sensor(points[0])
