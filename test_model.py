from training_model import create_predict_data, currency_unit_adjustment
from tensorflow.keras.models import load_model
import numpy as np

# 모듈 사용 예시 입니다.

n = 1
stock = "005930.KS"
windown_size = 30
# training_model(n, stock, windown_size)

# 모델 파일 경로
model_path = 'predict_' + stock + '.h5'
# 모델 불러오기
model = load_model(model_path)
close_prices, window, result_list = create_predict_data(n, stock, windown_size)

# 데이터를 모델의 입력 형태에 맞게 조정해 주는 과정입니다.
row = int(round(result_list.shape[0] * 0.9))
x_test = result_list[row:, :-1]
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
x_test.shape

predictions = model.predict(x_test)
pre_price = currency_unit_adjustment(predictions, window)

pre_close_price = close_prices[-1] - pre_price[-1]
print(pre_close_price)
if pre_close_price < 0:
    print("하향")
elif pre_close_price > 0:
    print("상향")
else:
    print("양호")
