# 📈 😊 SmileStock
주식 초보자를 위한 한줄에 보는 종목 종가 예측, 재무제표, 기사 감성분석
9oormthon Training (팀프로젝트)
- 개발 동기 : 진입장벽이 있는 주식 시장에 어려움을 느끼는 초보자들에게 종목 정보를 쉽게 제공하기 위해
- 개발 인원 : 4인
- 진행 기간 : 2024.02. - 2024.04.
- 사용 기술 : Flask, RDS(MySQL), EKS, ECR, Jenkins, FinanceDataReader, Keras, LSTM
- 담당 역할 : 종목 종가 예측, CI/CD, API 문서화

## 서비스 요약
- 사용자는 관심 종목 코드를 입력합니다. 해당 종목의 기사 감정, 종가 예측, 제무 분석 정보가 한 줄로 요약되어 나옵니다.
- 기사 감정 : 경우 크롤링을 통해 모든 기사의 감정을 분석하고, 상세 페이지에서 각 기사의 정보와 감정 결과를 확인할 수 있습니다.
- 종가 예측 : FinanceDataReader 라이브러리로 종목의 10년치 종가를 불러와 LSTM 모델을 통해 종가 정보를 예측합니다.
- 제무 분석 : Dart API로 종목의 제무 정보를 가져오고, Chat GPT API를 통해 제무 정보를 분석합니다.
- CI : Jenkins를 활용해 Github repo의 코드 변화를 감지해 ECR에 지속적으로 서비스의 이미지를 푸쉬합니다.
- CD : 푸쉬한 이미지를 Argo CD가 감지해 EKS 클러스터 내부 POD로 지속적인 배포를 합니다.

[서비스 흐름 영상](https://foreveryoung97.tistory.com/130)
[개발 회고](https://foreveryoung97.tistory.com/category/SmileStock) <br>
