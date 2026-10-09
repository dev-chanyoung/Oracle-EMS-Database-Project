-- 04_truncate_data.sql
-- 테이블 구조는 그대로 두고 데이터만 모두 비운다. 시드 데이터를 다시 적재하기 전에 사용한다.
--
-- TRUNCATE는 다른 테이블이 (활성화된) FK로 참조하는 테이블에는 쓸 수 없다 (ORA-02266).
-- 그래서 1) 모든 FK 비활성화 -> 2) 전체 TRUNCATE -> 3) FK 다시 활성화 순서로 실행한다.
-- 중간에 실패하면 FK가 비활성화된 채 남을 수 있으므로, 3) 구간만 다시 실행한다.
--
-- 시퀀스는 되돌리지 않고, Materialized View(employee_search_mv)는 건드리지 않는다.
-- 다시 적재한 뒤에는 시드의 평문을 전환해야 하므로 src/migrate_sensitive_data.py 를 다시 실행한다.

-- 1) FK 비활성화 (20개)
ALTER TABLE employee DISABLE CONSTRAINT FK_Department_TO_Employee_1;
ALTER TABLE project DISABLE CONSTRAINT FK_Customer_TO_Project_1;
ALTER TABLE participation_project DISABLE CONSTRAINT FK_Employee_TO_ParticipationProject_1;
ALTER TABLE participation_project DISABLE CONSTRAINT FK_Project_TO_ParticipationProject_1;
ALTER TABLE contract DISABLE CONSTRAINT FK_Employee_TO_Contract_1;
ALTER TABLE salary DISABLE CONSTRAINT FK_Employee_TO_Salary_1;
ALTER TABLE salary DISABLE CONSTRAINT FK_Contract_TO_Salary_1;
ALTER TABLE peer_evaluation DISABLE CONSTRAINT FK_Project_TO_PeerEvaluation_1;
ALTER TABLE peer_evaluation DISABLE CONSTRAINT FK_Employee_TO_PeerEvaluation_1;
ALTER TABLE peer_evaluation DISABLE CONSTRAINT FK_Employee_TO_PeerEvaluation_2;
ALTER TABLE pm_evaluation DISABLE CONSTRAINT FK_Project_TO_PMEvaluation_1;
ALTER TABLE pm_evaluation DISABLE CONSTRAINT FK_Employee_TO_PMEvaluation_1;
ALTER TABLE pm_evaluation DISABLE CONSTRAINT FK_Employee_TO_PMEvaluation_2;
ALTER TABLE customer_evaluation DISABLE CONSTRAINT FK_Project_TO_CustomerEvaluation_1;
ALTER TABLE customer_evaluation DISABLE CONSTRAINT FK_Customer_TO_CustomerEvaluation_1;
ALTER TABLE customer_evaluation DISABLE CONSTRAINT FK_Employee_TO_CustomerEvaluation_1;
ALTER TABLE incentive DISABLE CONSTRAINT FK_Project_TO_Incentive_1;
ALTER TABLE incentive DISABLE CONSTRAINT FK_Employee_TO_Incentive_1;
ALTER TABLE seminar_participation DISABLE CONSTRAINT FK_Seminar_TO_SeminarParticipation_1;
ALTER TABLE seminar_participation DISABLE CONSTRAINT FK_Employee_TO_SeminarParticipation_1;

-- 2) 데이터 삭제 (13개 테이블)
TRUNCATE TABLE seminar_participation;
TRUNCATE TABLE seminar;
TRUNCATE TABLE incentive;
TRUNCATE TABLE customer_evaluation;
TRUNCATE TABLE pm_evaluation;
TRUNCATE TABLE peer_evaluation;
TRUNCATE TABLE salary;
TRUNCATE TABLE contract;
TRUNCATE TABLE participation_project;
TRUNCATE TABLE project;
TRUNCATE TABLE customer;
TRUNCATE TABLE employee;
TRUNCATE TABLE department;

-- 3) FK 활성화 (20개)
ALTER TABLE employee ENABLE CONSTRAINT FK_Department_TO_Employee_1;
ALTER TABLE project ENABLE CONSTRAINT FK_Customer_TO_Project_1;
ALTER TABLE participation_project ENABLE CONSTRAINT FK_Employee_TO_ParticipationProject_1;
ALTER TABLE participation_project ENABLE CONSTRAINT FK_Project_TO_ParticipationProject_1;
ALTER TABLE contract ENABLE CONSTRAINT FK_Employee_TO_Contract_1;
ALTER TABLE salary ENABLE CONSTRAINT FK_Employee_TO_Salary_1;
ALTER TABLE salary ENABLE CONSTRAINT FK_Contract_TO_Salary_1;
ALTER TABLE peer_evaluation ENABLE CONSTRAINT FK_Project_TO_PeerEvaluation_1;
ALTER TABLE peer_evaluation ENABLE CONSTRAINT FK_Employee_TO_PeerEvaluation_1;
ALTER TABLE peer_evaluation ENABLE CONSTRAINT FK_Employee_TO_PeerEvaluation_2;
ALTER TABLE pm_evaluation ENABLE CONSTRAINT FK_Project_TO_PMEvaluation_1;
ALTER TABLE pm_evaluation ENABLE CONSTRAINT FK_Employee_TO_PMEvaluation_1;
ALTER TABLE pm_evaluation ENABLE CONSTRAINT FK_Employee_TO_PMEvaluation_2;
ALTER TABLE customer_evaluation ENABLE CONSTRAINT FK_Project_TO_CustomerEvaluation_1;
ALTER TABLE customer_evaluation ENABLE CONSTRAINT FK_Customer_TO_CustomerEvaluation_1;
ALTER TABLE customer_evaluation ENABLE CONSTRAINT FK_Employee_TO_CustomerEvaluation_1;
ALTER TABLE incentive ENABLE CONSTRAINT FK_Project_TO_Incentive_1;
ALTER TABLE incentive ENABLE CONSTRAINT FK_Employee_TO_Incentive_1;
ALTER TABLE seminar_participation ENABLE CONSTRAINT FK_Seminar_TO_SeminarParticipation_1;
ALTER TABLE seminar_participation ENABLE CONSTRAINT FK_Employee_TO_SeminarParticipation_1;
