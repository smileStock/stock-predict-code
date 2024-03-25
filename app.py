from flask import Flask, request, jsonify
from flask_restx import Api, Resource
import pymysql
from training_model import training_model, predict_stock

# Flask 객체 인스턴스 생성
app = Flask(__name__)
app.config.from_pyfile('config.py')

# Flask-RESTx Api 객체 생성
api = Api(app, version='1.0', title='Stock API', description='A simple Stock Prediction API')

# 데이터베이스 연결 설정
db = pymysql.connect(
    host=app.config['DATABASE_HOST'],
    user=app.config['DATABASE_USER'],
    password=app.config['DATABASE_PASSWORD'],
    charset='utf8'
)

# 기존 뷰를 리소스로 변경
@api.route('/')
class Index(Resource):
    def get(self):
        return 'Hello World!'

@api.route('/train_model')
class TrainModel(Resource):
    def get(self):
        stock = request.args.get('stock')
        if not stock:
            return {'error': 'Stock parameter is missing'}, 400

        try:
            training_model(10, stock, 30)
            return {'message': 'Model training completed successfully'}, 200
        except Exception as e:
            return {'error': str(e)}, 500

@api.route('/predict_stock')
class PredictStock(Resource):
    def get(self):
        stock = request.args.get('stock')
        try:
            prediction = predict_stock(stock, 30)
            return {'stock': stock, 'prediction': prediction}, 200
        except Exception as e:
            return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
