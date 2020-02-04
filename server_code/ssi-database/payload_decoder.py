import bitarray
import base64
import sys
import codecs
import uu

def gain_select(gain):
    if gain == 0:
        return 1
    elif gain == 1:
        return 2
    elif gain == 2:
        return 4
    elif gain == 3:
        return 8
    elif gain == 4:
        return 16
    elif gain == 5:
        return 32
    elif gain == 6:
        return 64
    elif gain == 7:
        return 128
    else:
        sys.exit("You have entered a gain that does not exists")
        return 0

def split_innerpayload(payload):
    #payload_bytes =  payload.encode('utf-8')
    #test cases
    #this test case 1 test 2 samples of periodic data
    #Test case 1 '0000100000000010010111100001011011111010110111011010000010100000010111100001011011111010110111011010000010100000'
    #IMPLEMENT A FAIL SAFE WHERE IF THE DIVISOR IS NOT THE EQUAL NUMBER THEN WE ARE GOING TO HAVE ISSUES
    #IMPLEMENT IF THE SIZE OF THE BITARRAY LEFT IS LESSER THAN WAHT WAS MENTIONED IN THE LENGTH
    #this is for mode 2 where there is no timestamp but there is 4 burst samples
    #Test case 3 '10011000010111100001011011111010110111010000000001100100000000000000000000000000000001001010010110100101101001011010010110100101101001011010010110100101'
    #this is multipacket combination of test 1 and test 3
    #gotta check for multi packet
    payload_bits = bitarray.bitarray('000010000000001001011110000101101111101011011101101000001010000001011110000101101111101011011101101000001010000010011000010111100001011011111010110111010000000001100100000000000000000000000000000001001010010110100101101001011010010110100101101001011010010110100101')
    #payload_bits.frombytes(payload_bytes)
    #print(payload_bytes)
    payload_info = payload_bits.buffer_info()
    payload_length = (payload_info[1]*8) - payload_info[3]
    final_frame = []
    #conclusion is that we dont need stop bits + start frames and we need the data_frame for should have 
    # a packet length cuz your inner payload could fail 32 bits for burst length. No need for packetlengths for data frames.
    # discard all infos on the network frame
    # i can just request the missing drop packets to Brian and the database shud be able to sort them up. 
    # if you have multipacket
    #for multipacket
    #message type(2bits) sensorID(3bits) gain (3bits) length (1byte) timestamp (4bytes) data(2bytes)
    index = 0
    print("Payload length is: ", payload_length)
    while(index < payload_length):
        #print("Payload bits are: ",payload_bits)
        mode = int(payload_bits[index :index+2].to01(),2)                       #0:2
        index = index + 2
        print("The index here supposed be 2 | ", index)
        channel =int(payload_bits[index:index+3].to01(),2)                     #2:5
        index = index + 3  
        print("The index here supposed be 5 | ", index)                                    
        print("The buffer info is: ", payload_bits.buffer_info())
        gain = int(payload_bits[index:index+3].to01(),2)                        #5:8
        gain = gain_select(gain)
        index = index + 3
        print("The index here supposed be 8 | ", index)
        #raw_data = int(payload_bits[24:24+length].to01(),2)/
        timestamp_list = []
        data_list = []

        if mode == 0:
            #periodic
            length =  int(payload_bits[index:index+8].to01(),2)               #8:16 length is in 6 bytes for timestamp and data
            index = index + 8  
            for x in range(length):
                #4 bytes for timestamp and 2 bytes for the actual data
                print("The chosen data mode is 0")
                offset = 6*8*(x+1)+index                            #32
                base_offset = 6*8*x+index                           #32
                raw = payload_bits[base_offset:offset]
                print(raw)
                timestamp = int(raw[0:4*8].to01(),2)
                print("The timestamp here is: ", timestamp)    
                data = int(raw[4*8:].to01(),2)
                print("The data is: ",data)
                timestamp_list.append(timestamp)
                data_list.append(data)
                print("The offset is: ",offset,"The base offset is: " , base_offset)
            index = offset
            
        #   dataset = list(zip(timestamp_list,data_list)

        elif mode == 1:
            #monitor periodic
            length =  int(payload_bits[index:index+8].to01(),2)               #8:16 length is in 6 bytes for timestamp and data
            index = index + 8  
            for x in range(length):
                #4 bytes for timestamp and 2 bytes for the actual data
                print("The chosen data mode is 1")
                offset = 6*8*(x+1)+index                            #32
                base_offset = 6*8*x+index                           #32
                raw = payload_bits[base_offset:offset]
                print(raw)
                timestamp = int(raw[0:4*8].to01(),2)
                print("The timestamp here is: ", timestamp)    
                data = int(raw[4*8:].to01(),2)
                print("The data is: ",data)
                timestamp_list.append(timestamp)
                data_list.append(data)
                print("The offset is: ",offset,"The base offset is: " , base_offset)
            index = offset
            
        #  dataset = list(zip(timestamp_list,data_list)
        elif mode == 2:
            print("The chosen data mode is 2")
            #burst
            timestamp = int(payload_bits[index:index + 32].to01(),2)        #8:40
            timestamp_list.append(timestamp)
            print("The timestamp here is: ",timestamp)
            index = index + 32
            print("The index here supposed be 40 | ", index) 
            burst_frequency = int(payload_bits[index:index + 16].to01(),2)  #40:56
            print("The burst frequency is: ",burst_frequency)#payload_bits[index:index + 16])
            index = index + 16
            print("The index here supposed be 56 | ", index) 
            num_data = int(payload_bits[index:index + 32].to01(),2)        #num data in python is 
            index = index + 32
            print("The number of burst shots are : ", num_data)
            print("The index here supposed be 88 | ", index) 
            for x in range(num_data):
                #4 bytes for timestamp and 2 bytes for the actual data
                offset = 2*8*(x+1)+index                                    #64
                base_offset = 2*8*x+index                                   #64
                temp = payload_bits[base_offset:offset]
                print("Raw bits in the mode 2 are : ",temp)
                data = int(payload_bits[base_offset:offset].to01(),2)
                print("The offset is: ",offset,"The base offset is: " , base_offset)
                data_list.append(data)
                print("The data is: ",data)
            index = offset
        # dataset = data_list
        else :
            print("alright man THINGS JUST DONT WORK")
            #debugging information dump into log files
        if mode == 2:
            length = num_data
        payload_frame = {
        'mode': mode,
        'gain': gain,
        'channel': channel,
        'length': length,
        'timestamp': timestamp_list,
        'data': data_list
        }
        print("/////////////////////////HERE IS YOUR PAYLOAD FRAME: ",payload_frame)
        
        final_frame.append(payload_frame)
    """
    range_final = len(final_frame)
    print(range_final)
    for i in range(range_final):
        print("The final frames are: ", final_frame[i])
    """
    return final_frame

#this should return byte mappings
def uudecode(body):
    head = 'begin 666 <data>\n'
    end = '\n \nend\n'
    body = head + body + end
    un_enc_data = codecs.decode(body.encode('utf-8'),'uu')
    return un_enc_data

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

#Type(1) sequence(7) deviceID(32) || flag(1) padding(3) setID(4)||  rawData(x) crc(8) 
def add_data(message_byte):
    #do the utf-8 decoding and then do the crc check i think
    crc_value = crc_check(message_byte)
    if (crc_value == True):
        decoded_data = uudecode(message_byte)
        data_bits = bitarray.bitarray()
        data_bits = data_bits.frombytes(decoded_data)
        data_info = data_bits.buffer_info()
        data_length = (data_info[1]*8) - data_info[3]
        external_frame ={
            'type' : data_bits[0],
            'sequence': data_bits[1:8],
            'deviceID': data_bits[8:32],
            'rawData': data_bits[32:(data_info[1]-1)*8] #(number of total bytes occupied -1)*8
            #u dont need to store the crc values
        }
        final_frame = split_innerpayload(external_frame['rawData'])
        #more processing needs to take place
    return 1



if __name__ == "__main__":
    # shared resources
    temp = 'Exa'
    print(temp)
    frame = split_innerpayload(temp)
    for i in range(len(frame)):
        print("The final FRAMES are: ", frame[i])