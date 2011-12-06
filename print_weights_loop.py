from database import db
import time

while True:
  collection = db.getCollection("pacman_weights")
  found = collection.find_one()
  weights = found["the_weights"]
  print "\n"
  for f_name in weights.keys():
    print "Feature:\t"+str(f_name)
    print "Weight:\t\t"+str(weights[f_name])
  time.sleep(2)
  db.kthxbye(collection)

