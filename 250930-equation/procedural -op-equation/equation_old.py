
def tokenize(string: str) -> list:
    arr = []  
    for a, ch in enumerate(string): # склейка цифр в числа 
        if (ch).isdigit():
            arr.append(int(ch))              
            if a!=0 and isinstance(arr[-2], int):
                arr[-2] = arr[-1]+arr[-2]*10
                arr.pop(-1)
        else:
            arr.append(string[a])
      
    for i, ch in enumerate(arr): # нахождение отрицательных чисел
        if ch == '-' and isinstance(arr[i+1], int):
            arr[i+1] = arr[i+1] * (-1)
            arr.pop(i)
    for i,ch in enumerate(arr):
        if isinstance((arr[i]), int):
            arr[i]=str(arr[i])
    return arr

def reduction(string: str) -> list:
    for i in range(0,len(string)): 
        
        if (string[i-2]).isdigit() and string[i-1] == '*' and (string[i]).isdigit() and i!=0 and i!=1:
            string[i-2] = string[i-2] * string[i]
            string.pop(i)
            string.pop(i-1)
        if (string[i-2]).isdigit() and string[i-1] == '/' and (string[i]).isdigit() and i!=0 and i!=1:
            string[i-2] = string[i-2] / string[i]
            string.pop(i)
            string.pop(i-1)
        if (string[i-2]).isdigit() and string[i-1] == '+' and (string[i]).isdigit() and i!=0 and i!=1:
            string[i-2] = string[i-2] + string[i]
            string.pop(i)
            string.pop(i-1)
        elif (string[i-1]).isdigit() and (string[i]).isdigit() and i!=0:
            string.insert(i,'+')
        elif string[i-1] == 'x' and (string[i]).isdigit() and i!=0:
            string.insert(i,'+')
            print('yes')
        elif string[i] == 'x' and (string[i-1]).isdigit() and i!=0:
            string.insert(i,'+')
    return string
#def solution(sttring: str):
    #None

ur = str(input('введите выражение:'))
arr = tokenize(ur)
arr1 = reduction(arr)


print(arr1)

