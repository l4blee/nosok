import json

from flask_restful import Resource, Api

api_manager = Api(prefix='/api')


class PerformanceStatistics(Resource):
    def get(self):
        with open('bot/data/data.json') as f:
            data = json.load(f)

        return {
            'message': 'OK',
            'content': data
        }


class Log(Resource):
    def get(self):
        with open('bot/data/log.log') as f:
            data = f.read()

        return {
            'message': 'OK',
            'content': data
        }


api_manager.add_resource(PerformanceStatistics, '/vars')
api_manager.add_resource(Log, '/log')
