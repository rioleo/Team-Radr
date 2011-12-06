'''Database interactions.'''

import copy
import pymongo
from pymongo import Connection

def getCollection(collectionName, readOnly=False):
    mongo_uri = "mongodb://two_twenty_one:pacmanparty@staff.mongohq.com:10001/play" #WARNING! plaintext password
    # c = Connection(mongo_uri)  #USE THIS FOR REMOTE DATABASE
    c = Connection()  #use this for local database
    collection = c.play[collectionName]
    return collection
    
def kthxbye(collectionInstance):
    '''When you're done with a collection you got through some getXXXX or through the direct getter (ie, road_sensor_data()), you should indicate that with this function so that you free up resources.  (This function will close up the collection's connection to the database for you.)
    
    Arguments:
    collectionInstance -- an instance of a collection you just finished using
    
    Returns:
    nothing
    
    '''
    dbase = collectionInstance.database
    c = dbase.connection
    c.end_request()
