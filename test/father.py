def add(a,b):
    return a+b
sum=add(1,2)

def create_user(**kwargs):
    """"
    计算两数之和
    :param kwargs:任意多字符
    :return:NONE
    """
    name = kwargs.get("name")
    age = kwargs.get("age")
    print(kwargs)
    print(name, age)

def llm():
    pass
def search_course():
    pass

create_user(name="Tom", age=20)


