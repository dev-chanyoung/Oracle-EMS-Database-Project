# 🏢 Enterprise Employee Management System (EMS) - Database Design & SQL

> **Oracle DB 기반의 사원 관리 시스템 데이터베이스 구축 프로젝트**
> **초점:** 데이터 표준화, 정규화 모델링, 제약조건 및 통계/검색 SQL 최적화 기반 마련

<br>

## 1. Project Overview
기업의 인사 정보(사원, 부서, 평가, 프로젝트 등) 관리를 위한 데이터베이스 구축 프로젝트입니다.
4인 팀 프로젝트에서 팀장으로서 요구사항 분석, 데이터 표준화, ERD 설계, 물리 DDL 작성, 백엔드 연동용 SQL 작성 등 **데이터베이스 모델링 및 SQL 작성**을 담당했습니다.

* **개발 기간:** 2024.09 ~ 2024.12 (약 14주)
* **참여 인원:** 4명
* **담당 역할:** 팀장, 데이터베이스 설계 및 SQL 작성
* **주요 업무:**
    * 데이터 표준화 수립 (표준 용어, 도메인, 코드 정의)
    * 개념/논리/물리 데이터 모델링 (ERD 설계, 정규화 적용)
    * MView 및 인덱스를 활용한 검색/통계 쿼리 성능 개선 기반 마련
    * 통계 쿼리 및 동적 검색을 위한 Native SQL 베이스라인 작성

*(※ Python Flask 웹 애플리케이션(`src/`)은 다른 팀원이 구현했습니다. 본 문서는 본인이 담당한 **DB 설계 및 SQL 작성 산출물**을 중심으로 작성했습니다. 프로젝트 이후 진행한 민감정보 암호화 개선(4.E)은 본인이 `src/`에 직접 반영했습니다.)*

<br>

## 2. Tech Stack
| Category | Technology |
| :--- | :--- |
| **Database** | Oracle Database (XE) |
| **Modeling** | DA# (Data Architecture), SQL Developer |
| **Language** | Native SQL (DDL, DML, DQL) |
| **Security** (프로젝트 이후 개선) | Python `cryptography` (AES-256-GCM), `werkzeug.security` (scrypt 해시) |

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
    * **정규화 적용:** 중복 데이터를 줄여 갱신 이상(Anomaly)을 방지하도록 설계했습니다. 다만 엄밀한 제3정규형은 아닙니다. `employee.skill_set`은 여러 스킬을 쉼표로 이은 문자열 한 컬럼이고, `salary`는 `contract_id`로 정해지는 `employee_id`를 함께 가집니다. 평가 항목(업무 수행/커뮤니케이션)은 `evaluation_type` 컬럼으로 한 테이블에 합쳤습니다(팀 보고서 주요 결정사항 1: 조인을 줄이는 대신 중복을 감수).
    * **이력 관리 고려:** 급여 및 계약(`CONTRACT`, `SALARY`) 테이블과 프로젝트 참여 이력(`PARTICIPATION_PROJECT`)을 설계하여 시간에 따른 데이터 변동 추적. `CONTRACT`와 `SALARY`는 발생일(`contract_date`, `salary_date`) 하나만 두고 날짜별로 행을 쌓는 방식이라 종료일은 없습니다(앱은 계약을 `contract_date` 최신순으로 골라 씁니다). 시작일·종료일·역할은 `PARTICIPATION_PROJECT`에만 있습니다.
    * **참여 이력 설계 근거:** 요구사항 정의서의 "참여 인원은 언제든 바뀔 수 있다", "특정 시점에 어떤 직원이 어떤 프로젝트·직무에 참여했는지 알 수 있어야 한다"를 반영해 `PARTICIPATION_PROJECT`에 시작일·종료일·역할을 두었습니다. 참여가 끝나면 행을 삭제하지 않고 종료일을 기록하도록 CRUD 매트릭스에 정의했습니다(참여 종료 = Update).

<br>

## 4. Key Features & Implementation (주요 성과)

### A. 제약조건을 활용한 데이터 무결성 확보
* 애플리케이션의 검증 로직에만 의존하지 않고, DB 레벨에서 명시적인 PK/FK 및 `CHECK` 제약조건을 강제하여 이상 데이터가 DB에 들어가지 않도록 했습니다.
* 예: 프로젝트 종료일이 시작일보다 빠를 수 없도록 제한(`CHECK (end_date >= start_date)`), 동료평가 점수 제한(`peer_evaluation`의 `CHECK (score BETWEEN 0 AND 10)`), 역할 제한(`CHECK (role IN (...))`), 평가 유형 제한(세 평가 테이블 모두).
* 범위: 점수 CHECK는 `peer_evaluation`에만 있습니다. `pm_evaluation`, `customer_evaluation`에는 점수 제약이 없고, 앱에도 평가를 입력하는 화면이 없어 이 두 테이블의 점수는 검증되지 않습니다.

### B. Materialized View(구체화 뷰)를 활용한 통계 쿼리 단순화
* 사원, 부서, 현재 참여 중인 프로젝트 개수 등 여러 테이블(`employee`, `department`, `participation_project`)에 분산된 데이터를 대시보드에 노출하기 위해 다중 조인과 집계 연산(`GROUP BY`)이 포함된 복잡한 쿼리를 작성했습니다.
* 백엔드가 매번 다중 조인·집계 쿼리를 작성하지 않도록, 해당 결과를 `employee_search_mv` 구체화 뷰로 생성하여 단일 뷰 조회로 구조를 단순화했습니다. (성능을 측정하지는 않았으며, 설계 단계에서 쿼리 복잡도를 줄이는 것이 목적이었습니다.)
* 프로젝트 당시(팀 보고서 기준) 이 MV의 컬럼은 `username`, `employee_name`, `department_name`, `current_projects` 4개였습니다. 프로젝트 이후(2026-09-28) 검색 화면이 MV에 없는 컬럼(사원번호·전화번호·이메일)을 조회하던 오류를 고치면서 `employee_id`, `employee_phone_number`, `employee_email`을 추가했습니다.

### C. 검색 패턴 분석을 통한 단일 인덱스 적용
* 사용자 동적 검색에서 빈번하게 조회 조건으로 사용되는 주요 컬럼(사원명, 부서명)을 분석했습니다.
* 해당 컬럼에 B-Tree 단일 인덱스(`idx_employee_name`, `idx_department_name`)를 생성하여, 완전 일치(Equal) 검색 조건 발생 시 Full Table Scan을 방지할 수 있는 성능 개선의 기반을 마련했습니다.

### D. 복잡한 통계 및 동적 검색을 위한 SQL 제공
* 백엔드 개발자가 사용자 입력 조건에 따라 동적 WHERE 절을 쉽게 조합할 수 있도록, 기준이 되는 베이스 Native SQL과 서브쿼리 문을 직접 도출하여 제공했습니다.

### E. 민감정보 평문 저장 개선 (프로젝트 이후)
정보보안 마이크로디그리 과정(컴퓨터보안 등)을 학습하며 민감정보 평문 저장의 위험을 배운 뒤, 이 프로젝트의 `employee` 테이블을 다시 점검했습니다.

* **발견한 문제**
    * 주민등록번호(`registration_number`)가 `VARCHAR2(14)` 평문으로 저장되고 있었습니다.
    * DDL에는 비밀번호 컬럼을 `-- 암호화된 비밀번호`로 설계해 두었지만, 실제 코드는 입력값을 그대로 저장하고 있었고 수정 화면에서 비밀번호를 다시 조회해 보여주고 있었습니다. 설계 의도가 구현에 반영됐는지 당시 확인하지 않았던 것입니다.
    * 저장 완료 메시지에 입력값 전체(주민등록번호·비밀번호 포함)를 그대로 출력하고 있었습니다.
* **조치** (`src/security.py`)
    * **비밀번호:** 복호화할 필요가 없으므로 `werkzeug.security`의 scrypt 단방향 해시만 저장합니다. 수정 화면에서는 조회하지 않고, 새로 입력했을 때만 바꿉니다.
    * **주민등록번호:** 원문이 필요할 수 있어 AES-256-GCM으로 암호화해 저장합니다(무작위 nonce + 인증 태그, base64 인코딩). 키는 DB가 아닌 환경변수(`RRN_ENCRYPTION_KEY`)로 분리했고, 화면에는 `900101-1******`처럼 마스킹한 값만 보여줍니다. 암호문 길이에 맞춰 컬럼을 `VARCHAR2(100)`으로 넓혔습니다.
    * 완료 메시지에는 ID만 출력하도록 바꿨습니다.
* **기존 데이터 전환** (`src/migrate_sensitive_data.py`): 이미 평문으로 쌓인 행을 해시/암호문으로 바꿉니다. 컬럼 길이를 먼저 확인해 넓히고, 이미 전환된 행은 건너뛰므로 여러 번 실행해도 결과가 같습니다.

```bash
# 1) 32바이트 키 생성 후 환경변수로 등록 (키는 저장소에 올리지 않는다)
python -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"
export RRN_ENCRYPTION_KEY=<생성한 키>

# 2) 01_ddl_schema.sql, 02_dml_seed_data.sql 적재 후 평문 데이터 전환
cd src && python migrate_sensitive_data.py
```

<br>

## 5. Directory Structure (DB & Docs 중심)
```text
Oracle-EMS-Database-Project
├── docs/                      # 📂 DB 설계 산출물 (핵심 포트폴리오)
│   ├── 01_Requirements.xlsx   # 요구사항 정의서
│   ├── 02_Standardization.xlsx# 표준 용어/도메인/코드 정의서
│   ├── 03_ERD_Model.pdf       # 논리/물리 데이터 모델링 (ERD)
│   └── 04_CRUD_Matrix.xlsx    # 기능-엔터티 상관관계 분석
│
├── sql/                       # 💾 SQL 스크립트
│   ├── 01_ddl_schema.sql      # 테이블, 제약조건, 뷰, 인덱스 생성
│   └── 02_dml_seed_data.sql   # 기초 테스트 데이터 적재 (평문, 적재 후 전환 스크립트 실행)
│
└── src/                       # Flask 웹 애플리케이션 (다른 팀원 구현)
    ├── security.py            # 비밀번호 해시, 주민등록번호 암호화·마스킹 (이후 개선)
    └── migrate_sensitive_data.py # 기존 평문 데이터 전환 (이후 개선)
```

<br>

## 6. Retrospective & Limitations (회고 및 한계점)
본 프로젝트를 통해 DB 설계 및 쿼리 작성의 기초를 다졌으나, 실무적인 관점에서 다음과 같은 구조적 한계점과 개선 방향을 명확히 인지하게 되었습니다.

* **MView 동기화(Refresh) 전략 누락:** 통계 쿼리 성능 개선을 위해 구체화 뷰(MView)를 생성했으나, 데이터 동기화 옵션을 명시하지 않아 원본 데이터 갱신 시 정합성이 어긋나는 구조적 결함이 있습니다. 실무 환경에서는 `DBMS_SCHEDULER`를 이용한 야간 배치(`COMPLETE REFRESH`)나 구체화 뷰 로그(MView Log)를 활용한 `FAST REFRESH ON DEMAND` 전략이 반드시 수반되어야 함을 배웠습니다.
* **민감 정보 평문 저장 → 이후 개선:** 기능 구현에 집중하여 주민등록번호와 비밀번호를 평문으로 저장했습니다. 이후 비밀번호는 해시로, 주민등록번호는 AES-256-GCM 암호문으로 저장하도록 고쳤습니다(4.E). 남은 과제도 있습니다. 키 교체(rotation) 절차가 없고, 키를 환경변수로만 관리해 실무라면 KMS 같은 별도 키 관리 체계가 필요합니다. 또 개인정보보호법 제24조의2는 법령 근거 없는 주민등록번호 처리를 금지하므로, 암호화 이전에 이 컬럼을 수집해야 하는지부터 요구사항 단계에서 따졌어야 했습니다.
* **B-Tree 인덱스 스캔의 한계 인지:** 검색 성능을 위해 B-Tree 인덱스를 생성했으나, 동적 검색 환경에서 `LIKE '%검색어%'` 형태의 양방향 와일드카드 검색을 수행할 경우 옵티마이저가 인덱스를 타지 못하고 Full Table Scan을 유발한다는 한계를 프로젝트 이후 학습을 통해 인지했습니다. 검색 패턴에 맞는 인덱스 설계가 중요하다는 점을 배웠습니다.
* **참여 이력 PK의 한계:** `PARTICIPATION_PROJECT`의 PK가 (사원, 프로젝트)라서, 같은 직원이 같은 프로젝트에서 빠졌다가 다시 투입되면 이력이 한 행으로만 남습니다. 재투입까지 추적하려면 시작일을 PK에 포함하거나 별도 대리키를 두어야 합니다.
* **논리적 모델링(슈퍼/서브타입)의 부재:** `peer_evaluation`, `pm_evaluation`, `customer_evaluation` 등 컬럼 구조가 거의 동일한 테이블을 평가자 종류별로 물리적으로 분리하여 스키마를 구성했습니다. 프로젝트 당시 팀 보고서에는 평가 정보를 한 테이블에 합치는 안(조인 불필요, 중복 우려)과 슈퍼/서브타입 안(유지보수 용이, 조인 성능 우려)을 비교한 기록이 있습니다. 지금 시점에서는 시스템 확장성 및 쿼리 중복을 고려할 때, 이를 단일 평가(Evaluation) 엔터티로 통합하고 '평가자 타입' 컬럼으로 분류하는 슈퍼/서브타입 모델링이 더 효율적이라고 판단합니다.
