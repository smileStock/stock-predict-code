import os
from flask import Flask
from flask_restx import Api, Resource, reqparse
import pymysql
from training_model import training_model, predict_stock

# Flask 객체 인스턴스 생성
app = Flask(__name__)
app.config.from_pyfile('config.py')

# 데이터베이스 연결 설정
db = pymysql.connect(
    host=app.config['DATABASE_HOST'],
    user=app.config['DATABASE_USER'],
    password=app.config['DATABASE_PASSWORD'],
    charset='utf8'
)

# Flask-RESTx Api 객체 생성
api = Api(app, version='1.0', title='Stock API', description='A simple Stock Prediction API')

# TrainModel에 대한 파라미터 파서 정의
train_model_parser = reqparse.RequestParser()
train_model_parser.add_argument('stock', type=str, required=True, help='Stock symbol to train model')

# PredictStock에 대한 파라미터 파서 정의
predict_stock_parser = reqparse.RequestParser()
predict_stock_parser.add_argument('stock', type=str, required=True, help='Stock symbol to predict')


# 기존 뷰를 리소스로 변경
@api.route('/')
class Index(Resource):
    def get(self):
        return 'Hello World!'


@api.route('/train_model')
class TrainModel(Resource):
    @api.expect(train_model_parser)
    def get(self):
        args = train_model_parser.parse_args()
        stock = args['stock']

        if not stock:
            return {'error': 'Stock parameter is missing'}, 400

        try:
            training_model(10, stock, 30)
            return {'message': 'Model training completed successfully'}, 200
        except Exception as e:
            return {'error': str(e)}, 500


@api.route('/predict_stock')
class PredictStock(Resource):
    @api.expect(predict_stock_parser)
    def get(self):
        args = predict_stock_parser.parse_args()
        stock = args['stock']

        # 특정 파일의 경로 지정
        file_path = 'model/' + stock + '/predict_' + stock + '.keras'

        # 파일 존재 여부 확인
        if not os.path.exists(file_path):
            training_model(10, stock, 30)
            return {'stock': stock, 'prediction': 0}, 200
        else:
            try:
                prediction = predict_stock(stock, 30)
                return {'stock': stock, 'prediction': prediction}, 200
            except Exception as e:
                return {'error': str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True)
