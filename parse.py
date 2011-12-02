f = open("out.txt", "r")
red = 0
blue = 0
for line in f.readlines():
	if "has captured" in line:
		x = line.strip().split("has captured")[0]+"won"
		#print x
		if "Blue" in x:
			blue += 1
		else:
			red += 1

print "Blue:", blue
print "Red:", red
