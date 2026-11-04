-- =============================================================================
-- ResumeIQ DBMS Demonstration 06: RBAC & Row-Level Security (RLS)
-- Academic Demonstration Script for Viva Defense
-- =============================================================================

\echo '----------------------------------------------------------------------'
\echo 'DEMO 6.1: Role-Based Access Control (RBAC) Catalog Inspection'
\echo '----------------------------------------------------------------------'

SELECT 
    rolname AS role_name,
    rolsuper AS is_superuser,
    rolcreaterole AS can_create_roles,
    rolcreatedb AS can_create_db,
    rolcanlogin AS can_login
FROM pg_roles
WHERE rolname IN ('resumeiq_app', 'resumeiq_analyst', 'resumeiq_auditor', 'apple')
ORDER BY rolname;

\echo ''
\echo '----------------------------------------------------------------------'
\echo 'DEMO 6.2: Table-level Privilege Grants for Application Roles'
\echo '----------------------------------------------------------------------'

SELECT 
    grantee, 
    table_name, 
    privilege_type
FROM information_schema.table_privileges
WHERE grantee IN ('resumeiq_app', 'resumeiq_analyst', 'resumeiq_auditor')
  AND table_schema = 'public'
ORDER BY grantee, table_name, privilege_type
LIMIT 15;

\echo ''
\echo '----------------------------------------------------------------------'
\echo 'DEMO 6.3: Row-Level Security (RLS) Policy Verification'
\echo '----------------------------------------------------------------------'

SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

\echo ''
\echo '----------------------------------------------------------------------'
\echo 'DEMO 6.4: RLS Simulation - Testing Visibility Under Restricted Role'
\echo '----------------------------------------------------------------------'

-- Show jobs visible to superuser/admin
SELECT COUNT(*) AS all_jobs_count FROM jobs;

-- Demonstrate RLS behavior
-- When connected as an analyst role that is only permitted active jobs
SET ROLE resumeiq_analyst;
SELECT COUNT(*) AS active_jobs_only FROM jobs;
RESET ROLE;
