from bitshares.blockchain import Blockchain
from time import time
test = Blockchain()

def recprint(array):
  global tab
  try:
    tab
  except:
    tab=0
  tab+=1
  if (isinstance(array, dict)):
    for key, value in array.items():
      if not (isinstance(value, dict) or isinstance(value, list)):
        print('  '*tab+str(key)+' : '+str(value))
      else:
        print('  '*tab+str(key)+' : ')
        recprint(value)
  elif (isinstance(array, list)):
    i=0
    for value in array:
      i+=1
      if not (isinstance(value, dict) or isinstance(value, list)):
        print('  '*tab+str(i)+' : '+str(value))
      else:
        print('  '*tab+str(i)+' : ')
        recprint(value)
  tab-=1

def showOperationsInBlock(block):
  global count
  try:
    count
  except:
    count = {}
  for transaction in block['transactions']:
    for operation in transaction['operations']:
      try:
        count[operation[0]]
      except:
        count[operation[0]]=1
      else:
        count[operation[0]]=count[operation[0]]+1
      print(count)
  return count

def extGen(gen):
  work=[]
  for value in gen:
    work.append(value)
  return work

def findFillOrdersInBlock(block):
  for transaction in block['transactions']:
    for operation in transaction['operations']:
      if operation[0]==4:
        print(block['block_num'])

#for block in extGen(test.blocks(1000000,1000100)): 
    #print(block)
    #showOperationsInBlock(block)
#print(next(b))
#recprint(b)
#showOperationsInBlock(b)
