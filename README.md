### Slack 설정

- 테스트 채널 생성
- 이동 - 앱 - incoming-webhook 검색 후 앱 추가
- 전송할 채널 선택, hook url은 AWS Lambda 환경변수로 지정

### AWS SNS

- 메세지 또는 알람을 주고받을 endpoints를 지정할 수 있다.
- 주제 - 주제 생성
  - 유형: 표준

### AWS Lambda

- 런타임 설정
  - 런타임: Python 3.7
  - 핸들러: lambda_function.lambda_handler
  - 아키텍처: x86_64
- 구성
  - 환경변수 추가
    - key: hookUrl, value: slack income-webhook 추가 후 나오는 url
    - key: slackChannel, value: 메세지 전송할 slack 채널. #까지 적는다.
- 코드 작성(lambda_function.py)
  - 메세지 템플릿 확인은 slack의 [Block Kit Builder](https://app.slack.com/block-kit-builder)를 이용한다.
- 테스트 JSON 작성 (test.json)
- 테스트 실행했을 때 slack에 메세지 전송되면 성공
  - 실행 로그는 Cloud Watch에서 확인 가능
  - 에러나면 로그 확인 후 postman에서 요청 보내보자...
- SNS 주제 연결
  - 함수 개요 - 트리거 추가
    - SNS 지정, 생성한 주제 선택

### CodeDeploy 트리거 설정

- 배포그룹 - 편집 - 트리거 - 트리거 생성
  - 이벤트: 언제 메세지 가게 할건지 선택. 배포 성공, 배포 실패를 선택했다.
  - 주제: 생성했던 주제 선택
