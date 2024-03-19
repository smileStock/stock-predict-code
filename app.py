from flask import Flask, request, jsonify
import pymysql
from training_model import training_model

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


# 접속 url 생성
@app.route('/')
def index():
    return 'Hello World!'


@app.route('/train_model', methods=['GET'])
def train_model():
    if request.method == 'GET':
        stock = request.args.get('stock')
        window_size = request.args.get('window_size', 30)  # 기본값으로 30을 사용
        n = request.args.get('n', 10)  # 기본값으로 10을 사용

        if not stock:  # stock 값이 제공되지 않은 경우 오류 메시지 반환
            return jsonify({'error': 'Stock parameter is missing'}), 400

        try:
            training_model(n, stock, window_size)

            return jsonify({'message': 'Model training completed successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/predict_stock', methods=['GET'])
def predict_stock():
    stock = request.args.get('stock')
    window_size = request.args.get('window_size', 30)  # 기본값으로 30을 사용

    try:
        prediction = predict_stock(stock, int(window_size))
        return jsonify({'stock': stock, 'prediction': prediction}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # 코드 수정 시 자동 반영
    app.run(debug=True)
