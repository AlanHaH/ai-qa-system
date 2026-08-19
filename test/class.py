class User:
    Boss="alan"
    def __init__(self, name, age):
        self.name = name
        self.age = age
    ''''
    class就蛋糕店的摸具，对象就是蛋糕
    蛋糕需要用图纸做出来，所以 对象=类() 对象可以用里面的方法
    用点方法使用，当然类还可以写很多函数
    '''
    ''''
    __init__ init在英语中是初始化的意思
    self是把传入的值赋到本类中
    所以才能用点方法取对象中的值
    Boss是类属性 通常是全局的
    '''
user = User("Tom",20)
print(user.name )