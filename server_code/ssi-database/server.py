import flask
import bitarray
from flask import request, jsonify
import codecs
import uu
import threading
import time
import json
import os

#--------------------functions----------------------
def uudecode(body):
  head = 'begin 666 <data>\n'
  end = '\n \nend\n'
  body = head + body + end
  un_enc_data = codecs.decode(body.encode('utf-8'),'uu')
  return un_enc_data

def byte_conversion(body):
  b = bytearray()
  b.extend(map(ord, body))
  return b


def dime_backwards(array,final_array):
    length = len(array)-1
    padding = length % 8
    loops = int(length / 8)

    binary = array[length]  #some weird indexing shit, apparently array[length] gives a zero where length is already size-1
    x = len(array)- loops-2   #indexing starts from 0
    
    for y in range(length-1,-1,-1):
        print("Y value at beginning is: ",y)
        if (y+1)%8 != 0 or y == 0 or y+1 == len(array)-1:
            
            temp = binary & (1 << (7 - ((x+1) % 8)))
            print("Temp value here is: ",hex(temp), " ||||",hex(temp << ((x+1) %8)),"x%7 is:",((x+1) % 8), "Binary value here is:", binary)
            temp = array[y] | (temp << ((x+1) %8))
            print("Temp value is: ", hex(temp), "Array[y] value is: ", hex(array[y]))
            final_array[x] = temp
            x = x-1
        elif (y+1) % 8 == 0:
            print("BINARY AF", hex(array[y]))
            binary = array[y]
        else:
            print("This entry is invalid")
        print("#####################################")
        print("Y value is:" ,y, "|| X value is :",x+1)
        print("##################################### \n\n\n\n")
    return final_array

def crc_check(message_byte):
    size = len(encoded_array)
    generator = 0x97
    crc = 0
    for x in range (size):
        currByte = encoded_array[x]
        print("x value is: ",x,"Encoded values are :", hex(currByte))
        crc = currByte ^ crc
        #print(hex(crc))
        for bit in range(8):
            print("bit values are: ", bit)
            if ((crc & 0x80) !=0):
                print(hex(crc))
                crc = crc << 1
                crc = truncate(crc)
                print(hex(crc))
                crc = crc ^generator
                print(hex(crc))
            else:
                crc = crc << 1
                crc = truncate(crc)
    print("CRC value is: ", crc)     
    if (crc == 0):
        return True
    else:
      return False

def uncompress(data):
  return data #TODO change this for real implementation.

def split_message(message_byte):
  # message_binary = '&#193;&#8364;&#225;ABC'
  # message_bit = bitarray.bitarray('11000001100000000000000000000000000000010000000011100001010000010100001001000011')  
  message_bit = bitarray.bitarray()
  print(message_byte)
  message_bit.frombytes(message_byte) #need if uu is correct
  if(message_bit[0]): #human readable
    data_type = 'readable'
    # data_bin = '0'
    # data_readble = message_bit[56:(56+int(message_bit[40:50].to01(),2)*8)].tobytes().decode('utf-8')
  else: #binary
    data_type = 'binary'
    # data_bin = message_bit[56:(56+int(message_bit[40:50].to01(),2)*8)].to01()
    # data_readble = '0'
  
  padding = int(message_bit[40:43].to01(),2)
  frame = {
    'type': data_type,
    'seq_num': int(message_bit[1:8].to01(),2),
    'id': message_bit[8:40].tobytes().hex(),
    # 'padding': padding,
    'end_of_message':message_bit[43],
    'setID': int(message_bit[44:48].to01(),2),
    # 'data_bin': data_bin,
    # 'data_readable': data_readble,
    'payload':message_bit[48:-(padding+8)],
    'crc_correct': crc_check(message_bit)
  }
  return frame

def insert_list(list,position,value):
  if(len(list) > position):
    list[position] = value
    return list
  else:
    new_list = [None] * (position + 1)
    new_list[0:len(list)] = list
    new_list[position] = value
    return new_list

def add_data(message_byte):
  frame = split_message(message_byte)
  #get data
  uncompressed_data = frame['payload'].tobytes().decode('utf-8')
  if(frame['type'] == 'binary'):
    uncompressed_data = uncompress(frame['payload']).tobytes().decode('utf-8')

  #check if sensor id, setid in dictionary. If not add value otherwise return value
  CRC_check = frame['crc_correct']

  message_complete = False

  if(frame['end_of_message']):
    num_message_packets = frame['seq_num'] + 1
  else:
    num_message_packets = None

  list_of_payload = data.setdefault((frame['id'],frame['setID']),([None],CRC_check,num_message_packets,message_complete))

  if(list_of_payload[1] == False):
    CRC_check = list_of_payload[1]

  if(list_of_payload[2] != None):
    num_message_packets = list_of_payload[2]

  updated_list = insert_list(list_of_payload[0],frame['seq_num'],uncompressed_data)

  if(not None in updated_list and len(updated_list) == num_message_packets):
    message_complete = True

  list_of_payload = (updated_list,CRC_check,num_message_packets,message_complete)

  # if(frame['crc_correct'] == False):
  #   list_of_payload = ['ERROR transmission']

  data[(frame['id'],frame['setID'])] = list_of_payload



#---------------------Thread----------------------

#Flask thread
def Flask(cond):
  app = flask.Flask(__name__)
  # app.config["DEBUG"] = True
  # app.config["use_reloader"]=False
  print("Starting FLASK....")

  # with cond:
  @app.before_first_request
  def activate_job():
    def run_job():
      while True:
          print("Run recurring task")
          time.sleep(3)

    thread = threading.Thread(target=run_job)
    thread.start()
  
  @app.route('/', methods=['GET'])
  def home():
    return '''<h1>Smart Sensor Interface</h1> <p> Website to get data.</p>'''
  
  #/sms
  @app.route('/sms', methods=['GET'])
  def displayMessage():
    return jsonify([message,data])
  
  @app.route('/sms', methods=['POST'])
  def createMessage():
    message_entry = {
      'ApiVersion': request.values.get('ApiVersion',None),
      'SmsSid': request.values.get('SmsSid',None),
      'SmsStatus': request.values.get('SmsStatus',None),
      'SmsMessageSid': request.values.get('SmsMessageSid',None),
      'NumSegments': request.values.get('NumSegments',None),
      'From': request.values.get('From',None),
      'ToState': request.values.get('ToState',None),
      'MessageSid': request.values.get('MessageSid',None),
      'AccountSid': request.values.get('AccountSid',None),
      'ToZip': request.values.get('ToZip',None),
      'FromCountry': request.values.get('FromCountry',None),
      'ToCity': request.values.get('ToCity',None),
      'FromCity': request.values.get('FromCity',None),
      'To': request.values.get('To',None),
      'FromZip': request.values.get('FromZip',None),
      'Body': request.values.get('Body',None),
      'ToCountry': request.values.get('ToCountry',None),
      'FromState': request.values.get('FromState',None),
      'NumMedia': request.values.get('NumMedia',None)
    }
    print("you have been summoned")
    encoded_message_byte = byte_conversion(message_entry['Body'])
    
    length = len(encoded_message_byte)-1
    loops = int(length / 8)
    decoded_message_byte = [0] * (len(encoded_message_byte) - loops-1)
    dime_backwards(encoded_message_byte,decoded_message_byte)
    message.append(message_entry)
  
    add_data(decoded_message_byte)
  
    return jsonify({'message': message, 'data': data}), 201
  #run Flask server
  app.run(host='141.212.114.146',port=22222,debug=True, use_reloader=False)

#database thread
def write_db(cond):
  print("Starting write_db....")
  while(True):
    print("Getting Data")
    #collect data and stictch message
    delete = [] 
    for x in data.items():
      if(x[1][3] == True and x[1][1] == True): #condition that message complete
        to_process.append((x[0][0], ''.join(x[1][0])))
        delete.append(x[0])

    for i in delete:
      del data[i]
    print(to_process)
    #parsing message and make it string
    for i in to_process:
      message_to_db = json.loads(i[1])
      message_to_db['sensor_id'] = i[0]
      to_process.remove(i)
      print("parsed message")
      print(message_to_db)
      # send to Database
      print("send to Database")
    print("Done getting Data")
    time.sleep(2)

if __name__ == "__main__":

  # shared resources
  message = []
  data = {} # {(id,setid):[data]}
  to_process = []

  condition = threading.Condition()
  Flask_thread = threading.Thread(name='Flask-server', target=Flask, args=(condition,))
  db_thread = threading.Thread(name='db_thread', target=write_db, args=(condition,))

  # db_thread.start()
  time.sleep(2)
  Flask_thread.start()
  
  
