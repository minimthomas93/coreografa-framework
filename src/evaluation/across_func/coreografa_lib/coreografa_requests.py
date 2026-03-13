
import json

class CoreoRequest:
    def __init__(self, name,function, constraints = [], initial_pop = [], initial_pop_files = [], request_type=None) -> None:
        self.name = name
        self.request_type = request_type
        self.metric_constraints = []
        self.prop_constraints = []
        self.function = function
        for constraint in constraints:
            if constraint.type == "metric":
                self.metric_constraints.append(constraint)
            elif constraint.type == "prop":
                self.prop_constraints.append(constraint)
        self.initial_pop = initial_pop
        self.initial_pop_files = initial_pop_files

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def write_json(self, file_name):
        with open(file_name, 'w') as file:
            file.write(self.toJSON())

class CoreoBasicConstraint:
    def __init__(self, type, name, op, value):
        self.type = type
        self.name = name
        self.op = op
        self.value = value
        #self.count = count

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)