-- 03_drop_schema.sql
-- 01_ddl_schema.sql 로 만든 객체를 모두 삭제한다. 테이블의 데이터도 함께 사라진다.
--
-- 삭제 순서: Materialized View -> 테이블(자식 -> 부모) -> 시퀀스
-- 인덱스(idx_department_name, idx_employee_name)는 테이블을 삭제할 때 함께 삭제되므로 따로 지우지 않는다.
-- 처음 실행할 때처럼 객체가 없으면 해당 줄에서 오류가 나지만, 나머지 줄은 계속 실행하면 된다.
-- 다시 만들려면 01_ddl_schema.sql 부터 순서대로 실행한다.

DROP MATERIALIZED VIEW employee_search_mv;

DROP TABLE seminar_participation CASCADE CONSTRAINTS;
DROP TABLE seminar CASCADE CONSTRAINTS;
DROP TABLE incentive CASCADE CONSTRAINTS;
DROP TABLE customer_evaluation CASCADE CONSTRAINTS;
DROP TABLE pm_evaluation CASCADE CONSTRAINTS;
DROP TABLE peer_evaluation CASCADE CONSTRAINTS;
DROP TABLE salary CASCADE CONSTRAINTS;
DROP TABLE contract CASCADE CONSTRAINTS;
DROP TABLE participation_project CASCADE CONSTRAINTS;
DROP TABLE project CASCADE CONSTRAINTS;
DROP TABLE customer CASCADE CONSTRAINTS;
DROP TABLE employee CASCADE CONSTRAINTS;
DROP TABLE department CASCADE CONSTRAINTS;

DROP SEQUENCE employee_id_seq;
DROP SEQUENCE customer_id_seq;
DROP SEQUENCE project_id_seq;
DROP SEQUENCE contract_id_seq;
DROP SEQUENCE salary_id_seq;
DROP SEQUENCE peer_evaluation_id_seq;
DROP SEQUENCE pm_evaluation_id_seq;
DROP SEQUENCE customer_evaluation_id_seq;
DROP SEQUENCE seminar_id_seq;
