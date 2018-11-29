'''
FLASK_APP=hello.py flask run
 * Running on http://localhost:5000/

'''

from flask import Flask, jsonify, abort, request, make_response, url_for
import json
from flask_restful import Api, Resource, reqparse


app = Flask(__name__)
api = Api(app)

global tarefas 
tarefas = [{'id': 0, 'nome': 'banana'}]
id_incremental = 1

'''
@app.route("/")
	def hello():
		return "Hello World!"
'''

class Tarefa(Resource):

	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('nome', type = str, location = 'json')

	def __str__(self):
		return self.nome

	#1
	#@app.route('/tarefa', methods = ['GET'])
	def get(self):
		return jsonify({'tarefas': tarefas})

	#2
	#@app.route('/tarefa', methods=['POST'])
	def post(self):
		global id_incremental
		#Tarefa tem nome (dado obtida do request) e id (auto incrementado)
		value = json.loads(request.data.decode("utf-8"))
		tarefas.append({"id":id_incremental,"nome":value["nome"]}) #Tarefa(request.data, id_incremental)
		id_incremental += 1
		#retorna um 201
		return jsonify({'status': 201})

class TarefaId(Resource):
	#3
	#@app.route('/tarefa/<int:task_id>', methods=['GET'])
	def get(self, task_id):
		tarefa = [tarefa for tarefa in tarefas if tarefa['id'] == task_id]
		if len(tarefa) == 0:
			abort(404)
		return jsonify({'tarefa': tarefa[0]})

	#4
	#@app.route('/tarefa/<int:task_id>', methods=['PUT'])
	def put(self, task_id):
		value = json.loads(request.data.decode("utf-8"))
		for i in tarefas:
			if i["id"] == int(value["id"]):
				i["nome"] = value["nome"]
		if len(tarefas) == 0:
			abort(404)
		return jsonify({"status": "OK"})

	#5
	#@app.route('/tarefa/<int:task_id>', methods=['DELETE'])
	def delete(self, task_id):
		value = json.loads(request.data.decode("utf-8"))
		global tarefas
		tarefas = [tarefa for tarefa in tarefas if tarefa['id'] != int(value["id"])]
		return jsonify({"status": "OK"})

@app.route('/healthcheck', methods = ['GET'])
def healthcheck():
	return "",200

api.add_resource(Tarefa, '/tarefa/', endpoint = 'tasks')
api.add_resource(TarefaId, '/tarefa/<task_id>', endpoint = 'task')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
