from asyncio.windows_events import NULL
from datetime import datetime
import requests, json
from bs4 import BeautifulSoup
import datetime

#Class to return a ticket based on accumulated information
class Ticket(object):
    url = str()
    
    #Returns a single ticket 
    def get_ticket_single(fromLocation, toLocation, departDate, departTime):
        parsed_html = Ticket.page_single(fromLocation, toLocation, departDate, departTime)
        return Ticket.get_cheapest_ticket(parsed_html, False, departDate, None,None)

    #Returns a return ticket
    def get_ticket_return(fromLocation, toLocation, departDate, departTime, returnDate, returnTime):
        parsed_html = Ticket.page_return(fromLocation, toLocation, departDate, departTime, returnDate, returnTime)
        return Ticket.get_cheapest_ticket(parsed_html, True, departDate, returnDate,returnTime)

    #URL of Single ticket
    def page_single(fromLoc, toLoc, depDate, depTime):
        url = ('http://ojp.nationalrail.co.uk/service/timesandfares/' + fromLoc + '/' + toLoc
            + '/' + depDate + '/' + depTime + '/dep')
        return Ticket.page_contents(url)

    #URL of Return ticket
    def page_return(fromLoc, toLoc, depDate, depTime, returnDate, returnTime):
        url = ('http://ojp.nationalrail.co.uk/service/timesandfares/' + fromLoc + '/' + toLoc
            + '/' + depDate + '/' + depTime + '/dep/' + returnDate + '/' + returnTime + '/dep')
        return Ticket.page_contents(url)

    #Get parsed HTML response to find specific information
    def page_contents(url):
        Ticket.url = url
        r = requests.get(url)
        return BeautifulSoup(r.text, 'html.parser')

    #Return the cheapest ticket available for Single/Return ticket
    def get_cheapest_ticket(page_contents, isReturn, depDate, returnDate,returnTime):
        try:
            info = json.loads(page_contents.find('script', {'type':'application/json'}).text)
            ticket = {}
            ticket['url'] = Ticket.url
            ticket['isReturn'] = isReturn
            ticket['depDate'] =depDate
            ticket['departureStationName'] = str(info['jsonJourneyBreakdown']['departureStationName'])
            ticket['arrivalStationName'] = str(info['jsonJourneyBreakdown']['arrivalStationName'])
            ticket['departureTime'] = str(info['jsonJourneyBreakdown']['departureTime'])
            ticket['arrivalTime'] = str(info['jsonJourneyBreakdown']['arrivalTime'])
            durationHours = str(info['jsonJourneyBreakdown']['durationHours'])
            durationMinutes = str(info['jsonJourneyBreakdown']['durationMinutes'])
            ticket['duration'] = (durationHours + 'h ' + durationMinutes + 'm')
            ticket['changes'] = str(info['jsonJourneyBreakdown']['changes'])
            if isReturn:
                ticket['returnDate'] = returnDate
                ticket['returnTime'] = returnTime
                ticket['fareProvider'] = info['returnJsonFareBreakdowns'][0]['fareProvider']
                ticket['returnTicketType'] = info['returnJsonFareBreakdowns'][0]['ticketType']
                ticket['ticketPrice'] = info['returnJsonFareBreakdowns'][0]['ticketPrice']
            else:
                ticket['fareProvider'] = info['singleJsonFareBreakdowns'][0]['fareProvider']
                ticket['ticketPrice'] = info['singleJsonFareBreakdowns'][0]['ticketPrice']
            return ticket
        except:
            return False