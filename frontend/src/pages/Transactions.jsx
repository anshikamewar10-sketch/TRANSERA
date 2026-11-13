
import { useEffect, useState } from "react";
import MainLayout from "../components/MainLayout";
import api from "../api";

import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Chip,
  Alert,
  Stack,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress
} from "@mui/material";

const panel = {
  background: "#102347",
  border: "1px solid #243A61",
  borderRadius: 3,
  p: 3,
  color: "#FFFFFF"
};

const muted = "#AFC1DB";

async function requestJSON(url, method = "GET") {
  const response = await fetch(url, { method });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : JSON.stringify(data.detail || data)
    );
  }

  return data;
}

function Transactions() {
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [logs, setLogs] = useState([]);
  const [summary, setSummary] = useState({
    total: 0,
    committed: 0,
    rolled_back: 0
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadHistory = async () => {
    setHistoryLoading(true);

    try {
      const data = await requestJSON(api.transactionHistory);

      setHistory(data.history || []);
      setLogs(data.logs || []);

      setSummary({
        total: data.total || 0,
        committed: data.committed || 0,
        rolled_back: data.rolled_back || 0
      });

    } catch (err) {
      setError(err.message);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const executeTransactions = async () => {
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const data = await requestJSON(
        api.executeTransactions,
        "POST"
      );

      setResult(data);
      setMessage(data.message);

      await loadHistory();

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const statusColor = (status) => {
    if (status === "COMMITTED") return "success";
    if (status === "ROLLED_BACK") return "error";
    if (status === "SKIPPED") return "warning";
    return "default";
  };

  const results = result?.results || [];

  return (
    <MainLayout>
      <Box sx={{ color: "white", pb: 5 }}>

        {/* HEADER */}

        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 2,
            mb: 3
          }}
        >
          <Box>
            <Typography variant="h4" fontWeight="bold">
              Transaction Center
            </Typography>

            <Typography color={muted} mt={1}>
              Oracle DBMS Transaction Management
            </Typography>

            <Typography
              variant="body2"
              color="#93C5FD"
              mt={1}
            >
              ACID Properties • COMMIT • ROLLBACK
            </Typography>
          </Box>

          <Button
            variant="contained"
            size="large"
            onClick={executeTransactions}
            disabled={loading}
            sx={{
              bgcolor: "#2563EB",
              px: 4,
              py: 1.5,
              fontWeight: "bold",
              borderRadius: 2,
              "&:hover": { bgcolor: "#1D4ED8" }
            }}
          >
            {loading
              ? "Executing..."
              : "Execute Transactions"}
          </Button>
        </Box>

        {loading && (
          <Box sx={{ mb: 3 }}>
            <CircularProgress size={22} />
            <Typography color={muted} ml={2} component="span">
              Processing Oracle transactions...
            </Typography>
          </Box>
        )}

        {message && (
          <Alert
            severity={result?.success ? "success" : "warning"}
            sx={{ mb: 3 }}
          >
            {message}
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* SUMMARY CARDS */}

        <Grid container spacing={3} sx={{ mb: 3 }}>
          {[
            {
              label: "Total Transactions",
              value: summary.total,
              color: "#60A5FA"
            },
            {
              label: "Committed",
              value: summary.committed,
              color: "#4ADE80"
            },
            {
              label: "Rolled Back",
              value: summary.rolled_back,
              color: "#FB7185"
            },
            {
              label: "Last Batch Processed",
              value: result?.total_processed || 0,
              color: "#FBBF24"
            }
          ].map((item) => (
            <Grid item xs={12} sm={6} md={3} key={item.label}>
              <Paper sx={panel}>
                <Typography variant="body2" color={muted}>
                  {item.label}
                </Typography>

                <Typography
                  variant="h3"
                  fontWeight="bold"
                  sx={{ mt: 1, color: item.color }}
                >
                  {item.value}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        {/* LATEST RESULTS */}

        <Paper sx={{ ...panel, mb: 3 }}>
          <Typography variant="h6" fontWeight="bold" mb={2}>
            Latest Transaction Results
          </Typography>

          {!result ? (
            <Typography color={muted}>
              Click Execute Transactions to process
              completed business operations.
            </Typography>
          ) : results.length === 0 ? (
            <Alert severity="info">
              No new eligible transactions found.
            </Alert>
          ) : (
            <Grid container spacing={2}>
              {results.map((item, index) => (
                <Grid
                  item
                  xs={12}
                  md={6}
                  lg={4}
                  key={`${item.operation_id}-${index}`}
                >
                  <Box
                    sx={{
                      p: 2.5,
                      height: "100%",
                      borderRadius: 2,
                      bgcolor: "#172E54",
                      border: "1px solid #30486D"
                    }}
                  >
                    <Stack
                      direction="row"
                      justifyContent="space-between"
                      alignItems="center"
                      mb={2}
                    >
                      <Typography fontWeight="bold">
                        {item.operation_id}
                      </Typography>

                      <Chip
                        label={item.status}
                        color={statusColor(item.status)}
                        size="small"
                      />
                    </Stack>

                    <Typography variant="body2" color={muted}>
                      {item.operation_type || "Transaction"}
                    </Typography>

                    {item.transaction_id && (
                      <Typography variant="caption" color={muted}>
                        ID: {item.transaction_id}
                      </Typography>
                    )}

                    {item.product_name && (
                      <Typography mt={2} fontWeight="medium">
                        {item.product_name}
                      </Typography>
                    )}

                    {item.before_quantity !== undefined && (
                      <Box
                        sx={{
                          bgcolor: "#102347",
                          borderRadius: 2,
                          p: 2,
                          mt: 2
                        }}
                      >
                        <Typography
                          variant="caption"
                          color={muted}
                        >
                          Inventory Quantity
                        </Typography>

                        <Typography
                          variant="h5"
                          fontWeight="bold"
                          color={
                            item.status === "COMMITTED"
                              ? "#4ADE80"
                              : "white"
                          }
                        >
                          {item.before_quantity}
                          {" → "}
                          {item.after_quantity}
                        </Typography>
                      </Box>
                    )}

                    <Typography
                      variant="body2"
                      color={muted}
                      mt={2}
                    >
                      {item.message}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          )}
        </Paper>

        {/* TRANSACTION HISTORY */}

        <Paper sx={{ ...panel, mb: 3 }}>
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="center"
            flexWrap="wrap"
            gap={2}
            mb={2}
          >
            <Typography variant="h6" fontWeight="bold">
              Transaction History
            </Typography>

            <Button
              variant="outlined"
              onClick={loadHistory}
              disabled={historyLoading}
              sx={{
                color: "#93C5FD",
                borderColor: "#3B5B85"
              }}
            >
              Refresh History
            </Button>
          </Stack>

          <Divider sx={{ borderColor: "#30486D", mb: 2 }} />

          {history.length === 0 ? (
            <Typography color={muted}>
              No transactions recorded in Oracle yet.
            </Typography>
          ) : (
            <TableContainer sx={{ maxHeight: 400 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    {[
                      "Transaction",
                      "Operation",
                      "Process",
                      "Type",
                      "Status",
                      "Time"
                    ].map((heading) => (
                      <TableCell
                        key={heading}
                        sx={{
                          bgcolor: "#172E54",
                          color: "white",
                          fontWeight: "bold"
                        }}
                      >
                        {heading}
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>

                <TableBody>
                  {history.map((item) => (
                    <TableRow key={item.transaction_id}>
                      <TableCell sx={{ color: "white" }}>
                        {item.transaction_id}
                      </TableCell>

                      <TableCell sx={{ color: muted }}>
                        {item.operation_id}
                      </TableCell>

                      <TableCell sx={{ color: muted }}>
                        {item.process_id}
                      </TableCell>

                      <TableCell sx={{ color: muted }}>
                        {item.operation_type}
                      </TableCell>

                      <TableCell>
                        <Chip
                          size="small"
                          label={item.status}
                          color={statusColor(item.status)}
                        />
                      </TableCell>

                      <TableCell sx={{ color: muted }}>
                        {item.end_time
                          ? new Date(item.end_time).toLocaleString()
                          : "—"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>

        {/* TRANSACTION LOGS */}

        <Paper sx={panel}>
          <Typography variant="h6" fontWeight="bold" mb={2}>
            Database Transaction Logs
          </Typography>

          {logs.length === 0 ? (
            <Typography color={muted}>
              No transaction log entries found.
            </Typography>
          ) : (
            <Stack spacing={1.5}>
              {logs.slice(0, 20).map((log) => (
                <Box
                  key={log.log_id}
                  sx={{
                    p: 2,
                    bgcolor: "#172E54",
                    borderRadius: 2,
                    border: "1px solid #30486D"
                  }}
                >
                  <Stack
                    direction="row"
                    justifyContent="space-between"
                    alignItems="center"
                    gap={2}
                  >
                    <Box>
                      <Typography fontWeight="bold">
                        {log.transaction_id}
                      </Typography>

                      <Typography
                        variant="body2"
                        color={muted}
                        mt={0.5}
                      >
                        {log.description}
                      </Typography>
                    </Box>

                    <Chip
                      size="small"
                      label={log.event_type}
                      color={
                        log.event_type === "COMMIT"
                          ? "success"
                          : "error"
                      }
                    />
                  </Stack>
                </Box>
              ))}
            </Stack>
          )}
        </Paper>

      </Box>
    </MainLayout>
  );
}

export default Transactions;
