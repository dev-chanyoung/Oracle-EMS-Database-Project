# 🏢 Enterprise Employee Management System (EMS)
> **Oracle DB 기반의 사원 관리 시스템 구축 프로젝트** > **초점:** 데이터 표준화, 정규화 모델링, 그리고 Raw SQL 최적화

<br>

## 1. Project Overview
기업의 인사 정보(사원, 부서, 급여, 계약 등)를 효율적으로 관리하기 위한 웹 애플리케이션 및 데이터베이스 구축 프로젝트입니다.  
단순한 기능 구현을 넘어, **현업 수준의 데이터 모델링 절차(요구사항 분석 -> 개념/논리/물리 설계 -> 구현)**를 준수하여 데이터 무결성과 시스템 안정성을 확보하는 데 주력했습니다.

* **개발 기간:** 2024.09 ~ 2024.12 (약 14주)
* **참여 인원:** 4명 (팀장, DB 설계 및 백엔드 총괄)
* **주요 역할:**
    * 데이터 표준화 수립 (용어, 도메인, 코드 정의)
    * DB 모델링 (ERD 설계, 3NF 정규화)
    * Python Flask 연동 및 비즈니스 로직 구현
    * 복잡한 통계 쿼리 및 동적 검색 쿼리 작성

<br>

## 2. Tech Stack
| Category | Technology |
| :--- | :--- |
| **Backend** | Python 3.9, Flask |
| **Database** | Oracle Database 19c (XE), cx_Oracle |
| **Modeling** | DA# (Data Architecture), SQL Developer |
| **Frontend** | HTML5, CSS3, Jinja2 Template |

<br>

## 3. Core Architecture & Modeling (핵심 역량)
이 프로젝트의 핵심은 **철저한 설계 문서화**와 **데이터 거버넌스 준수**입니다. 소스 코드 작성 전, 다음과 같은 단계를 거쳐 설계를 완료했습니다.

### 3.1. 데이터 표준화 (Data Standardization)
무분별한 컬럼명 사용을 방지하고 데이터 일관성을 유지하기 위해 표준을 수립했습니다. ([docs/02_Standardization.xlsx](docs/02_Standardization.xlsx) 참조)
* **표준 단어:** 사원, 부서, 급여 등 업무 용어 정의
* **표준 도메인:** 문자형(VARCHAR2), 숫자형(NUMBER) 등 데이터 타입 및 길이 표준화
* **표준 코드:** 직급 코드, 부서 코드 등 공통 코드 관리

### 3.2. ERD (Entity Relationship Diagram)
<img width="2758" height="1222" alt="image" src="https://github.com/user-attachments/assets/fff7a06f-df50-4eba-b072-b8c5856b9d95" />

* **설계 특징:**
    * **제3정규형(3NF) 준수:** 중복 데이터를 제거하여 이상 현상(Anomaly) 방지.
    * **관계 설정:** 부서-사원(1:N), 사원-급여(1:N) 등 엔터티 간 관계를 명확히 정의하고 FK 제약조건 설정.
    * **이력 관리:** 연봉 계약(`CONTRACT`) 테이블을 별도로 분리하여 급여 변동 이력을 추적할 수 있도록 설계.

### 3.3. CRUD Matrix
시스템 기능(Create, Read, Update, Delete)과 테이블 간의 상관관계를 매트릭스로 정의하여, 개발 누락을 방지하고 영향도를 분석했습니다. ([docs/04_CRUD_Matrix.xlsx](docs/04_CRUD_Matrix.xlsx) 참조)

<br>

## 4. Key Features & Implementation
ORM(Object Relational Mapping)을 사용하지 않고, **Native SQL**을 직접 작성하여 오라클 DB의 기능을 100% 활용했습니다.

### A. 동적 쿼리 빌더 (Dynamic Query Builder)
* **Challenge:** 이름, 부서, 직급 등 사용자가 입력하는 검색 조건의 조합이 수십 가지가 넘어 고정된 쿼리로는 처리가 불가능.
* **Solution:** Python에서 조건에 따라 `WHERE` 절을 동적으로 생성하는 로직을 구현하고, **바인딩 변수(Bind Variables)**를 사용하여 SQL Injection 방지 및 파싱 부하를 최소화했습니다.
    > *관련 파일: `src/search_views.py` - `build_search_query()` 함수*

### B. 복잡한 급여 정산 로직
* `JOIN`과 서브쿼리를 활용하여 사원의 기본 급여 정보와 현재 계약 상태를 결합해 실지급액을 계산하는 로직을 구현했습니다.
* Oracle의 `NVL`, `LISTAGG` 등 내장 함수를 활용하여 데이터 가공 작업을 DB 레벨에서 처리, 애플리케이션 부하를 줄였습니다.

<br>

## 5. Directory Structure
```text
Oracle-EMS-Project
├── docs/                      # 📂 설계 산출물 (핵심 포트폴리오)
│   ├── 01_Requirements.xlsx   # 요구사항 정의서
│   ├── 02_Standardization.xlsx# 표준 용어/도메인/코드 정의서
│   ├── 03_ERD_Model.pdf       # 데이터 모델링 (ERD)
│   └── 04_CRUD_Matrix.xlsx    # 기능-테이블 상관관계 분석
│
├── sql/                       # 💾 SQL 스크립트
│   ├── 01_ddl_schema.sql      # 테이블 생성 (CREATE)
│   └── 02_dml_seed_data.sql   # 기초 데이터 적재 (INSERT)
│
├── src/                       # 💻 Flask 애플리케이션
│   ├── templates/             # HTML Views
│   ├── views/                 # Blueprints (비즈니스 로직 분리)
│   │   ├── main_views.py
│   │   ├── sign_views.py
│   │   └── search_views.py
│   ├── app.py                 # 앱 실행 및 설정
│   └── db.py                  # Oracle DB 연결 (OS별 Client 경로 자동화)
│
└── README.md                  # 프로젝트 설명서
```
<br>

## 6. Retrospective (회고)
* **DB 중심적 사고:** 자바 개발자로서 평소 소홀했던 DB 설계의 중요성을 깨닫는 계기가 되었습니다. 특히 **"잘못된 설계는 어떤 코드로도 덮을 수 없다"**는 것을 배우며, 초기 모델링에 많은 시간을 투자했습니다.
* **보안 이슈:** 본 프로젝트는 DB 설계 학습에 초점을 맞추었기에 비밀번호 해싱 등 일부 보안 로직은 생략되었습니다. 실무 환경이라면 `werkzeug.security` 등을 활용해 암호화하여 저장해야 함을 인지하고 있습니다.

---
*Developed by Chan-young Yu*
