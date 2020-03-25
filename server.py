import tornado.ioloop, tornado.web, tornado.websocket, json, re
from __random import RandomOrg

PORT = 1234

class MainHandler(tornado.web.RequestHandler):
	def get(self): self.render("index.html")

class SimpleWebSocket(tornado.websocket.WebSocketHandler):
	connections = set()
	def open(self): self.connections.add(self)
	def on_message(self, message):
		if message['message']:
			message = json.loads(message)
			if message['message'][0] == '!' and not re.search('[a-cA-Ce-zE-Z]', l): # Starting a message with an exclamation point and doesn't contain any characters but basic math, integers, and a d triggers the dice parser
				m = message['message'].lstrip('!').replace(' ', '') # Remove the exclamation and any spaces for formatting purposes
				message['message'] = '<p>Dice Parcer</p>\n' # This starts the newly formatted message to let users know that the following information is from the dice parser
				rollRequests = re.findall(r"[0-9]*d[0-9]*", m) # This searches the string for any dice rolls and stores them in a list: denoted by a #d# or just d# (e.g. 1d20 (d20) to roll a single 20 sided die or 5d10 to roll five ten sided dice
				if rollRequests: # If there are any rolls to be made, they are processed before anything else
					for request in rollRequests: # Iterate through every roll request
						roll = 0 # Initialize the roll total. This tracks the sum total value of each roll from a single request. (e.g. a 2d20 request is made, each roll of the d20 is made independently, and finally both rolls are added together).
						# The followin 3 lines split the request into two numbers: the first is the number of dice to be rolled and the second is the sides of the die (e.g. a d20 equals 20 sides)g
						dParse = request.split('d')
						dParse[0] = int(dParse[0]) if dParse[0] else 1 # If there is no number of rolls given (e.g. d20) then the number of rolls will equal 1
						dParse[1] = int(dParse[1])
						rolls = dice_roll(dParse[0], dParse[1]) # Send the information to the roll manager to be processed which returns a list (even if it is a list of one)
						for i in range(0, len(rolls)): # Proccess each roll and add them to the message
							roll += int(rolls[i])
							message['message'] += f'<p>{i+1}. d{dParse[1]}: {rolls[i]}</p>\n'
						m = m.replace(request, str(roll), 1) # Finally replace the request (#d#) with the roll total
				try: # This attempts to evaluate the string
					total = eval(m, {'__builtins__': None}) # WARNING! Not the most secure way to do this but eliminating characters other than those necessary and preventing built in functions from running should close the hole
				except Exception as e:
					total = e
				message['message'] += f'<p>{m} = {total}</p>\n'
			[client.write_message(message) for client in self.connections]
	def close(self): self.connections.remove(self)

def dice_roll(numRolls, sides):
	integers = RandomOrg()
	integers.get_true_random(type='integers', num=numRolls, min=1, max=sides)
	return integers.data

def make_app(): return tornado.web.Application([ (r"/", MainHandler), (r"/websocket", SimpleWebSocket) ])

if __name__ == '__main__':
	app = make_app()
	app.listen(PORT)
	tornado.ioloop.IOLoop.current().start()