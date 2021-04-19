import os

dir = r'.\片源'
name_list = [file.split('.')[0] for file in os.listdir(dir)]

file = open('text.txt',mode='r',encoding='utf-8')
text = file.read()
file.close()
name_in_str = []
name_not_in_str = []

for name in name_list:
    if name in text:
        name_in_str.append(name)
    else:
        name_not_in_str.append(name)

print(name_in_str)
print(name_not_in_str)