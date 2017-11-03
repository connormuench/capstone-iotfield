from db_man import DatabaseManager
from point import Point
from rule import Rule

man = DatabaseManager('coordinator.db')

points = []
points.append(Point(long_address='1234567890'))
points.append(Point(long_address='0987654321'))
print points
man.add_point(points[0])
man.add_point(points[1])

rules = []
rules.append(Rule(expression='{1234567890} == 1', target_device=points[1], action='on'))
print rules
man.add_rule(rules[0])

print man.get_rules_for_controllable_device(points[1])
print man.get_rules_for_sensor(points[0])
