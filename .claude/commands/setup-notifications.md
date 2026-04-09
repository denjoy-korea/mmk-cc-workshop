# Slack/Notion 알림 초기 설정

증시 유튜브 요약 알림 시스템의 Slack과 Notion 연동을 설정합니다.

## 실행 순서

### 1단계: 현재 설정 확인

`scripts/config.json` 파일을 읽어 현재 Slack/Notion 설정 상태를 확인하고 사용자에게 보여줍니다.

### 2단계: Slack 설정

사용자에게 Slack 알림을 설정할지 물어봅니다.

설정하려면:
1. Slack MCP 도구 `slack_search_channels`로 관련 채널을 검색합니다
2. 사용자에게 채널을 선택하게 합니다 (또는 채널명을 직접 입력받습니다)
3. `scripts/config.json`의 `slack.channel_id`와 `slack.enabled`를 업데이트합니다
4. 테스트 메시지를 전송하여 연결을 확인합니다:
   `slack_send_message`로 "증시 유튜브 요약 알림이 설정되었습니다." 전송

### 3단계: Notion 설정

사용자에게 Notion 데이터베이스를 설정할지 물어봅니다.

**새로 생성하는 경우:**
1. 사용자에게 데이터베이스를 생성할 Notion 페이지 URL을 요청합니다
2. Notion MCP 도구 `notion-create-database`로 아래 스키마의 DB를 생성합니다:

```sql
CREATE TABLE 증시_유튜브_요약 (
  제목 TITLE,
  채널 SELECT,
  콘텐츠시리즈 SELECT,
  요약 RICH_TEXT,
  핵심포인트 RICH_TEXT,
  언급종목 MULTI_SELECT,
  영상URL RICH_TEXT,
  게시일 DATE,
  처리일 DATE
);
```

3. 생성된 database_id를 `scripts/config.json`에 저장합니다

**기존 DB를 사용하는 경우:**
1. 사용자에게 Notion 데이터베이스 URL을 요청합니다
2. `notion-fetch`로 DB 정보를 확인합니다
3. database_id를 `scripts/config.json`에 저장합니다

4. `scripts/config.json`의 `notion.database_id`와 `notion.enabled`를 업데이트합니다

### 4단계: 설정 완료 확인

최종 설정 상태를 사용자에게 보여줍니다:
- Slack: 활성화 여부 + 채널명
- Notion: 활성화 여부 + DB 이름
- 다음 단계 안내: `/check-videos`로 수동 테스트 또는 `/loop 1h /check-videos`로 자동화 시작
