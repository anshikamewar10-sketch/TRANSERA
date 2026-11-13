
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
  CircularProgress,
  LinearProgress,
  Stack,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
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

function ResourceCenter() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadHistory = async () => {
    try {
      const data = await requestJSON(api.resourceHistory);
      setHistory(data.history || []);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const allocateResources = async () => {
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const data = await requestJSON(
        api.allocateResources,
        "POST"
      );

      setResult(data);

      if (!data.success && !data.results) {
        setMessage(
          data.message ||
          "No processes awaiting resource allocation."
        );
      } else {
        setMessage(
          data.message ||
          "Resource allocation processing completed."
        );
      }

      await loadHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const results = result?.results || [];

  const allocated = results.filter(
    (p) => p.status === "ALLOCATED"
  );

  const waiting = results.filter(
    (p) => p.status === "WAITING"
  );

  const errors = results.filter(
    (p) => p.status === "ERROR"
  );

  const total = result?.total_processed || 0;

  const getChipColor = (status) => {
    if (status === "ALLOCATED") return "success";
    if (status === "WAITING") return "warning";
    if (status === "ERROR") return "error";
    return "default";
  };

  const formatResources = (items, waitingMode = false) => {
    if (!items?.length) return "None";

    return items.map((item, index) => (
      <Box key={index} sx={{ mb: 0.7 }}>
        <Typography variant="body2" color={muted}>
          {item.resource_name}
          {" × "}
          {waitingMode
            ? item.units_needed
            : item.units}
          {waitingMode &&
            item.available_units !== undefined &&
            ` (Available: ${item.available_units})`}
        </Typography>
      </Box>
    ));
  };

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
              Resource Allocation Center
            </Typography>

            <Typography color={muted} sx={{ mt: 1 }}>
              Multiple-instance resource management
              integrated with Oracle and Banker's Algorithm
            </Typography>
          </Box>

          <Button
            variant="contained"
            size="large"
            onClick={allocateResources}
            disabled={loading}
            sx={{
              bgcolor: "#2563EB",
              px: 4,
              py: 1.5,
              borderRadius: 2,
              fontWeight: "bold",
              "&:hover": { bgcolor: "#1D4ED8" }
            }}
          >
            {loading
              ? "Allocating..."
              : "Allocate Resources"}
          </Button>
        </Box>

        {loading && (
          <LinearProgress sx={{ mb: 3, borderRadius: 2 }} />
        )}

        {message && (
          <Alert severity="success" sx={{ mb: 3 }}>
            {message}
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* SUMMARY */}

        <Grid container spacing={3} sx={{ mb: 3 }}>
          {[
            {
              label: "Processes Checked",
              value: total,
              color: "#60A5FA"
            },
            {
              label: "Allocated",
              value: allocated.length,
              color: "#4ADE80"
            },
            {
              label: "Waiting",
              value: waiting.length,
              color: "#FBBF24"
            },
            {
              label: "Errors",
              value: errors.length,
              color: "#FB7185"
            }
          ].map((item) => (
            <Grid item xs={12} sm={6} md={3} key={item.label}>
              <Paper sx={panel}>
                <Typography color={muted} variant="body2">
                  {item.label}
                </Typography>

                <Typography
                  variant="h3"
                  fontWeight="bold"
                  sx={{ color: item.color, mt: 1 }}
                >
                  {item.value}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        {/* PROCESS RESULTS */}

        <Paper sx={{ ...panel, mb: 3 }}>
          <Typography variant="h6" fontWeight="bold" mb={2}>
            Process Allocation Results
          </Typography>

          {!result ? (
            <Typography color={muted}>
              Click Allocate Resources to view the
              process-wise allocation results.
            </Typography>
          ) : results.length === 0 ? (
            <Alert severity="info">
              No processes currently awaiting resource allocation.
            </Alert>
          ) : (
            <Grid container spacing={2}>
              {results.map((process) => (
                <Grid
                  item
                  xs={12}
                  md={6}
                  lg={4}
                  key={process.process_id}
                >
                  <Box
                    sx={{
                      p: 2.5,
                      height: "100%",
                      borderRadius: 2,
                      background: "#172E54",
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
                        {process.process_id}
                      </Typography>

                      <Chip
                        size="small"
                        label={process.status}
                        color={getChipColor(process.status)}
                      />
                    </Stack>

                    {process.allocated_resources?.length > 0 && (
                      <>
                        <Typography
                          variant="subtitle2"
                          color="#4ADE80"
                          mb={1}
                        >
                          Allocated Resources
                        </Typography>

                        {formatResources(
                          process.allocated_resources
                        )}
                      </>
                    )}

                    {process.waiting_resources?.length > 0 && (
                      <>
                        <Typography
                          variant="subtitle2"
                          color="#FBBF24"
                          mt={1}
                          mb={1}
                        >
                          Waiting For
                        </Typography>

                        {formatResources(
                          process.waiting_resources,
                          true
                        )}
                      </>
                    )}

                    {process.message && (
                      <Typography
                        variant="caption"
                        color={muted}
                        display="block"
                        sx={{ mt: 2 }}
                      >
                        {process.message}
                      </Typography>
                    )}
                  </Box>
                </Grid>
              ))}
            </Grid>
          )}
        </Paper>

        {/* WAITING QUEUE */}

        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ ...panel, height: "100%" }}>
              <Typography variant="h6" fontWeight="bold" mb={2}>
                Waiting Queue
              </Typography>

              {!result ? (
                <Typography color={muted}>
                  Waiting processes will appear after allocation.
                </Typography>
              ) : !result.waiting_queue?.length ? (
                <Alert severity="success">
                  No processes currently in the waiting queue.
                </Alert>
              ) : (
                <Stack spacing={1.5}>
                  {result.waiting_queue.map((process) => (
                    <Box
                      key={process.process_id}
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        bgcolor: "#172E54",
                        display: "flex",
                        justifyContent: "space-between"
                      }}
                    >
                      <Box>
                        <Typography fontWeight="bold">
                          {process.process_id}
                        </Typography>

                        <Typography variant="caption" color={muted}>
                          Operation: {process.operation_id}
                        </Typography>
                      </Box>

                      <Chip
                        label="WAITING"
                        color="warning"
                        size="small"
                      />
                    </Box>
                  ))}
                </Stack>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ ...panel, height: "100%" }}>
              <Typography variant="h6" fontWeight="bold" mb={2}>
                Allocation Summary
              </Typography>

              <Typography color={muted} mb={2}>
                Results from the latest allocation request
              </Typography>

              {total > 0 ? (
                <>
                  <Typography variant="body2" mb={1}>
                    Allocated: {allocated.length} / {total}
                  </Typography>

                  <LinearProgress
                    variant="determinate"
                    value={(allocated.length / total) * 100}
                    color="success"
                    sx={{ height: 10, borderRadius: 2, mb: 3 }}
                  />

                  <Typography variant="body2" mb={1}>
                    Waiting: {waiting.length} / {total}
                  </Typography>

                  <LinearProgress
                    variant="determinate"
                    value={(waiting.length / total) * 100}
                    color="warning"
                    sx={{ height: 10, borderRadius: 2 }}
                  />
                </>
              ) : (
                <Typography color={muted}>
                  No allocation batch has been processed yet.
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>

        {/* RESOURCE HISTORY */}

        <Paper sx={panel}>
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="center"
            mb={2}
          >
            <Typography variant="h6" fontWeight="bold">
              Resource Allocation History
            </Typography>

            <Button
              variant="outlined"
              onClick={loadHistory}
              sx={{ color: "#93C5FD" }}
            >
              Refresh History
            </Button>
          </Stack>

          <Divider sx={{ borderColor: "#30486D", mb: 2 }} />

          {history.length === 0 ? (
            <Typography color={muted}>
              No resource allocation history found.
            </Typography>
          ) : (
            <TableContainer sx={{ maxHeight: 350 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    {[
                      "Process",
                      "Resource",
                      "Status",
                      "Allocation Time"
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
                  {history.map((entry, index) => (
                    <TableRow key={index}>
                      <TableCell sx={{ color: "white" }}>
                        {entry.process_id}
                      </TableCell>

                      <TableCell sx={{ color: muted }}>
                        {entry.resource_name}
                      </TableCell>

                      <TableCell>
                        <Chip
                          size="small"
                          label={entry.allocation_status}
                          color={
                            entry.allocation_status === "ALLOCATED"
                              ? "success"
                              : "default"
                          }
                        />
                      </TableCell>

                      <TableCell sx={{ color: muted }}>
                        {entry.allocation_time}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>

      </Box>
    </MainLayout>
  );
}

export default ResourceCenter;
