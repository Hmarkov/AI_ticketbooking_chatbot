from asyncio.windows_events import NULL
from experta import *
from experta.watchers import RULES, AGENDA
import dateutil.parser
from datetime import datetime
from predictFromLocalFile import predict_total
from scraper import Ticket

#source
#https://experta.readthedocs.io/en/latest/reference.html

#Class to process and prioritise functions until a specific goal is met.
class Booking(KnowledgeEngine):
    @DefFacts()

    #Initialise base
    def _initial_action(self):
        if 'reset' in self.dictionary[0]:
            if self.dictionary.get('reset') == 'true':
                self.knowledge = {}
                self.dictionary['service'] = 'chat'
            
        # Get Service
        service = self.dictionary[0].get('service')
        if 'service' in self.knowledge:
            if service != 'chat':
                name = self.knowledge.get('name')
                self.knowledge = {}
                self.knowledge['name'] = name
                self.knowledge['service'] = service
        else:
            self.knowledge['service'] = service
        yield Fact(service = self.knowledge.get('service'))

        # Knowladge system to keep information in specific stages
        if not 'question' in self.knowledge:
            self.knowledge['question'] = str()
        if 'name' in self.knowledge:
            yield Fact(name = self.knowledge.get('name'))
        if 'isReturn' in self.knowledge:
            yield Fact(isReturn = self.knowledge.get('isReturn'))
        if 'fromLocation' in self.knowledge:
            yield Fact(fromLocation = self.knowledge.get('fromLocation'))
        if 'toLocation' in self.knowledge:
            yield Fact(toLocation = self.knowledge.get('toLocation'))
        if 'departDate' in self.knowledge:
            yield Fact(departDate = self.knowledge.get('departDate'))
        if 'departTime' in self.knowledge:
            yield Fact(departTime = self.knowledge.get('departTime'))
        if 'returnDate' in self.knowledge:
            yield Fact(returnDate = self.knowledge.get('returnDate'))
        if 'returnTime' in self.knowledge:
            yield Fact(returnTime = self.knowledge.get('returnTime'))
        if 'givenTicket' in self.knowledge:
            yield Fact(givenTicket = self.knowledge.get('givenTicket'))
        if 'whatsNext' in self.knowledge:
            yield Fact(whatsNext = self.knowledge.get('whatsNext'))
        if 'predictFromLocation' in self.knowledge:
            yield Fact(predictFromLocation = self.knowledge.get('predictFromLocation'))
        if 'predictToLocation' in self.knowledge:
            yield Fact(predictToLocation = self.knowledge.get('predictToLocation'))
        if 'predictDelayTime' in self.knowledge:
            yield Fact(predictDelayTime = self.knowledge.get('predictDelayTime'))
        if 'predictDelayTime' in self.knowledge:
            yield Fact(predictDelay = self.knowledge.get('predictDelay'))
        if 'informationGiven' in self.knowledge:
            yield Fact(informationGiven = self.knowledge.get('informationGiven'))

    #Greeting Rule that provides a set of frases to the user
    @Rule(salience = 100)
    def greeting(self):
        if 'greeting' in self.dictionary[0]:
            Message.send_feedback('greeting',self.dictionary[1],self.dictionary[2])

    #Ask Name Rule that provides a question to the user and expects an answer with no specific format
    @Rule(Fact(service = 'chat'),
        NOT(Fact(name = W())),
        salience = 99)
    def ask_name(self):
        if 'name' in self.dictionary[0]:
            name = self.dictionary[0].get('name')
            self.declare(Fact(name = name))
            self.knowledge['name'] = name
        else:
            if self.knowledge['question'] == 'ask_name':
                Message.send_feedback('unknown_message',self.dictionary[1],self.dictionary[2])
            else:
                self.knowledge['question'] = 'ask_name'
            Message.send_feedback('ask_name',self.dictionary[1],self.dictionary[2])

    # Ask Service Rule that provides a question to the user and asks if the user wants a booking or to predict a delay
    @Rule(Fact(service = 'chat'),
        Fact(name = MATCH.name),
        salience = 98)
    def ask_if_booking(self, name):
        if self.knowledge['question'] == 'ask_if_booking':
            Message.send_feedback('unknown_message',self.dictionary[1],self.dictionary[2],name)
        else:
            self.knowledge['question'] = 'ask_if_booking'
        Message.send_feedback('ask_make_booking',self.dictionary[1],self.dictionary[2],name)

    # Ask Location Rule that provides a question to the user and asks if the user for departure station and final destination
    @Rule(Fact(service = 'book'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(fromLocation = W())),
        NOT(Fact(toLocation = W())),
        salience = 97)
    def ask_location(self):
        error = False
        if 'location' in self.dictionary[0] and len(self.dictionary[0].get('location')) > 1:
            location = self.dictionary[0].get('location')
            self.declare(Fact(fromLocation = location[0]))
            self.knowledge['fromLocation'] = location[0]
            self.declare(Fact(toLocation = location[1]))
            self.knowledge['toLocation'] = location[1]
        else:
            if self.knowledge['question'] == 'ask_location':
                Message.send_feedback('unknown_message',self.dictionary[1],self.dictionary[2])
            else:
                self.knowledge['question'] = 'ask_location'
            Message.send_feedback('ask_location',self.dictionary[1],self.dictionary[2])
            self.declare(Fact(isQuestion = True))

    # Ask Depart Date Rule that asks the user for departure date
    @Rule(Fact(service = 'book'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(departDate = W())),
        salience = 96)
    def ask_depart_date(self):
        departDate = 'false'
        error = False
        if 'dates' in self.dictionary[0]:
            departDate = self.dictionary[0].get('dates')[0]
            if dateutil.parser.parse(departDate) < datetime.now():
                Message.send_feedback('past_date',self.dictionary[1],self.dictionary[2])
                error = True
            else:
                self.declare(Fact(departDate = departDate))
                self.knowledge['departDate'] = departDate

        if self.knowledge['question'] == 'ask_depart_date' and departDate == 'false' and not error:
            Message.send_feedback('wrong_date',self.dictionary[1],self.dictionary[2])
        else:
            self.knowledge['question'] = 'ask_depart_date'

        if departDate == 'false' or error:
            Message.send_feedback('ask_depart_date',self.dictionary[1],self.dictionary[2])
            self.declare(Fact(isQuestion = True))

    # Ask Depart Time Rule that asks the user for departure time
    @Rule(Fact(service = 'book'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(departTime = W())),
        salience = 95)
    def ask_depart_time(self):
        if 'times' in self.dictionary[0]:
            departTime = self.dictionary[0].get('times')
            self.declare(Fact(departTime = departTime[0]))
            self.knowledge['departTime'] = departTime[0]
            del self.dictionary[0]['times']
        else:
            if self.knowledge['question'] == 'ask_depart_time':
                Message.send_feedback('unknown_message',self.dictionary[1],self.dictionary[2])
            else:
                self.knowledge['question'] = 'ask_depart_time'
            Message.send_feedback('ask_depart_time',self.dictionary[1],self.dictionary[2])
            self.declare(Fact(isQuestion = True))

    # Ask If Return Rule that asks the user if it wants a return ticket too
    @Rule(Fact(service = 'book'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(isReturn = W())),
        salience = 94)
    def ask_is_return(self):
        if 'return' in self.dictionary[0]:
            self.declare(Fact(isReturn = 'true'))
            self.knowledge['isReturn'] = 'true'
        elif 'answer' in self.dictionary[0]:
            answer = self.dictionary[0].get('answer')
            self.declare(Fact(isReturn = answer))
            self.knowledge['isReturn'] = answer
            del self.dictionary[0]['answer']
        else:
            if self.knowledge['question'] == 'ask_is_return':
                Message.send_feedback('unknown_message',self.dictionary[1],self.dictionary[2])
            else:
                self.knowledge['question'] = 'ask_is_return'
            Message.send_feedback('ask_is_return',self.dictionary[1],self.dictionary[2])
            self.declare(Fact(isQuestion = True))

    # Ask Return Date Rule after the function above if TRUE this rule is executed asking the user for return date
    @Rule(Fact(service = 'book'),
        NOT(Fact(isQuestion = W())),
        Fact(isReturn = 'true'),
        NOT(Fact(returnDate = W())),
        salience = 93)
    def ask_return_date(self):
        returnDate = 'false'
        error = False
        if 'dates' in self.dictionary[0]:
            returnDate = self.dictionary[0].get('dates')
            returnDate = returnDate[1] if len(returnDate) > 1 else returnDate[0]
            if dateutil.parser.parse(returnDate) < dateutil.parser.parse(self.knowledge.get('departDate')):
                Message.send_feedback('past_depart_date',self.dictionary[1],self.dictionary[2])
                error = True
            else:
                self.declare(Fact(returnDate = returnDate))
                self.knowledge['returnDate'] = returnDate

        if self.knowledge['question'] == 'ask_return_date' and returnDate == 'false' and not error:
            Message.send_feedback('wrong_date',self.dictionary[1],self.dictionary[2])
        else:
            self.knowledge['question'] = 'ask_return_date'

        if returnDate == 'false' or error:
            Message.send_feedback('ask_return_date',self.dictionary[1],self.dictionary[2])
            self.declare(Fact(isQuestion = True))

    # Ask Return Time Rule that asks the user for return time
    @Rule(Fact(service = 'book'),
        NOT(Fact(isQuestion = W())),
        Fact(isReturn = 'true'),
        NOT(Fact(returnTime = W())),
        salience = 92)
    def ask_return_time(self):
        if 'times' in self.dictionary[0]:
            returnTime = self.dictionary[0].get('times')
            returnTime = returnTime[1] if len(returnTime) > 1 else returnTime[0]
            self.declare(Fact(returnTime = returnTime))
            self.knowledge['returnTime'] = returnTime
        else:
            if self.knowledge['question'] == 'ask_return_time':
                Message.send_feedback('unknown_message',self.dictionary[1],self.dictionary[2])
            else:
                self.knowledge['question'] = 'ask_return_time'
            Message.send_feedback('ask_return_time',self.dictionary[1],self.dictionary[2])
            self.declare(Fact(isQuestion = True))

    # Show Single Ticket Rule based on previous accumulated data returns a ticket information to the user
    @Rule(Fact(service = 'book'),
        NOT(Fact(givenTicket = W())),
        Fact(isReturn = 'false'),
        Fact(fromLocation = MATCH.fromLocation),
        Fact(toLocation = MATCH.toLocation),
        Fact(departDate = MATCH.departDate),
        Fact(departTime = MATCH.departTime),
        salience = 91)
    def show_single_ticket(self, fromLocation, toLocation, departDate, departTime):
        if not 'givenTicket' in self.knowledge:
            ticket = Ticket.get_ticket_single(fromLocation, toLocation, departDate, departTime)
            if not ticket:
                Message.send_feedback('ticket_error',self.dictionary[1],self.dictionary[2])
                Message.send_feedback('make_another_booking',self.dictionary[1],self.dictionary[2])
                self.declare(Fact(givenTicket = False))
                self.knowledge['givenTicket'] = False
            else:
                Message.send_feedback('ticket_found_single',self.dictionary[1],self.dictionary[2])
                Message.send_ticket(ticket,self.dictionary[1],self.dictionary[2])
                self.knowledge['url'] = ticket.get('url')
                self.declare(Fact(givenTicket = True))
                self.knowledge['givenTicket'] = True

    # Show Return Ticket Rule based on previous accumulated data returns a ticket information to the user
    @Rule(Fact(service = 'book'),
        NOT(Fact(givenTicket = W())),
        Fact(isReturn = 'true'),
        Fact(fromLocation = MATCH.fromLocation),
        Fact(toLocation = MATCH.toLocation),
        Fact(departDate = MATCH.departDate),
        Fact(departTime = MATCH.departTime),
        Fact(returnDate = MATCH.returnDate),
        Fact(returnTime = MATCH.returnTime),
        salience = 90)
    def show_return_ticket(self, fromLocation, toLocation, departDate, departTime, returnDate, returnTime):
        if not 'givenTicket' in self.knowledge:
            ticket = Ticket.get_ticket_return(fromLocation, toLocation, departDate, departTime, returnDate, returnTime)
            if not ticket:
                Message.send_feedback('ticket_error',self.dictionary[1],self.dictionary[2])
                Message.send_feedback('make_another_booking',self.dictionary[1],self.dictionary[2])
                self.declare(Fact(givenTicket = False))
                self.knowledge['givenTicket'] = False
            else:
                Message.send_feedback('ticket_found_return',self.dictionary[1],self.dictionary[2])
                Message.send_ticket(ticket,self.dictionary[1],self.dictionary[2])
                self.knowledge['url'] = ticket.get('url')
                self.declare(Fact(givenTicket = True))
                self.knowledge['givenTicket'] = True

    # Ask Confirm Booking Rule to confirm a ticket after all information shown to the user if true Rule is executed
    @Rule(Fact(service = 'book'),
        Fact(givenTicket = True),
        salience = 89)
    def confirm_booking(self):
        if 'answer' in self.dictionary[0]:
            if self.dictionary[0].get('answer') == 'true':
                 Message.send_qr( self.knowledge.get('url'),self.dictionary[1],self.dictionary[2])
            Message.send_feedback('thank_you',self.dictionary[1],self.dictionary[2])
            self.knowledge['givenTicket'] = False
            self.declare(Fact(whatsNext = True))
            self.knowledge['whatsNext'] = True
            del self.dictionary[0]['answer']
        else:
            if self.knowledge['question'] == 'confirm_booking':
                Message.send_feedback('unknown_message',self.dictionary[1],self.dictionary[2])
            else:
                self.knowledge['question'] = 'confirm_booking'
            Message.send_feedback( 'confirm_booking',self.dictionary[1],self.dictionary[2])

    # Ask Predict Location Rule that requires current and final destination to predict a delay
    @Rule(Fact(service = 'predict'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(predictFromLocation = W())),
        NOT(Fact(predictToLocation = W())),
        salience = 88)
    def ask_predict_location(self):
        if 'location' in self.dictionary[0] and len(self.dictionary[0].get('location')) > 1:
            location = self.dictionary[0].get('location')
            self.declare(Fact(predictFromLocation = location[0]))
            self.knowledge['predictFromLocation'] = location[0]
            self.declare(Fact(predictToLocation = location[1]))
            self.knowledge['predictToLocation'] = location[1]
            del self.dictionary[0]['location']
        else:
            if self.knowledge['question'] == 'ask_predict_location':
                Message.send_feedback('unknown_message',self.dictionary[1],self.dictionary[2])
            else:
                self.knowledge['question'] = 'ask_predict_location'
            Message.send_feedback( 'ask_predict_location',self.dictionary[1],self.dictionary[2])
            self.declare(Fact(isQuestion = True))

    # Ask Current Delay Rule that predicts delay on top of the current delay to a specific station 
    @Rule(Fact(service = 'predict'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(predictDelayTime = W())),
        salience = 87)
    def ask_current_arrival_time(self):
        if 'minutes' in self.dictionary[0]:
            predictDelayTime = self.dictionary[0].get('minutes')
            self.declare(Fact(predictDelayTime = predictDelayTime[0]))
            self.knowledge['predictDelayTime'] = predictDelayTime[0]
            self.dictionary[0]['minutes']
        else:
            if self.knowledge['question'] == 'ask_predict_delay':
                Message.send_feedback('unknown_message',self.dictionary[1],self.dictionary[2])
            else:
                self.knowledge['question'] = 'ask_predict_delay'
            Message.send_feedback('ask_predict_delay',self.dictionary[1],self.dictionary[2])
            self.declare(Fact(isQuestion = True))

    @Rule(Fact(service = 'predict'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(predictReturnTime = W())),
        salience = 86)
    def ask_predict_return_time(self):
        if 'minutes' in self.dictionary[0]:
            minutes = self.dictionary[0].get('minutes')
            self.declare(Fact(predictDelay = minutes))
            self.knowledge['predictDelay'] = minutes
            self.declare(Fact(informationGiven = False))
            self.knowledge['informationGiven'] = False
            del self.dictionary[0]['name']
        else:
            if self.knowledge['question'] == 'ask_predict_delay':
                Message.send_feedback('unknown_message',self.dictionary[1],self.dictionary[2])
            else:
                self.knowledge['question'] = 'ask_predict_delay'
            Message.send_feedback('ask_predict_delay',self.dictionary[1],self.dictionary[2])
            self.declare(Fact(isQuestion = True))

    @Rule(Fact(service = 'predict'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(predictDelay = W())),
        salience = 85)
    def ask_predict_delay(self):
        if 'minutes' in self.dictionary[0]:
            minutes = self.dictionary[0].get('minutes')[0]
            self.declare(Fact(predictDelay = minutes))
            self.knowledge['predictDelay'] = minutes
            self.declare(Fact(informationGiven = False))
            self.knowledge['informationGiven'] = False
            del self.dictionary[0]['minutes']
        else:
            if self.knowledge['question'] == 'ask_predict_delay':
                Message.send_feedback('unknown_message',self.dictionary[1],self.dictionary[2])
            else:
                self.knowledge['question'] = 'ask_predict_delay'
            Message.send_feedback('ask_predict_delay',self.dictionary[1],self.dictionary[2])
            self.declare(Fact(isQuestion = True))

    @Rule(Fact(service = 'predict'),
        Fact(informationGiven = False),
        salience = 84)
    def predict_delay(self):
        # To Do: Add Train Delay Prediction Component
        delaytime=str(predict_total(self.knowledge['predictFromLocation'],int(self.knowledge['predictDelayTime'])))
        if delaytime!=NULL:
            #print("there is a total of:"+str(delaytime)+" minutes of delay")
            Message.send_delay(delaytime,self.dictionary[1],self.dictionary[2])
            self.knowledge['informationGiven'] = True
            self.declare(Fact(whatsNext = True))
            self.knowledge['whatsNext'] = True
        else:
            Message.send_feedback('prediction_error',self.dictionary[1],self.dictionary[2])
           

    # Ask Next Stage Rule to progress from one stage to another based on the user input
    @Rule(Fact(whatsNext = True),
        salience = 83)
    def whats_next(self):
        if self.knowledge['question'] == 'whats_next':
            Message.send_feedback('unknown_message',self.dictionary[1],self.dictionary[2])
        else:
            self.knowledge['question'] = 'whats_next'
        Message.send_feedback('whats_next',self.dictionary[1],self.dictionary[2])


# New booking is initialized
engine = Booking()
engine.knowledge = {}

# Knowladge engine based on a dictionary
def process_entities(entities):
    engine.dictionary = entities
    engine.reset()
    engine.run()

# Import Message from server
from server import Message