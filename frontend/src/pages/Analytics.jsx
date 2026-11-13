
import { useEffect, useState } from "react";
import MainLayout from "../components/MainLayout";
import api from "../api";

import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  Alert,
  Stack,
  LinearProgress,
  CircularProgress,
  Divider
} from "@mui/material";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend
} from "recharts";

const C = {
  panel: "#102347",
  inner: "#172E54",
  border: "#29436C",
  muted: "#B3C4DD",
  blue: "#60A5FA",
  green: "#4ADE80",
  yellow: "#FBBF24",
  red: "#FB7185",
  purple: "#A78BFA",
  cyan: "#22D3EE"
};

const chartColors = [
  C.blue,
  C.green,
  C.yellow,
  C.red,
  C.purple,
  C.cyan
];

const panel = {
  background: C.panel,
  border: `1px solid ${C.border}`,
  borderRadius: "20px",
  p: { xs: 2, md: 3 },
  color: "#FFFFFF",
  minWidth: 0,
  width: "100%",
  boxSizing: "border-box"
};

const inner = {
  background: C.inner,
  border: `1px solid ${C.border}`,
  borderRadius: 2,
  p: 2,
  minWidth: 0
};

const num = (value) => Number(value ?? 0);
const pct = (value) => `${num(value).toFixed(1)}%`;
const clamp = (value) =>
  Math.min(100, Math.max(0, num(value)));

const grid = (columns) => ({
  display: "grid",
  gridTemplateColumns: columns,
  gap: 2.5,
  width: "100%",
  minWidth: 0
});

function SectionTitle({ children, subtitle }) {
  return (
    <Box sx={{ mb: 2.5 }}>
      <Typography
        variant="h5"
        fontWeight={800}
        sx={{ fontSize: { xs: 20, md: 24 } }}
      >
        {children}
      </Typography>

      {subtitle && (
        <Typography
          color={C.muted}
          variant="body2"
          sx={{ mt: 0.5 }}
        >
          {subtitle}
        </Typography>
      )}
    </Box>
  );
}

function MetricCard({ label, value, detail, color }) {
  return (
    <Paper
      elevation={0}
      sx={{
        ...panel,
        minHeight: 145,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center"
      }}
    >
      <Typography
        color={C.muted}
        variant="body2"
        fontWeight={600}
      >
        {label}
      </Typography>

      <Typography
        sx={{
          color: color || C.blue,
          fontWeight: 800,
          fontSize: { xs: 30, md: 38 },
          lineHeight: 1.35,
          mt: 1
        }}
      >
        {value}
      </Typography>

      {detail && (
        <Typography color={C.muted} variant="caption">
          {detail}
        </Typography>
      )}
    </Paper>
  );
}

function ProgressItem({
  label,
  value,
  detail,
  color = C.blue
}) {
  return (
    <Box sx={{ mb: 2.5 }}>
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        gap={1}
        mb={1}
      >
        <Typography fontWeight={600} variant="body2">
          {label}
        </Typography>

        <Typography
          variant="body2"
          fontWeight={700}
          sx={{ color }}
        >
          {pct(value)}
        </Typography>
      </Stack>

      <LinearProgress
        variant="determinate"
        value={clamp(value)}
        sx={{
          height: 10,
          borderRadius: 10,
          backgroundColor: "#2B4165",
          "& .MuiLinearProgress-bar": {
            backgroundColor: color,
            borderRadius: 10
          }
        }}
      />

      {detail && (
        <Typography
          color={C.muted}
          variant="caption"
          display="block"
          mt={0.7}
        >
          {detail}
        </Typography>
      )}
    </Box>
  );
}

function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAnalytics = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(api.analyticsDashboard);
      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(
          typeof result.detail === "string"
            ? result.detail
            : result.message || "Analytics request failed."
        );
      }

      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  const operations = data?.operations || {};
  const processes = data?.processes || {};
  const transactions = data?.transactions || {};
  const integrity = data?.integrity || {};

  const processStates = (data?.process_states || []).map(
    (item) => ({
      status: item.status,
      total: num(item.total)
    })
  );

  const transactionStates = (
    data?.transaction_states || []
  ).map((item) => ({
    name: item.status,
    value: num(item.total)
  }));

  const departments = data?.departments || [];
  const resources = data?.resources || [];
  const rankings = data?.resource_ranking || [];
  const insights = data?.insights || [];
  const failures = data?.failure_reasons || [];

  const integrityChecks = [
    {
      label: "Resource Accounting",
      description: "Total = Available + Active Allocations",
      errors: num(integrity.resource_errors)
    },
    {
      label: "Inventory Validity",
      description: "No negative inventory quantities",
      errors: num(integrity.negative_inventory)
    },
    {
      label: "Process–Operation Consistency",
      description: "Terminated processes match completed operations",
      errors: num(integrity.process_operation_errors)
    },
    {
      label: "Transaction Link Consistency",
      description: "Transactions reference matching processes and operations",
      errors: num(integrity.transaction_link_errors)
    }
  ];

  const integrityPassed = integrityChecks.every(
    (check) => check.errors === 0
  );

  const hasResourceHistory = rankings.some(
    (item) => num(item.historical_units) > 0
  );

  const totalTransactionChartValues = transactionStates.reduce(
    (sum, item) => sum + item.value,
    0
  );

  return (
    <MainLayout>
      <Box
        sx={{
          color: "white",
          width: "100%",
          maxWidth: "100%",
          minWidth: 0,
          boxSizing: "border-box",
          pb: 6
        }}
      >
        {/* HEADER */}

        <Stack
          direction={{ xs: "column", md: "row" }}
          justifyContent="space-between"
          alignItems={{ xs: "stretch", md: "center" }}
          gap={2}
          sx={{ mb: 4 }}
        >
          <Box>
            <Typography
              variant="h4"
              fontWeight={800}
              sx={{ fontSize: { xs: 27, md: 34 } }}
            >
              Analytics & Insights
            </Typography>

            <Typography color={C.muted} mt={0.5}>
              Oracle-powered Business & System Performance
            </Typography>

            <Typography
              variant="body2"
              color={C.blue}
              mt={1}
            >
              SQL Aggregations • Resource Efficiency • Data Integrity
            </Typography>
          </Box>

          <Button
            variant="contained"
            onClick={loadAnalytics}
            disabled={loading}
            sx={{
              bgcolor: "#F7C948",
              color: "#101010",
              fontWeight: 800,
              px: 3,
              py: 1.5,
              borderRadius: 2,
              alignSelf: { md: "center" },
              "&:hover": { bgcolor: "#E8B92F" }
            }}
          >
            Refresh Analytics
          </Button>
        </Stack>

        {loading && (
          <Box sx={{ mb: 3 }}>
            <LinearProgress sx={{ mb: 2 }} />
            <Typography color={C.muted}>
              Reading live Oracle analytics...
            </Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {!data ? (
          !loading && (
            <Alert severity="info">
              Analytics data is not available.
            </Alert>
          )
        ) : (
          <Stack spacing={5}>

            {/* PERFORMANCE OVERVIEW */}

            <Box>
              <SectionTitle
                subtitle="Current performance calculated directly from Oracle"
              >
                Performance Overview
              </SectionTitle>

              <Box
                sx={grid({
                  xs: "repeat(1, minmax(0, 1fr))",
                  sm: "repeat(2, minmax(0, 1fr))",
                  lg: "repeat(4, minmax(0, 1fr))"
                })}
              >
                <MetricCard
                  label="Operation Completion"
                  value={pct(operations.completion_percent)}
                  detail={`${num(operations.completed_operations)} of ${num(operations.total_operations)} operations`}
                  color={C.green}
                />

                <MetricCard
                  label="Process Completion"
                  value={pct(processes.completion_percent)}
                  detail={`${num(processes.terminated_processes)} of ${num(processes.total_processes)} processes`}
                  color={C.blue}
                />

                <MetricCard
                  label="Transaction Success"
                  value={pct(transactions.success_percent)}
                  detail={`${num(transactions.committed_transactions)} committed transactions`}
                  color={C.purple}
                />

                <MetricCard
                  label="Database Integrity"
                  value={integrityPassed ? "PASS" : "WARNING"}
                  detail={`${integrityChecks.filter(c => c.errors > 0).length} failed checks`}
                  color={integrityPassed ? C.green : C.red}
                />
              </Box>
            </Box>

            {/* PROCESS EFFICIENCY */}

            <Box>
              <SectionTitle
                subtitle="Live process states and completion progress"
              >
                Operations & Process Efficiency
              </SectionTitle>

              <Box
                sx={grid({
                  xs: "minmax(0, 1fr)",
                  md: "minmax(0, 1.5fr) minmax(0, 1fr)"
                })}
              >
                <Paper sx={panel}>
                  <Typography variant="h6" fontWeight={700} mb={2}>
                    Process State Distribution
                  </Typography>

                  {processStates.length === 0 ? (
                    <Box
                      sx={{
                        minHeight: 280,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center"
                      }}
                    >
                      <Typography color={C.muted}>
                        No processes generated yet.
                      </Typography>
                    </Box>
                  ) : (
                    <Box sx={{ width: "100%", height: 310 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={processStates}
                          margin={{
                            top: 15,
                            right: 15,
                            left: -15,
                            bottom: 45
                          }}
                        >
                          <CartesianGrid
                            stroke="#30486D"
                            strokeDasharray="3 3"
                          />

                          <XAxis
                            dataKey="status"
                            stroke={C.muted}
                            angle={-20}
                            textAnchor="end"
                            interval={0}
                            tick={{ fontSize: 11 }}
                          />

                          <YAxis
                            stroke={C.muted}
                            allowDecimals={false}
                          />

                          <Tooltip
                            contentStyle={{
                              background: C.inner,
                              border: `1px solid ${C.border}`,
                              color: "white"
                            }}
                          />

                          <Bar
                            dataKey="total"
                            name="Processes"
                            radius={[7, 7, 0, 0]}
                          >
                            {processStates.map((item, index) => (
                              <Cell
                                key={item.status}
                                fill={chartColors[index % chartColors.length]}
                              />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </Box>
                  )}
                </Paper>

                <Paper sx={panel}>
                  <Typography variant="h6" fontWeight={700} mb={3}>
                    Completion Progress
                  </Typography>

                  <ProgressItem
                    label="Business Operations"
                    value={operations.completion_percent}
                    color={C.green}
                    detail={`${num(operations.completed_operations)} of ${num(operations.total_operations)} completed`}
                  />

                  <ProgressItem
                    label="OS Processes"
                    value={processes.completion_percent}
                    color={C.blue}
                    detail={`${num(processes.terminated_processes)} of ${num(processes.total_processes)} terminated`}
                  />

                  <Divider
                    sx={{
                      borderColor: C.border,
                      my: 3
                    }}
                  />

                  <Box
                    sx={grid("repeat(2, minmax(0, 1fr))")}
                  >
                    <Box sx={inner}>
                      <Typography color={C.muted} variant="caption">
                        Waiting
                      </Typography>
                      <Typography
                        variant="h4"
                        fontWeight={800}
                        color={C.yellow}
                      >
                        {num(processes.waiting_processes)}
                      </Typography>
                    </Box>

                    <Box sx={inner}>
                      <Typography color={C.muted} variant="caption">
                        Allocated
                      </Typography>
                      <Typography
                        variant="h4"
                        fontWeight={800}
                        color={C.blue}
                      >
                        {num(processes.allocated_processes)}
                      </Typography>
                    </Box>
                  </Box>
                </Paper>
              </Box>
            </Box>

            {/* DEPARTMENTS */}

            <Paper sx={panel}>
              <Typography variant="h6" fontWeight={700} mb={1}>
                Department-wise Operation Performance
              </Typography>

              <Typography color={C.muted} variant="body2" mb={3}>
                Completion rate for each department
              </Typography>

              {departments.length === 0 ? (
                <Typography color={C.muted}>
                  No department data available.
                </Typography>
              ) : (
                <Box
                  sx={grid({
                    xs: "minmax(0, 1fr)",
                    sm: "repeat(2, minmax(0, 1fr))",
                    lg: "repeat(3, minmax(0, 1fr))"
                  })}
                >
                  {departments.map((item) => (
                    <Box key={item.department} sx={inner}>
                      <ProgressItem
                        label={item.department}
                        value={item.completion_percent}
                        color={C.green}
                        detail={`${item.completed_operations} / ${item.total_operations} operations completed`}
                      />
                    </Box>
                  ))}
                </Box>
              )}
            </Paper>

            {/* RESOURCE UTILIZATION */}

            <Box>
              <SectionTitle
                subtitle="Current capacity and historical resource demand"
              >
                Resource Utilization & Bottlenecks
              </SectionTitle>

              <Box
                sx={grid({
                  xs: "minmax(0, 1fr)",
                  md: "minmax(0, 1.4fr) minmax(0, 1fr)"
                })}
              >
                <Paper sx={panel}>
                  <Typography variant="h6" fontWeight={700} mb={3}>
                    Current Resource Utilization
                  </Typography>

                  <Stack spacing={2.5}>
                    {resources.map((resource) => {
                      const usage = num(resource.utilization_percent);
                      const bottleneck =
                        num(resource.available_units) === 0 &&
                        num(resource.waiting_processes) > 0;

                      return (
                        <Box key={resource.resource_id}>
                          <ProgressItem
                            label={resource.resource_name}
                            value={usage}
                            color={
                              bottleneck
                                ? C.red
                                : usage >= 75
                                  ? C.yellow
                                  : C.blue
                            }
                            detail={`${resource.used_units} / ${resource.total_units} instances used`}
                          />

                          {bottleneck && (
                            <Chip
                              label={`${resource.waiting_processes} waiting process(es)`}
                              color="warning"
                              size="small"
                            />
                          )}
                        </Box>
                      );
                    })}
                  </Stack>
                </Paper>

                <Paper sx={panel}>
                  <Typography variant="h6" fontWeight={700} mb={1}>
                    Most Used Resources
                  </Typography>

                  <Typography
                    color={C.muted}
                    variant="body2"
                    mb={3}
                  >
                    Ranked by historical allocated instances
                  </Typography>

                  {!hasResourceHistory ? (
                    <Alert severity="info">
                      No allocation history yet. Rankings will appear
                      after resources are allocated.
                    </Alert>
                  ) : (
                    <Stack spacing={1.5}>
                      {rankings
                        .filter((item) => num(item.historical_units) > 0)
                        .map((item) => (
                          <Box
                            key={item.resource_name}
                            sx={inner}
                          >
                            <Stack
                              direction="row"
                              justifyContent="space-between"
                              alignItems="center"
                              gap={1}
                            >
                              <Box sx={{ minWidth: 0 }}>
                                <Typography fontWeight={700}>
                                  #{item.usage_rank}{" "}
                                  {item.resource_name}
                                </Typography>

                                <Typography
                                  color={C.muted}
                                  variant="caption"
                                >
                                  Outstanding requests:{" "}
                                  {item.requested_units} units
                                </Typography>
                              </Box>

                              <Chip
                                size="small"
                                label={`${item.historical_units} units`}
                                sx={{
                                  bgcolor: C.yellow,
                                  color: "#101010",
                                  fontWeight: 700
                                }}
                              />
                            </Stack>
                          </Box>
                        ))}
                    </Stack>
                  )}
                </Paper>
              </Box>
            </Box>

            {/* TRANSACTION RELIABILITY */}

            <Box>
              <SectionTitle
                subtitle="Oracle COMMIT and ROLLBACK outcomes"
              >
                Transaction Reliability
              </SectionTitle>

              <Box
                sx={grid({
                  xs: "minmax(0, 1fr)",
                  md: "minmax(0, 1.2fr) minmax(0, 1fr)"
                })}
              >
                <Paper sx={panel}>
                  <Typography variant="h6" fontWeight={700} mb={2}>
                    Transaction Outcomes
                  </Typography>

                  {totalTransactionChartValues === 0 ? (
                    <Box
                      sx={{
                        minHeight: 280,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center"
                      }}
                    >
                      <Typography color={C.muted}>
                        No transactions have been executed yet.
                      </Typography>
                    </Box>
                  ) : (
                    <Box sx={{ width: "100%", height: 300 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={transactionStates}
                            dataKey="value"
                            nameKey="name"
                            innerRadius={65}
                            outerRadius={105}
                            paddingAngle={3}
                          >
                            {transactionStates.map((item, index) => (
                              <Cell
                                key={item.name}
                                fill={
                                  item.name === "COMMITTED"
                                    ? C.green
                                    : item.name === "ROLLED_BACK"
                                      ? C.red
                                      : chartColors[index % chartColors.length]
                                }
                              />
                            ))}
                          </Pie>

                          <Tooltip
                            contentStyle={{
                              background: C.inner,
                              border: `1px solid ${C.border}`,
                              color: "white"
                            }}
                          />

                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </Box>
                  )}
                </Paper>

                <Paper sx={panel}>
                  <Typography variant="h6" fontWeight={700} mb={3}>
                    Transaction Summary
                  </Typography>

                  <Box
                    sx={grid("repeat(2, minmax(0, 1fr))")}
                  >
                    <Box sx={inner}>
                      <Typography color={C.muted} variant="caption">
                        Total
                      </Typography>
                      <Typography variant="h4" color={C.blue}>
                        {num(transactions.total_transactions)}
                      </Typography>
                    </Box>

                    <Box sx={inner}>
                      <Typography color={C.muted} variant="caption">
                        Success Rate
                      </Typography>
                      <Typography variant="h4" color={C.purple}>
                        {pct(transactions.success_percent)}
                      </Typography>
                    </Box>

                    <Box sx={inner}>
                      <Typography color={C.muted} variant="caption">
                        Committed
                      </Typography>
                      <Typography variant="h4" color={C.green}>
                        {num(transactions.committed_transactions)}
                      </Typography>
                    </Box>

                    <Box sx={inner}>
                      <Typography color={C.muted} variant="caption">
                        Rolled Back
                      </Typography>
                      <Typography variant="h4" color={C.red}>
                        {num(transactions.rolled_back_transactions)}
                      </Typography>
                    </Box>
                  </Box>
                </Paper>
              </Box>
            </Box>

            {/* FAILURE REASONS */}

            <Paper sx={panel}>
              <Typography variant="h6" fontWeight={700} mb={2}>
                Transaction Failure Reasons
              </Typography>

              {failures.length === 0 ? (
                <Alert severity="info">
                  No rollback reasons recorded.
                </Alert>
              ) : (
                <Stack spacing={1.5}>
                  {failures.map((item, index) => (
                    <Box key={index} sx={inner}>
                      <Stack
                        direction="row"
                        justifyContent="space-between"
                        alignItems="center"
                        gap={2}
                      >
                        <Typography color={C.muted}>
                          {item.reason}
                        </Typography>

                        <Chip
                          label={`${item.total} occurrence(s)`}
                          color="error"
                          size="small"
                        />
                      </Stack>
                    </Box>
                  ))}
                </Stack>
              )}
            </Paper>

            {/* INTEGRITY AND ACTIVITY */}

            <Box>
              <SectionTitle
                subtitle="Oracle consistency validation and recorded activity"
              >
                Database Integrity & System Insights
              </SectionTitle>

              <Box
                sx={grid({
                  xs: "minmax(0, 1fr)",
                  md: "minmax(0, 1.2fr) minmax(0, 1fr)"
                })}
              >
                <Paper sx={panel}>
                  <Typography variant="h6" fontWeight={700} mb={3}>
                    Oracle Integrity Checks
                  </Typography>

                  <Stack spacing={1.5}>
                    {integrityChecks.map((check) => (
                      <Box key={check.label} sx={inner}>
                        <Stack
                          direction="row"
                          justifyContent="space-between"
                          alignItems="center"
                          gap={2}
                        >
                          <Box sx={{ minWidth: 0 }}>
                            <Typography fontWeight={700}>
                              {check.label}
                            </Typography>

                            <Typography
                              variant="caption"
                              color={C.muted}
                            >
                              {check.description}
                            </Typography>
                          </Box>

                          <Chip
                            size="small"
                            label={
                              check.errors === 0
                                ? "PASS"
                                : `${check.errors} ERROR(S)`
                            }
                            color={
                              check.errors === 0
                                ? "success"
                                : "error"
                            }
                          />
                        </Stack>
                      </Box>
                    ))}
                  </Stack>
                </Paper>

                <Paper sx={panel}>
                  <Typography variant="h6" fontWeight={700} mb={3}>
                    System Activity
                  </Typography>

                  <Box
                    sx={grid("repeat(2, minmax(0, 1fr))")}
                  >
                    <Box sx={inner}>
                      <Typography color={C.muted} variant="body2">
                        Deadlock Recoveries
                      </Typography>

                      <Typography
                        variant="h3"
                        fontWeight={800}
                        color={C.yellow}
                        mt={1}
                      >
                        {num(data.recovery?.recovery_count)}
                      </Typography>
                    </Box>

                    <Box sx={inner}>
                      <Typography color={C.muted} variant="body2">
                        System Log Entries
                      </Typography>

                      <Typography
                        variant="h3"
                        fontWeight={800}
                        color={C.blue}
                        mt={1}
                      >
                        {num(data.system_logs?.log_count)}
                      </Typography>
                    </Box>
                  </Box>

                  <Typography
                    color={C.muted}
                    variant="body2"
                    mt={3}
                  >
                    Counts reflect records currently stored in Oracle.
                    Resetting the demo database clears historical activity.
                  </Typography>
                </Paper>
              </Box>
            </Box>

            {/* SQL INSIGHTS */}

            <Paper sx={panel}>
              <Typography variant="h6" fontWeight={700} mb={1}>
                SQL-Generated System Insights
              </Typography>

              <Typography color={C.muted} variant="body2" mb={3}>
                Observations derived directly from Oracle SQL views
              </Typography>

              <Box
                sx={grid({
                  xs: "minmax(0, 1fr)",
                  sm: "repeat(2, minmax(0, 1fr))"
                })}
              >
                {insights.map((item, index) => (
                  <Box key={index} sx={inner}>
                    <Chip
                      size="small"
                      label={item.category}
                      sx={{
                        bgcolor: C.yellow,
                        color: "#101010",
                        fontWeight: 800,
                        mb: 1.5
                      }}
                    />

                    <Typography color={C.muted}>
                      {item.insight}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Paper>

          </Stack>
        )}
      </Box>
    </MainLayout>
  );
}

export default Analytics;
