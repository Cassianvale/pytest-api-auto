# dict1 = {"a": 1, "b": 2, "c": 3}
# dict2 = {}

# for key, value in dict1.items():
#     dict2[key] = value

# print(dict2)
# 定义两个字典 
dict1 = {"a": 1, "b": 2}   # b的value被覆盖
dict2 = {"b": 3, "c": 4} 

# 使用 update() 方法将 dict2 的键值对更新到 dict1 中 
dict1.update(dict2) 
print(dict1) 	# 输出: {'a': 1, 'b': 3, 'c': 4}