# Program to cancel the timer 
import threading 
  
def gfg(n): 
    print("GeeksforGeeks\n") 
    print(n)


def f1():  
    print("1") 
    print("2") 
    timer = threading.Timer(5, gfg,args=('Hello world',)).start()
    print("3") 
    print("4") 
    # timer.cancel() 
    return 5

a=f1()
print(a)