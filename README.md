# 🏢 Enterprise Employee Management System (EMS) - Database Design & SQL

> **Oracle DB 기반의 사원 관리 시스템 데이터베이스 구축 프로젝트**
> **초점:** 데이터 표준화, 정규화 모델링, 제약조건 및 통계/검색 SQL 최적화 기반 마련

<br>

## 1. Project Overview
기업의 인사 정보(사원, 부서, 평가, 프로젝트 등) 관리를 위한 데이터베이스 구축 프로젝트입니다.
요구사항 분석부터 데이터 표준화, ERD 설계, 물리적 DDL 작성 및 백엔드 연동을 위한 최적화된 SQL 쿼리 도출 등 **데이터베이스 모델링 및 SQL 개발 전반**을 전담했습니다.

* **개발 기간:** 2024.09 ~ 2024.12 (약 14주)
* **담당 역할:** 데이터베이스 설계 및 SQL 개발 총괄 (팀장)
* **주요 업무:**
    * 데이터 표준화 수립 (표준 용어, 도메인, 코드 정의)
    * 개념/논리/물리 데이터 모델링 (ERD 설계, 3NF 정규화 적용)
    * MView 및 인덱스를 활용한 검색/통계 쿼리 성능 개선 기반 마련
    * 통계 쿼리 및 동적 검색을 위한 Native SQL 베이스라인 작성

*(※ 본 프로젝트의 전체 시스템은 Python Flask 웹 애플리케이션으로 구현되었으나, 본 문서는 본인이 직접 전담한 **DB 설계 및 SQL 작성 산출물**에 초점을 맞추어 작성되었습니다.)*

<br>

## 2. Tech Stack
| Category | Technology |
| :--- | :--- |
| **Database** | Oracle Database 19c (XE) |
| **Modeling** | DA# (Data Architecture), SQL Developer |
| **Language** | Native SQL (DDL, DML, DQL) |

<br>

## 3. Core Architecture & Modeling
소스 코드 작성 전, 데이터 거버넌스 준수와 철저한 설계 문서화를 거쳐 DB 구축을 진행했습니다.

### 3.1. 데이터 표준화 (Data Standardization)
무분별한 컬럼명 사용을 방지하고 데이터 일관성을 유지하기 위해 데이터 표준을 수립했습니다. ([docs/02_Standardization.xlsx](docs/02_Standardization.xlsx) 참조)
* **표준 단어:** 사원, 부서, 평가 등 시스템 내에서 사용되는 업무 용어 정의
* **표준 도메인:** 데이터 타입 및 길이(예: VARCHAR2, NUMBER)를 일관되게 적용
* **표준 코드:** 직위, 평가 유형 등 공통 코드화 가능한 데이터 분류

### 3.2. ERD (Entity Relationship Diagram)
<img width="4493" height="3177" alt="03_ERD_Model" src="https://github.com/user-attachments/assets/ef8a4586-107a-405d-bc7f-37ea8466c014" />

* **설계 특징:**
    * **제3정규형(3NF) 준수:** 중복 데이터를 제거하여 갱신 이상(Anomaly) 방지.
    * **이력 관리 고려:** 급여 및 계약(`CONTRACT`, `SALARY`) 테이블과 프로젝트 참여 이력(`PARTICIPATION_PROJECT`)을 설계하여 시간에 따른 데이터 변동 추적.

<br>

## 4. Key Features & Implementation (주요 성과)

### A. 제약조건을 활용한 데이터 무결성 확보
* 애플리케이션의 검증 로직에만 의존하지 않고, DB 레벨에서 명시적인 PK/FK 및 `CHECK` 제약조건을 강제하여 이상 데이터 삽입을 원천 차단했습니다.
* 예: 프로젝트 종료일이 시작일보다 빠를 수 없도록 제한(`CHECK (end_date >= start_date)`), 평가 점수 도메인 제한(`CHECK (score BETWEEN 0 AND 10)`), 역할 제한(`CHECK (role IN (...))`).

### B. Materialized View(구체화 뷰)를 활용한 통계 쿼리 단순화
* 사원, 부서, 현재 참여 중인 프로젝트 개수 등 여러 테이블(`employee`, `department`, `participation_project`)에 분산된 데이터를 대시보드에 노출하기 위해 다중 조인과 집계 연산(`GROUP BY`)이 포함된 복잡한 쿼리를 작성했습니다.
* 백엔드에서 매번 무거운 집계 연산을 수행하는 오버헤드를 줄이고자, 해당 결과를 `employee_search_mv` 구체화 뷰로 생성하여 단일 뷰 조회로 구조를 단순화했습니다.

### C. 검색 패턴 분석을 통한 단일 인덱스 적용
* 사용자 동적 검색에서 빈번하게 조회 조건으로 사용되는 주요 컬럼(사원명, 부서명)을 분석했습니다.
* 해당 컬럼에 B-Tree 단일 인덱스(`idx_employee_name`, `idx_department_name`)를 생성하여, 완전 일치(Equal) 검색 조건 발생 시 Full Table Scan을 방지할 수 있는 성능 개선의 기반을 마련했습니다.

### D. 복잡한 통계 및 동적 검색을 위한 SQL 제공
* 백엔드 개발자가 사용자 입력 조건에 따라 동적 WHERE 절을 쉽게 조합할 수 있도록, 기준이 되는 베이스 Native SQL과 서브쿼리 문을 직접 도출하여 제공했습니다.

<br>

## 5. Directory Structure (DB & Docs 중심)
```text
Oracle-EMS-Project
├── docs/                      # 📂 DB 설계 산출물 (핵심 포트폴리오)
│   ├── 01_Requirements.xlsx   # 요구사항 정의서
│   ├── 02_Standardization.xlsx# 표준 용어/도메인/코드 정의서
│   ├── 03_ERD_Model.pdf       # 논리/물리 데이터 모델링 (ERD)
│   └── 04_CRUD_Matrix.xlsx    # 기능-엔터티 상관관계 분석
│
└── sql/                       # 💾 SQL 스크립트
    ├── 01_ddl_schema.sql      # 테이블, 제약조건, 뷰, 인덱스 생성
    └── 02_dml_seed_data.sql   # 기초 테스트 데이터 적재
```

<br>

## 6. Retrospective & Limitations (회고 및 한계점)
본 프로젝트를 통해 DB 설계 및 쿼리 작성의 기초를 다졌으나, 실무적인 관점에서 다음과 같은 구조적 한계점과 개선 방향을 명확히 인지하게 되었습니다.

* **MView 동기화(Refresh) 전략 누락:** 통계 쿼리 성능 개선을 위해 구체화 뷰(MView)를 생성했으나, 데이터 동기화 옵션을 명시하지 않아 원본 데이터 갱신 시 정합성이 어긋나는 구조적 결함이 있습니다. 실무 환경에서는 `DBMS_SCHEDULER`를 이용한 야간 배치(`COMPLETE REFRESH`)나 구체화 뷰 로그(MView Log)를 활용한 `FAST REFRESH ON DEMAND` 전략이 반드시 수반되어야 함을 배웠습니다.
* **민감 정보(주민등록번호) 평문 저장:** 기능 구현에 집중하여 주민등록번호(`registration_number`)를 `VARCHAR2` 형태의 평문으로 저장했습니다. 이는 보안상 매우 치명적이며, 실제 운영 환경에서는 개인정보보호법에 따라 애플리케이션 단에서 AES-256 등의 양방향 암호화를 거치거나, Oracle TDE(Transparent Data Encryption)를 적용하여 저장해야 함을 깨달았습니다.
* **B-Tree 인덱스 스캔의 한계 인지:** 검색 성능을 위해 B-Tree 인덱스를 생성했으나, 동적 검색 환경에서 `LIKE '%검색어%'` 형태의 양방향 와일드카드 검색을 수행할 경우 옵티마이저가 인덱스를 타지 못하고 Full Table Scan을 유발한다는 점을 실행 계획(Execution Plan) 분석을 통해 확인했습니다. 검색 패턴에 맞는 인덱스 설계의 중요성을 체감했습니다.
* **논리적 모델링(슈퍼/서브타입)의 부재:** `peer_evaluation`, `pm_evaluation`, `customer_evaluation` 등 컬럼 구조가 거의 동일한 테이블을 물리적으로 분리하여 스키마를 구성했습니다. 시스템 확장성 및 쿼리 중복을 고려할 때, 이를 단일 평가(Evaluation) 엔터티로 통합하고 '평가자 타입' 컬럼으로 분류하는 슈퍼/서브타입 모델링을 적용하는 것이 훨씬 효율적인 설계임을 확인했습니다.
