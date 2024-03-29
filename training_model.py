import os
import numpy as np
from keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pandas_datareader import data as pdr
import yfinance as yf


# 학습하기 위한 데이터를 생성하기 위한 함수입니다.
def create_x_test(n, stock, windown_size):
    yf.pdr_override()

    # now: 현재 날짜, before: n년 전
    now = datetime.now()
    before = now - relativedelta(years=n)

    # before_day 부터 now_day 까지 정보를 가져오기 위해 날짜 값 변환
    now_day = now.strftime("%Y-%m-%d")
    before_day = before.strftime("%Y-%m-%d")

    # stock_data: stock 종목의 n년 데이터
    stock_data = pdr.get_data_yahoo(stock, start=before_day, end=now_day)
    # close_prices: stock 종목의 n년 데이테에서 종가 추출
    close_prices = stock_data['Close'].values
    # close_prices가 비어 있는 경우 예외 발생
    if len(close_prices) == 0:
        raise ValueError("No data available for stock: " + stock)

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
    try:
        x_train, y_train, x_test, y_test, windown_size = create_x_test(n, stock, windown_size)
    except ValueError as e:
        print(e)  # 예외 메시지 출력 또는 로깅
        return -2  # 데이터가 없는 경우 -2 반환

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

    # 모델을 저장하기 전에 경로 확인 및 생성
    model_dir = 'model/' + stock
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)  # 경로가 없으면 생성

    # 모델(파일) 저장
    model.save('model/' + stock + '/predict_' + stock + '.keras')


# stock 종목의 다음날 종가를 예측하여 "상향", "하향", "양호" 값으로 반환합니다.
def get_last_data(n_days, stock):
    ticker = yf.Ticker(stock)

    last_day_price = ticker.history(interval='1d', period='3mo').tail(n_days)['Close'].values

    normal_data = []
    for p in last_day_price:
        normal_data.append(((float(p) / float(last_day_price[0])) - 1))

    return np.array(normal_data), last_day_price


def predict_stock(stock, windown_size):
    # 모델 파일 경로
    model_path = 'model/' + stock + '/predict_' + stock + '.keras'
    # 모델 불러오기
    model = load_model(model_path)

    normal_data, last_day_price = get_last_data(windown_size, stock)
    predict_data = np.reshape(normal_data, (1, windown_size, 1))

    predictions = model.predict(predict_data)
    print(predictions)

    pre_price = (predictions + 1) * last_day_price[0]

    pre_close_price = pre_price - last_day_price[-1]
    print('전일종가:', last_day_price[-1], '예측종가:', pre_price, '차액:', pre_close_price)

    if pre_close_price < 0:
        return 2    # down
    elif pre_close_price > 0:
        return 3    # up
    else:
        return 1    # stay
