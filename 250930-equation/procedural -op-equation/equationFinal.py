def tokenize(string: str) -> list[str]:
    arr = []
    for i, ch in enumerate(string): 
        if (ch).isdigit():
            arr.append(ch)             
            if i!=0 and (arr[-2]).isdigit():
                arr[-2] += arr[-1]
                arr.pop(-1)
        else:
            arr.append(string[i])
    return arr

def find_nn(line: str) -> list[str]:
    for i, ch in enumerate(line): 
        if ch == '-' and (line[i+1]).isdigit():
            line[i+1] = '-' + line[i+1]
            if i==0 or i==len(line)-2:
                line.pop(i)
            else:
                line[i] = '+'
    return line   

def solution(line: str) -> float:
    if (line[0]).isdigit() and line.index('=') == 1: #привидение выражений a=x+b к виду x+b=a
        line.append('=')
        line.append(line[0])
        line.pop(1)
        line.pop(0)
    
    if (line[0]).isdigit() and (line[2]).isdigit(): #решение выражений вида a+b
        line.pop(4)
        line.pop(3)
        otv = eval("".join(line))
    else:
        if line.count('+'):
            line[-1] = str(int(line[-1])*(-1)) 
            line.remove('=')
            line.remove('x')
            otv = eval("".join(line))*(-1)
            
        if line.count('-'):
            if line.index('-') == 1 and line.index('x') == 2:
                line[-1] = str(int(line[-1])*(-1)) 
                line.remove('=')
                line.remove('x')
                line.remove('-')
                otv = eval("".join(line))
            else:
                line[-1] = str(int(line[-1])*(-1)) 
                line.remove('=')
                line.remove('x')
                otv = eval("".join(line))*(-1)
                
        if line.count('*'):
            line[-1] = '/' + line[-1]
            line.remove('=')
            line.remove('x')
            line.remove('*')
            otv = eval("".join(line))**(-1)
            
        if line.count('/'):
            if line.index('/') == 1 and line.index('x') == 2:
                line[-1] = '/' + line[-1]
                line.remove('=')
                line.remove('x')
                line.remove('/')
                otv = eval("".join(line))
            else:
                line[-1] = '*' + line[-1]
                line.remove('=')
                line.remove('x')
                line.remove('/')
                otv = eval("".join(line))
    o = float(otv)
    return o

ur = str(input('Введите выражение: '))
x = solution(find_nn(tokenize(ur)))
print('Ответ: x = ', x)