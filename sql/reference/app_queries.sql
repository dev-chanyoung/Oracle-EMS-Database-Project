-- app_queries.sql
-- 팀원에게 제공한 동적 검색 SQL을 보여주기 위해, 앱 코드에서 따로 옮겨 둔 파일이다.
-- 출처: src/views/search_views.py (build_search_query, fetch_employee_detail), 현재 코드 기준
-- 실행용이 아니라 참고용이다. 파이썬에서 문자열을 이어 붙이는 쿼리를 SQL로 풀어 썼다.

-- ============================================================
-- 1) 직원 목록 검색 (동적 검색)
--    기본 쿼리에, 입력값이 있는 조건만 AND 절로 이어 붙인다 (최소 1개 이상 입력).
--    바인드 변수에는 '%검색어%' 형태로 값이 전달된다.
-- ============================================================

-- 기본 쿼리
SELECT mv.username,
       mv.employee_name,
       mv.department_name,
       mv.current_projects,
       mv.employee_id
FROM employee_search_mv mv
WHERE 1=1

-- 이름을 입력한 경우
 AND mv.employee_name LIKE :employee_name

-- 부서를 입력한 경우
 AND mv.department_name LIKE :department_name

-- 직급(직무)을 입력한 경우: 현재 참여 중인 프로젝트에서 찾는다
 AND EXISTS (SELECT 1 FROM participation_project pp
             WHERE pp.employee_id = mv.employee_id
               AND pp.end_date IS NULL
               AND pp.role LIKE :role)

-- 전화번호를 입력한 경우
 AND mv.employee_phone_number LIKE :phone

-- 이메일을 입력한 경우
 AND mv.employee_email LIKE :email;

-- ============================================================
-- 2) 직원 세부정보 조회
-- ============================================================
SELECT
    e.username,
    e.employee_name,
    d.department_name,
    (SELECT COUNT(*) FROM participation_project pp WHERE pp.employee_id = e.employee_id) AS project_count,
    e.education_level,
    e.skill_set,
    e.employee_email,
    e.employee_phone_number,
    e.employee_address,
    (SELECT c.annual_salary
     FROM contract c
     WHERE c.employee_id = e.employee_id
     ORDER BY c.contract_date DESC
     FETCH FIRST 1 ROWS ONLY) AS current_annual_salary,
    NVL(
        (SELECT LISTAGG(TO_CHAR(salary_date, 'YYYY-MM') || ': ' || monthly_salary, ', ')
         WITHIN GROUP (ORDER BY salary_date)
         FROM salary s
         WHERE s.employee_id = e.employee_id
         AND EXTRACT(YEAR FROM salary_date) = EXTRACT(YEAR FROM SYSDATE)
        ), 'No salary records'
    ) AS monthly_salaries
FROM employee e
JOIN department d ON e.department_id = d.department_id
WHERE e.employee_id = :employee_id;
