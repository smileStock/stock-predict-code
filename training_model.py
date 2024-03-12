import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense
from tensorflow.keras.models import load_model
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pandas_datareader import data as pdr
import yfinance as yf

# n: n달 전 까지의 정보, stock: 종목 코드, windown_size 일 만큼 학습 후 다음 날의 종가 예측


# 학습하기 위한 데이터를 생성하기 위한 함수입니다.
def create_x_test(n, stock, windown_size):
    yf.pdr_override()

    # now: 현재 날짜, before: n년 전
    now = datetime.now()
    before = now - relativedelta(month=n)

    # before_day 부터 now_day 까지 정보를 가져오기 위해 날짜 값 변환
    now_day = now.strftime("%Y-%m-%d")
    before_day = before.strftime("%Y-%m-%d")

    # stock_data: stock 종목의 n년 데이터
    stock_data = pdr.get_data_yahoo(stock, start=before_day, end=now_day)
    # close_prices: stock 종목의 n년 데이테에서 종가 추출
    close_prices = stock_data['Close'].values

    # result_list: n년치 데이터를 windown일 단위로 묶어 하나의 학습 데이터 세트로 가공
    result_list = []
    for i in range((len(close_prices) - (windown_size + 1))):
        result_list.append(close_prices[i: i + (windown_size + 1)])

    # 데이터 가공
    normal_data = []
    for window in result_list:
        window_list = [((float(p) / float(window[0])) - 1) for p in window]
        normal_data.append(window_list)

    # 데이터 가공
    result_list = np.array(normal_data)

    # 학습 데이터로 가공
    row = int(round(result_list.shape[0] * 0.9))
    train = result_list[:row, :]

    # 모델 기준 x_train: 인풋 데이터, y_train: 아웃풋 데이터
    x_train = train[:, :-1]
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    y_train = train[:, -1]

    # x_test: 예측을 위한 테스트 데이터(인풋), y_test: 예측을 위한 테스트 데이터(아웃풋)
    x_test = result_list[row:, :-1]
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    y_test = result_list[row:, -1]

    return x_train, y_train, x_test, y_test, windown_size


# 주가 예측 모델을 학습하여 생성하고, 파일로 저장합니다.
def training_model(n, stock, windown_size):
    x_train, y_train, x_test, y_test, windown_size = create_x_test(n, stock, windown_size)

    # LSTM 모델 생성
    model = Sequential()
    model.add(LSTM(windown_size, return_sequences=True, input_shape=(windown_size, 1)))
    model.add(LSTM(64, return_sequences=False))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mse', optimizer='rmsprop')
    model.summary()

    # 모델 학습
    model.fit(x_train, y_train,
              validation_data=(x_test, y_test),
              batch_size=10,
              epochs=10)

    # 모델(파일) 저장
    model.save('predict_' + stock + '.h5')


# 예측을 위한 데이터를 생성합니다.
def create_predict_data(n, stock, windown_size):
    yf.pdr_override()

    now = datetime.now()
    before = now - relativedelta(month=n)

    now_day = now.strftime("%Y-%m-%d")
    before_day = before.strftime("%Y-%m-%d")

    stock_data = pdr.get_data_yahoo(stock, start=before_day, end=now_day)

    close_prices = stock_data['Close'].values

    result_list = []
    for i in range(len(close_prices) - (windown_size + 1)):
        result_list.append(close_prices[i: i + (windown_size + 1)])

    normal_data = []
    for window in result_list:
        window_list = [((float(p) / float(window[0])) - 1) for p in window]
        normal_data.append(window_list)

    result_list = np.array(normal_data)

    return close_prices, window, result_list


# 예측한 값의 화폐 단위를 조정해 줍니다.
def currency_unit_adjustment(predictions, window):
    pred_price = []
    for i in predictions:
        pred_price.append((i + 1) * window[0])

    return pred_price


# stock 종목의 다음날 종가를 예측하여 "상향", "하향", "양호" 값으로 반환합니다.
def predict_stock(n, stock, windown_size):
    # 모델 파일 경로
    model_path = 'predict_' + stock + '.h5'
    # 모델 불러오기
    model = load_model(model_path)
    close_prices, window, result_list = create_predict_data(n, stock, windown_size)

    row = int(round(result_list.shape[0] * 0.9))
    x_test = result_list[row:, :-1]
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    x_test.shape

    predictions = model.predict(x_test)
    pre_price = currency_unit_adjustment(predictions, window)

    pre_close_price = close_prices[-1] - pre_price[-1]
    print(pre_close_price)
    if pre_close_price < 0:
        return "하향"
    elif pre_close_price > 0:
        return "상향"
    else:
        return "양호"
