-- example_queries.sql
-- 테스트를 쉽게 하기 위한 예시 쿼리 모음 (2026-10 추가).
-- 시드(02_dml_seed_data.sql)를 적재한 DB에서 SQL Developer 등으로 한 문장씩 실행해 결과를 확인한다.
-- 각 쿼리 아래의 "시드 기준" 값은 시드 데이터를 같은 조건으로 계산한 값이다.

-- 1) 특정 시점에 참여 중이던 직원·프로젝트·직무 조회
--    종료일이 비어 있으면 현재 진행 중인 참여이므로 end_date IS NULL 도 함께 본다.
SELECT e.employee_name, p.project_name, pp.role
FROM participation_project pp
JOIN employee e ON e.employee_id = pp.employee_id
JOIN project  p ON p.project_id  = pp.project_id
WHERE pp.start_date <= DATE '2024-06-30'
  AND (pp.end_date IS NULL OR pp.end_date >= DATE '2024-06-30');
-- 시드 기준: 14건 (9개 프로젝트)

-- 2) 현재 진행 중인 참여 목록 (종료일이 없는 참여)
SELECT pp.employee_id, pp.project_id, pp.role, pp.start_date
FROM participation_project pp
WHERE pp.end_date IS NULL
ORDER BY pp.start_date;
-- 시드 기준: 43건

-- 3) 사원별 현재 참여 프로젝트 수 (COUNT 집계)
--    employee_search_mv 의 정의와 같은 집계를 원본 테이블로 직접 계산한다.
SELECT e.employee_id, e.employee_name, COUNT(pp.project_id) AS current_projects
FROM employee e
LEFT JOIN participation_project pp
       ON e.employee_id = pp.employee_id AND pp.end_date IS NULL
GROUP BY e.employee_id, e.employee_name
HAVING COUNT(pp.project_id) > 0
ORDER BY current_projects DESC, e.employee_id;
-- 시드 기준: 34명, 가장 많은 사원은 4건 (employee_id 18)

-- 4) 검색용 Materialized View 조회
--    MView 는 자동으로 갱신되지 않으므로, 시드를 적재한 뒤 한 번 갱신해야 값이 나온다.
--    EXEC DBMS_MVIEW.REFRESH('EMPLOYEE_SEARCH_MV');
SELECT employee_id, employee_name, department_name, current_projects
FROM employee_search_mv
WHERE current_projects > 0
ORDER BY current_projects DESC;

-- 5) 계약과 급여는 행을 쌓아 이력을 보존한다 (직원 2번 예시)
SELECT contract_id, contract_date, annual_salary
FROM contract
WHERE employee_id = 2
ORDER BY contract_date;
-- 시드 기준: 6건

SELECT TO_CHAR(salary_date, 'YYYY-MM') AS salary_month,
       base_salary,
       monthly_salary,
       monthly_salary - base_salary AS incentive
FROM salary
WHERE employee_id = 2
  AND EXTRACT(YEAR FROM salary_date) = 2024
ORDER BY salary_date;
-- 시드 기준: 11건 (2024-01 ~ 2024-11)

-- 6) 제약 확인: 아래 문장들은 CHECK 제약 때문에 실패해야 한다 (실패하지 않으면 제약이 빠진 것이다).
--    employee 1, project 1·2 는 시드에 참여 이력이 없어 기본키 충돌 없이 CHECK 만 확인된다.

-- 참여 종료일이 시작일보다 빠름 -> CK_ParticipationProject_EndDates 위반 예상
INSERT INTO participation_project (employee_id, project_id, start_date, end_date, role)
VALUES (1, 1, DATE '2024-02-01', DATE '2024-01-01', 'PM');

-- 허용되지 않은 직무 값 -> CK_ParticipationProject_role 위반 예상
INSERT INTO participation_project (employee_id, project_id, start_date, end_date, role)
VALUES (1, 2, DATE '2024-02-01', DATE '2024-03-01', 'Manager');

-- 프로젝트 종료일이 시작일보다 빠름 -> CK_Project_EndDate 위반 예상
INSERT INTO project (project_id, customer_id, project_name, start_date, end_date)
VALUES (900001, 1, 'constraint test', DATE '2024-02-01', DATE '2024-01-01');

ROLLBACK;
