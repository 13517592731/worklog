import random
def captcha():
    temp = ""
    for i in range(4):
        if i == 0 or i == 1:
            number = str(random.randint(1, 5))
            temp += number
        else:
            number = str(random.randint(6, 9))
            temp += number
    print(temp)
    return temp

captcha()