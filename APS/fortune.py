from flask import Flask, jsonify, abort, request, make_response, url_for
import json
from flask_restful import Api, Resource, reqparse
import random

app = Flask(__name__)
api = Api(app)

global list1
list1 = ["Nunca ", "Sempre ", "As vezes ", "Propositalmente ", "Em nenhuma ocasiao ", "Imediatamente ", "Enfim ", "Somente "]

global list2
list2 = ["crie ", "ame ", "escolha ", "agradeca ", "reflita ", "observe ", "possua ", "finalize ", "limite ", "preveja "]

global list3
list3 = ["medos", "o cinema", "Deus", "o Raul", "a arte", "o futuro", "amar", "muito dinheiro", "pouco dinheiro"] 


class Cookie(Resource):

	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('nome', type = str, location = 'json')

	def __str__(self):
		return self.nome

	def get(self):
		sequencia = []
		loto = "Your lottery numbers are: "
		for x in range(6):
  			sequencia.append(random.randint(0, 60))
		sequencia.sort()
		
		rand1 = random.choice(list1)
		rand2 = random.choice(list2)
		rand3 = random.choice(list3)
		
		texto = str(rand1) + str(rand2) + str(rand3) + "   " + loto + str(sequencia)
		return json.dumps({'text': texto})


@app.route('/healthcheck', methods = ['GET'])
def healthcheck():
	return "",200

api.add_resource(Cookie, '/fortune/', endpoint = 'tasks')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
