import { useLabStatus } from '../hooks/useLabStatus.js';
import LabStatusBanner from '../components/lab/LabStatusBanner.jsx';
import ExperimentCard from '../components/lab/ExperimentCard.jsx';

export default function ExperimentsPage() {
  const { labStatus, loading, error } = useLabStatus();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-100">Security Experiments</h1>
        <p className="text-sm text-gray-400 mt-1">
          Execute controlled security tests and evaluate defensive mechanisms across the 4 primary scenarios.
        </p>
      </div>

      <LabStatusBanner labStatus={labStatus} loading={loading} error={error} />

      <div className="space-y-6">
        {/* Scenario 1: SQL Injection */}
        <ExperimentCard
          id="sqli"
          title="Scenario 1: SQL Injection"
          cwe="CWE-89"
          objective="Determine whether unsafe SQL query construction allows manipulation of backend queries to bypass authentication or extract unauthorized records."
          description="Variant A executes string concatenation inside the SQL statement. Variant B enforces parameterized queries with bound variables."
          defaultPayload="' OR '1'='1"
          supportsVariants={['A', 'B']}
        />

        {/* Scenario 2: Excessive Database Privileges */}
        <ExperimentCard
          id="privileges"
          title="Scenario 2: Excessive Database Privileges"
          cwe="CWE-250"
          objective="Evaluate whether an overprivileged application identity can perform unauthorized operations (e.g. inspecting system catalogs or database roles) compared to least-privilege roles."
          description="Variant A runs under the overprivileged app_vulnerable role. Variant B uses app_readonly / app_writer with least-privilege permissions."
          defaultPayload="SELECT rolname, rolsuper, rolinherit FROM pg_roles LIMIT 5"
          supportsVariants={['A', 'B']}
        />

        {/* Scenario 3: Broken Authorization / BOLA */}
        <ExperimentCard
          id="bola"
          title="Scenario 3: Broken Object-Level Authorization (BOLA/IDOR)"
          cwe="CWE-284"
          objective="Determine whether one customer can access another customer's financial accounts. Compare application-level validation vs PostgreSQL Row-Level Security (RLS)."
          description="Variant A omits ownership validation. Variant B enforces application-layer ownership checks. Variant C tests PostgreSQL Row-Level Security."
          defaultPayload=""
          supportsVariants={['A', 'B', 'C']}
        />

        {/* Scenario 4: Database Network Exposure */}
        <ExperimentCard
          id="network"
          title="Scenario 4: Database Network Exposure"
          cwe="CWE-668"
          objective="Verify that PostgreSQL listens exclusively on the isolated internal DB-NET interface and rejects unauthorized network traffic from external or audit segments."
          description="Variant A tests the secured isolated DB-NET configuration. Variant B tests exposure to unauthorized subnets."
          defaultPayload=""
          supportsVariants={['A', 'B']}
        />
      </div>
    </div>
  );
}

