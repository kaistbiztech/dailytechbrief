# 다중 검색 전략 (F2)

SKILL.md `[3] 다중 web_search` 단계의 세부 룰.

## 1. 검색 카테고리 (반드시 모두 커버)

| 카테고리 | 횟수 | 목적 | 쿼리 예시 |
|---|---|---|---|
| **A. 글로벌 자본/딜** | 2~3 | 펀딩·M&A·IPO·실적 시그널 | `"AI funding round [날짜]"`, `"tech M&A [날짜]"`, `"big tech earnings [날짜]"`, `"largest tech deal [날짜]"` |
| **B. 한국 산업·기업** | 2~3 | 한국 빅테크·반도체·플랫폼·스타트업 동향 | `"한국 IT 산업 [날짜]"`, `"한국 AI 산업 [날짜]"`, `"한국 반도체 동향 [날짜]"`, `"한국 테크 스타트업 [주]"`, `"Korea tech news [날짜]"` |
| **C. 화제 아티클·블로그·뉴스레터** | 2~3 | 깊이 있는 분석·인터뷰·인사이드 시각 | `"tech essay this week"`, `"AI analysis newsletter [주]"`, `"테크 칼럼 [주제]"`, `"테크 인사이트 [주제]"` |
| **D. 신서비스·오픈소스** | 1 | 새 제품·OSS 트렌드 | `"GitHub trending this week"`, `"Product Hunt top [주]"`, `"Hacker News top [날짜]"` |

**총 7~10회**. 적으면 후보 부족, 많으면 토큰/시간 낭비.

## 2. 쿼리 작성 원칙

### 원칙 1: 회사명을 박지 마라 (1차 검색은 산업·주제 중심)

- ❌ `"삼성전자 [날짜]"` — 삼성전자만 보임. 다른 회사를 놓침.
- ❌ `"네이버 카카오 쿠팡"` — 이 세 곳 외 SK텔레콤, KT, 토스, 우아한형제들, 두나무, 야놀자, 직방 같은 회사를 누락.
- ✅ `"한국 IT 산업 동향 [날짜]"` — 그날의 핫 이슈가 자동으로 모임.
- ✅ `"한국 AI 스타트업 [날짜]"` — 신생 플레이어까지 잡힘.
- ✅ `"Korean tech industry weekly [날짜]"` — 영문 외신이 본 한국 뉴스.

### 원칙 2: 산업·주제·맥락 키워드 위주

- 산업: `"AI 인프라"`, `"반도체"`, `"파운드리"`, `"플랫폼"`, `"핀테크"`, `"이커머스"`, `"모빌리티"`, `"콘텐츠"`
- 맥락: `"실적 발표"`, `"투자 유치"`, `"인수합병"`, `"신제품"`, `"파트너십"`, `"규제"`, `"해외 진출"`
- 결합: `"한국 AI 스타트업 투자 유치 [주]"`, `"국내 반도체 신제품 [날짜]"`

### 원칙 3: 회사명은 2차 보강 검색에서만

1차 산업 검색에서 잡힌 후보 중 디테일이 부족하면 그때 회사명을 박아 추가 검색:
- 1차: `"한국 반도체 동향 5월 25일"` → 결과에 OCI 등장
- 2차(보강): `"OCI 반도체 소재 사업 재편 2026"` → 정확한 디테일 확보

### 원칙 4: 날짜를 명시적으로

`"AI funding 2026 May"` 보다 `"AI funding round May 26 2026"`이 신선도 게이트를 자연스레 통과한다.

### 원칙 5: 영문·한국어 교차

- 글로벌 시그널은 영문이 빠르고
- 한국 시장 함의는 한국어가 정확하다
- 같은 사건도 영문·한국어로 한 번씩 잡으면 출처가 자연스레 풍부해진다

## 3. 한국어 보도 보조 검색 (선택)

큰 사건이면 한국어 보도가 같이 있는 경우가 많다. 한국어 매체에서 추가 정보(국내 함의·인용·후속)가 잡히면 그 URL을 `sources` 배열에 함께 담아 한국 독자에게 더 친숙하게 만든다.

쿼리 패턴:
- `"[회사명] 한국경제 OR 매일경제 OR 조선비즈"`
- `"[회사명] [핵심 키워드] 사이트:zdnet.co.kr OR 사이트:bloter.net"`

**한국어 보도가 없어도 영문 단독 출처로 후보 통과 가능.** 한국어 매체는 "있으면 좋은 보조"이지 필수가 아니다.

## 4. 신뢰 매체 리스트

### 한국어 (있으면 sources 배열의 앞쪽에 배치)

**종합 비즈니스**: 한국경제, 매일경제, 조선비즈, 머니투데이, 서울경제, 파이낸셜뉴스
**IT 전문**: ZDNet Korea, Bloter, IT조선, 디지털타임스, 전자신문, 테크M, 디지털데일리, AI타임스
**스타트업·벤처**: 더벤처스퀘어, 플래텀, 와우테일, 벤처스퀘어, 비석세스
**아티클·인사이트(C 카테고리 핵심)**: **아웃스탠딩, 더스쿠프, EO, 모비인사이드, 디지털인사이트, 카카오 테크 블로그, 네이버 D2, 우아한형제들 기술 블로그, 토스 기술 블로그, 당근마켓 팀 블로그, 브런치 IT 카테고리**
**종합 일간 IT섹션**: 중앙일보 테크, 동아일보 IT, 한겨레 IT

### 영문 (뒤쪽 보조)

**일반 비즈니스**: Financial Times, Bloomberg, The Wall Street Journal, Reuters
**테크 전문**: TechCrunch, The Verge, Ars Technica, Wired, Engadget
**아티클·뉴스레터(C 카테고리 핵심)**: **The Information, Stratechery (Ben Thompson), Platformer (Casey Newton), Lenny's Newsletter, Every, Not Boring (Packy McCormick), The Generalist, Import AI (Jack Clark), The Pragmatic Engineer, Benedict Evans, Where's Your Ed At**
**아시아**: Nikkei Asia, South China Morning Post, Rest of World
**보안·OSS**: The Hacker News, Hacker News (news.ycombinator.com), Bleeping Computer

## 5. C 카테고리(아티클·뉴스레터) 보강 전략

아티클·블로그 후보가 부족했던 v1 경험에 따라, C 카테고리는 **반드시 2회 이상** 검색한다.

**1차 검색** (광범위):
- `"this week tech essay analysis"`
- `"AI newsletter weekly recap [주]"`
- `"테크 칼럼 인사이트 이번 주"`
- `"한국 테크 블로그 이번 주"`

**2차 검색** (특정 매체):
- `"site:stratechery.com [주제]"`
- `"site:platformer.news [주제]"`
- `"site:theinformation.com [주제]"`
- `"site:outstanding.kr OR site:mobiinside.co.kr [주제]"`
- `"브런치 [회사명 또는 산업]"`

**3차 검색** (이슈 깊이):
- 1차에서 본 후보 중 가장 깊이 있는 사건 1개를 골라 그 사건의 인사이드 분석 검색
- `"[사건명] inside story analysis"`
- `"[사건명] backstory why"`

## 6. 접근 불가 소스 한계

- **Threads / X / Instagram / 카카오톡 채널** 본문은 봇 차단으로 접근 불가.
- 이런 소스가 원천이면 "기사화·블로그화된 2차 소스" 기반으로만 다룬다.
- 1차 SNS 인용이 필수인 사안은 솔직히 한계 고지하고 후보에서 빼는 것을 우선 검토.

## 7. 검색 결과를 후보 풀로 정리

각 후보를 다음 필드로 메모해 두면 큐레이션 단계에서 빠르다:

```
- 사건 한 줄 요약
- 관련 회사
- 핵심 숫자
- 영문 원문 URL
- 한국어 보도 URL (있으면 추가, 없어도 OK)
- 발행일
- 카테고리 (A/B/C/D)
```
