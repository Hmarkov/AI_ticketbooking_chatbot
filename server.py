from asyncio.windows_events import NULL
import socket
import qrcode
import time
import socket
import socket, threading  
import random
import json
import calendar

#JSON file loader
def json_file(filename):
    with open(filename + '.json') as f:
        return json.load(f)

#Class that sends a message after being processed in the NLPU and KB&RE
class Message(object):
    queue=str()    

    #IF the user required a delay information this function will send all the information required
    #... i could've used the JSON file i know 
    def send_delay(delay,s,addr):
        delay="Your total delay is"+delay+" minutes"
        s.sendto(delay.encode('utf-8'), addr)

    #Return a ticket based on the information acquired  
    def send_ticket(ticket_info,s,addr):
        if ticket_info["isReturn"]==False:
            ticketinfo=str("Departure date:"+ticket_info['depDate']+"||| "
            +"Departure station:"+ticket_info['departureStationName']+" ||| "
            +"Arrival station:"+ticket_info['arrivalStationName']+" ||| "
            +"Departure time:"+ticket_info['departureTime']+"\n"
            +"Arrival time:"+ticket_info['arrivalTime']+" ||| "
            +"Duration:"+ticket_info['duration']+" ||| "
            +"Number of changes:"+ticket_info['changes']+" ||| "
            +"Fare provider:"+ticket_info['fareProvider']+"\n"
            +"Ticket price:"+str(ticket_info['ticketPrice'])+"|")
        else:
            ticketinfo=str("Departure date:"+ticket_info['depDate']+"||| "
            +"Departure station:"+ticket_info['departureStationName']+" ||| "
            +"Arrival station:"+ticket_info['arrivalStationName']+" ||| "
            +"Departure time:"+ticket_info['departureTime']+"\n"
            +"Arrival time:"+ticket_info['arrivalTime']+" ||| "
            +"Duration:"+ticket_info['duration']+" ||| "
            +"Number of changes:"+ticket_info['changes']+" ||| "
            +"Fare provider:"+ticket_info['fareProvider']+"\n"
            +"Return date:"+ticket_info['returnDate']+"|||"
            +"Return time:"+ticket_info['returnTime']+"|||"
            +"Ticket price:"+str(ticket_info['ticketPrice'])+"|")
        s.sendto(ticketinfo.encode('utf-8'), addr)

    #Process the URL given the ticket information and return a QR code for the user
    def send_qr(ticket_info,s,addr):
        qr = qrcode.QRCode(version=1,box_size=10,border=5)
        qr.add_data(ticket_info)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save('qrcode1.png')
        s.sendto("qrcode1.png".encode('utf-8'), addr)
        
    #Structuring and concatenating string  
    def queue_message(messege):
        Message.queue+=messege

    #Send message to the client
    def send_message(message,s,addr):
        message = { 'message': Message.queue + message}
        Message.queue = str()
        s.sendto(message['message'].encode('utf-8'), addr)

    #Retreive appropriate answer based on the user message
    def queue_feedback(feedback_name):
        feedbacks = json_file('feedback')[feedback_name]
        Message.queue += random.choice(feedbacks) + ' '
        Message.send_message(Message.queue)

    #Retreive suitable answer and concatenate if needed
    def send_feedback(feedback_name,s,addr,string=str()):
        # turn=1
        feedbacks = json_file('feedback')[feedback_name]
        feedback = Message.queue + random.choice(feedbacks)
        feedback = feedback.replace('%s', string)
        Message.queue = str()
        print("Sending: " + feedback)
        Message.send_message(feedback,s,addr)
        #Message.send_message(feedback,s,addr)


from nlpu import get_entities
from kbandre import process_entities


#Server function to wait for user messages and process them
def Main_func():
    host = '127.0.0.1' #Server ip
    port = 4000

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    print("Server Started")
    while True:
        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')
        print("Message from: " + str(addr))
        print("From connected user: " + data)
        process_entities(get_entities(data,s,addr))

if __name__=='__main__':
    thread = threading.Thread(target=Main_func)
    thread.start()