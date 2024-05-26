lista=[5, 134, 2,9, 100]

a=0

for i in range(len(lista)):
    a=lista[i]
    for j in range(len(lista)):
        if(a<lista[j]):
            a=lista[j]

print(a)