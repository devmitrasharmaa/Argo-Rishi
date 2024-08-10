import os


directory = os.path.join(r'C:\Users\devmi\OneDrive\Documents\brocode\Python\Flask_shit\Facecify\website1\facecify', 'static', 'dataset','2')
if not os.path.exists(directory):
    print('making new one')
    os.makedirs(directory)
else:
    print('nahhh')

class_id=directory.split('\\')[-1]
print(class_id)
