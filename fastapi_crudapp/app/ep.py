def func1(num,sm):
    if num<=0:
        return sm
    x = num %10
    num = num//10
    sm+=x
    return func1(num,sm)


print(func1(1023,0))
