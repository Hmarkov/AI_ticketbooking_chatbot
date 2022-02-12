import re, dateutil.parser, en_core_web_sm
from spacy.lang.en import English as english

parser = english()
nlp = en_core_web_sm.load()

# Regular expressions to recognise specific words
greeting = re.compile(r'\b(?i)(hello|hey|hi)\b')
true = re.compile(r'\b(?i)(true|yes|yeah|yh)\b')
false = re.compile(r'\b(?i)(false|no|nah)\b')
fromTo = re.compile(r'(?i)(.*) to (.*)')
toFrom = re.compile(r'(?i)(.*) from (.*)')
time = re.compile(r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$')

#Function to process and recognise specific word
def get_entities(tx,s,addr):
	message = tx
	message = nlp(message)

	results = {}
	results['service'] = 'chat'

	#Initial greeting response
	if greeting.search(str(message)):
		results['greeting'] = 'true'

	#Name required for friendlier converastion 
	hasName = False
	for entity in message.ents:
		if entity.label_ == 'PERSON':
			results['name'] = entity.text
			hasName = True
	if not hasName and len(str(message).split()) == 1 and not ('greeting' in results):
		results['name'] = str(message)

	#Answer
	if false.search(str(message)):
		results['answer'] = 'false'
	if true.search(str(message)):
		results['answer'] = 'true'

	#Locations
	locations = []
	toMatch = toFrom.search(str(message))
	if toMatch:
		locations.append(toMatch[0].split()[0])
		locations.append(toMatch[0].split()[2])
	fromMatch = fromTo.search(str(message))
	if fromMatch:
		locations.append(fromMatch[0].split()[0])
		locations.append(fromMatch[0].split()[2])
	if len(locations) > 0:
		results['location'] = locations

	minutes = []
	dates = []
	times = []
	for entity in message.ents:
		# Minutes
		if entity.text.isdigit():
			minutes.append(entity.text)
		# Dates
		if entity.label_ == 'DATE':
			try:
				date = dateutil.parser.parse(entity.text)
				date = str(date.day).zfill(2) + str(date.month).zfill(2) + (str(date.year)[2:])
				dates.append(date)
			except:
				Message.send_feedback('wrong_date')
		# Times
		if entity.label_ == 'TIME':
			date = dateutil.parser.parse(entity.text)
			times.append(str(date.hour).zfill(2) + str(date.minute).zfill(2))
	if time.search(str(message)):
		date = dateutil.parser.parse(str(message))
		times.append(str(date.hour).zfill(2) + str(date.minute).zfill(2))

	if len(minutes) > 0:
		results['minutes'] = minutes
	if len(dates) > 0:
		results['dates'] = dates
	if len(times) > 0:
		results['times'] = times

	# Service/Is Return
	for token in message:
		token = str(token).lower()

		if token in { 'delay','predict', 'prediction', 'delays','predictions'}:
			results['service'] = 'predict'

		if token in {'ticket', 'book', 'booking', 'bookings','travel', 'travels'}:
			results['service'] = 'book'

		if token in {'return', 'returns'}:
			results['return'] = 'true'

	if 'back' in str(message):
		results['return'] = 'true'

	return results,s,addr

from server import Message