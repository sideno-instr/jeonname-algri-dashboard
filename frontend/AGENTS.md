<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# 전남 농수산물 가격 변동 및 수급 위험 분석 대시보드를 단계적으로구현한다.
# 현재 프로젝트의 기본 구조는 이미 수동으로 생성되어 있다.
## 고정 기술 스택:
- Frontend: Next.js, TypeScript, App Router, Tailwind CSS, Recharts
- Backend: Python, FastAPI, Pydantic, pandas, httpx
- LLM: LangChain 과 Gemini 또는 현재 설정된 LLM
- Data: KAMIS Open API
- 실행 환경: 로컬
- 배포: 제외

## 최종 기능:
1. 품목 선택
2. 조회 기간 선택
3. KAMIS 가격 데이터 조회
4. 현재가, 평균가, 최고가, 최저가, 변동률 계산
5. 가격 변동성과 변동률을 이용한 수급 위험 추정 지수 계산
6. 가격 추이 선 그래프
7. 위험 등급 표시
8. 버튼을 눌렀을 때 LangChain 기반 AI 분석 생성
9. 데이터 출처와 분석 한계 표시

## 중요한 범위 제한:
- 로그인과 회원가입을 구현하지 않는다.
- 데이터베이스를 사용하지 않는다.
- 배포하지 않는다.
- SSE 스트리밍을 구현하지 않는다.
- 도구 호출형 챗봇을 구현하지 않는다.
- 멀티 에이전트를 구현하지 않는다.
- LangGraph 는 선택 기능이며 기본 구현에서는 사용하지 않는다.
- 실제 수급량 데이터가 없으므로 결과 이름은 반드시 '수급 위험 추정 지수'로 표시한다.
- KAMIS 실제 응답에 없는 필드를 임의로 만들지 않는다.
- 확인하지 않은 품목 코드와 API 응답 필드를 추측하지 않는다.
- API 키를 코드에 직접 작성하지 않는다.

## 작업 규칙:
1. 내가 지정한 단계만 구현한다.
2. 작업 전에 현재 파일 구조와 관련 코드를 먼저 확인한다.
3. 기존 코드를 불필요하게 삭제하거나 전체 구조를 변경하지 않는다.
4. 다음 단계의 기능을 미리 구현하지 않는다.
5. 구현 후 실행 명령과 확인 방법을 제시한다.
6. 오류가 발생하면 원인을 먼저 설명하고 최소 범위만 수정한다.
7. 프론트엔드에서 KAMIS 와 LLM 을 직접 호출하지 않는다.
8. 외부 API 호출과 LLM 호출은 모두 FastAPI 에서 수행한다.
9. 데이터가 부족하면 값을 꾸며내지 말고 계산 불가 또는 데이터 부족으로 표시한다.

## 완료 보고 형식:
- 확인한 기존 파일
- 생성하거나 수정한 파일
- 구현한 기능
- 실행 명령
- 확인 결과
- 남은 문제