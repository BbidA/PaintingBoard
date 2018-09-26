import pickle

import dollar_1

target = open('/Users/jundaliao/Downloads/templates.pkl', 'rb')
templates = pickle.load(target)
circle = pickle.load(open('/Users/jundaliao/Downloads/triangle.pkl', 'rb'))

result = dollar_1.recognize_shape(circle, templates)

print(result)
