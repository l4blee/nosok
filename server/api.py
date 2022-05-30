import json

from flask_restful import Resource, Api
from flask import send_from_directory



class PerformanceStatistics(Resource):
    def get(self):
        with open('bot/data/data.json') as f:
            data = json.load(f)

        return {
            'message': 'success',
            'content': 'vars',
            'data': data
        }


class Log(Resource):
    def get(self):
        with open('bot/data/log.log') as f:
            data = f.read()
        
        return {
            'message': 'success',
            'content': 'log',
            'data': data
        }
