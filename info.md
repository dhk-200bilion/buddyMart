도매꾹 상품 정보로 받아온 데이터를 활용한 쿠팡 자동 등록에 필요한 정보 매칭

- 등록상품명
  - 쿠팡 데이터 : data.displayProductName
  - 쿠팡 데이터 : data.generalProductName
  - 쿠팡 데이터 : data.sellerProductName
  - 도매꾹 데이터 : data.domeggook.basis.title
-
- 키워드
  - 쿠팡 데이터 : data.displayProductName
  - 도매꾹 데이터 : data.domeggook.basis.keywords.kw
- 카테고리

  - 쿠팡 데이터 : data.displayCategoryCode
  - 쿠팡 카테고리 추천 API 활용 - 참조 API URL : https://developers.coupangcorp.com/hc/ko/articles/360033509234-%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC-%EC%B6%94%EC%B2%9C - 파라미터 - productName : 상품명(data.domeggook.basis.title)
    ```json
    {
      "code": 200,
      "message": "OK",
      "data": {
        "autoCategorizationPredictionResultType": "SUCCESS",
        "predictedCategoryId": "63950",
        "predictedCategoryName": "일반 섬유유연제",
        "comment": null
      }
    }
    ```

- 판매가격
  - data.domeggook.price.dome
- 판매 시작일
  - data.domeggook.basis.dateStart
- 판매 종료일
  - data.domeggook.basis.dateEnd
- 판매 수량
  - data.domeggook.qty.inventory
- 판매 단위
  - data.domeggook.qty.domeUnit
