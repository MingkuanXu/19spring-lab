import sys


f1 = open("scatac_white_list.txt","r")
f2 = open("barcode-output.txt","w+")

line = f1.readline()
line = f1.readline()
while True:
    newline = "".join(line.split("	"))
    print(newline)
    f2.write(newline)
    line = f1.readline()
    if not line:
        break
f1.close()
f2.close()
