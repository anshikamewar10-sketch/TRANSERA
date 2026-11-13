
import { useEffect, useRef, useState } from "react";
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
  CircularProgress,
  LinearProgress,
  Stepper,
  Step,
  StepLabel
} from "@mui/material";

const panel = {
  p: 3,
  background: "#102347",
  border: "1px solid #243A61",
  borderRadius: 3,
  color: "white"
};

const muted = "#AFC1DB";

const stages = [
  "Reading Oracle Resource Data",
  "Analyzing Resource Dependencies",
  "Running Deadlock Detection",
  "Processing Detection Result"
];

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

function Deadlock() {
  const [loading, setLoading] = useState(false);
  const [resolving, setResolving] = useState(false);

  const [result, setResult] = useState(null);
  const [recovery, setRecovery] = useState(null);
  const [stage, setStage] = useState(-1);
  const [error, setError] = useState("");

  const timers = useRef([]);

  const clearTimers = () => {
    timers.current.forEach(clearTimeout);
    timers.current = [];
  };

  useEffect(() => {
    return () => clearTimers();
  }, []);

  const detectDeadlock = async () => {
    if (loading || resolving) return;

    clearTimers();
    setLoading(true);
    setError("");
    setResult(null);
    setRecovery(null);
    setStage(0);

    let responseData = null;
    let responseError = null;

    try {
      responseData = await requestJSON(
        api.detectDeadlock,
        "POST"
      );
    } catch (err) {
      responseError = err.message;
    }

    // The backend request has finished.
    // These delays visualize its completed stages.
    for (let i = 1; i < stages.length; i++) {
      timers.current.push(
        setTimeout(() => setStage(i), i * 450)
      );
    }

    timers.current.push(
      setTimeout(() => {
        if (responseError) {
          setError(responseError);
        } else {
          setResult(responseData);
        }

        setLoading(false);
        setStage(stages.length);
      }, stages.length * 450)
    );
  };

  const resolveDeadlock = async () => {
    if (!result?.deadlock || resolving) return;

    setResolving(true);
    setError("");

    try {
      const data = await requestJSON(
        api.resolveDeadlock,
        "POST"
      );

      setRecovery(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setResolving(false);
    }
  };

  const deadlocked = result?.deadlocked_processes || [];
  const completion = result?.completion_result;
  const completed = completion?.completed_processes || [];

  const statusLabel = !result
    ? "NOT CHECKED"
    : result.deadlock
      ? "DEADLOCK DETECTED"
      : result.status === "NO_DEADLOCK_COMPLETED"
        ? "NO DEADLOCK - COMPLETED"
        : result.status || "NO DEADLOCK";

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
              Deadlock Detection & Recovery
            </Typography>

            <Typography color={muted} mt={1}>
              Oracle-backed deadlock detection and
              process recovery simulator
            </Typography>
          </Box>

          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              onClick={detectDeadlock}
              disabled={loading || resolving}
              sx={{
                bgcolor: "#2563EB",
                px: 3,
                py: 1.4,
                fontWeight: "bold"
              }}
            >
              {loading ? "Detecting..." : "Detect Deadlock"}
            </Button>

            <Button
              variant="contained"
              color="error"
              onClick={resolveDeadlock}
              disabled={
                !result?.deadlock ||
                loading ||
                resolving ||
                recovery?.resolved === true
              }
              sx={{ px: 3, fontWeight: "bold" }}
            >
              {resolving ? "Resolving..." : "Resolve Deadlock"}
            </Button>
          </Stack>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* DETECTION STATUS */}

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
              Detection Status
            </Typography>

            <Chip
              label={statusLabel}
              color={
                !result
                  ? "default"
                  : result.deadlock
                    ? "error"
                    : result.success
                      ? "success"
                      : "warning"
              }
            />
          </Stack>

          {loading ? (
            <>
              <LinearProgress sx={{ mb: 3 }} />

              <Stepper activeStep={stage} alternativeLabel>
                {stages.map((label) => (
                  <Step key={label}>
                    <StepLabel
                      sx={{
                        "& .MuiStepLabel-label": {
                          color: "#AFC1DB !important",
                          fontSize: 12
                        }
                      }}
                    >
                      {label}
                    </StepLabel>
                  </Step>
                ))}
              </Stepper>
            </>
          ) : !result ? (
            <Typography color={muted}>
              Click Detect Deadlock to begin analysis.
            </Typography>
          ) : (
            <Alert
              severity={
                result.deadlock
                  ? "error"
                  : result.success
                    ? "success"
                    : "warning"
              }
            >
              {result.message}
            </Alert>
          )}
        </Paper>

        {/* PROCESS VISUALIZATION */}

        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ ...panel, minHeight: 310 }}>
              <Typography variant="h6" fontWeight="bold" mb={1}>
                Process Dependency Visualization
              </Typography>

              <Typography variant="body2" color={muted} mb={3}>
                Processes identified by the detection algorithm
              </Typography>

              {!result ? (
                <Box
                  sx={{
                    height: 180,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center"
                  }}
                >
                  {loading ? (
                    <CircularProgress />
                  ) : (
                    <Typography color={muted}>
                      Awaiting deadlock detection
                    </Typography>
                  )}
                </Box>
              ) : result.deadlock ? (
                <Box>
                  <Grid container spacing={2}>
                    {deadlocked.map((pid, index) => (
                      <Grid item xs={12} sm={6} key={pid}>
                        <Box
                          sx={{
                            p: 3,
                            borderRadius: 3,
                            textAlign: "center",
                            bgcolor: "#401E35",
                            border: "2px solid #F87171",
                            animation: "deadlockPulse 1.8s infinite"
                          }}
                        >
                          <Typography
                            variant="h5"
                            fontWeight="bold"
                          >
                            {pid}
                          </Typography>

                          <Chip
                            size="small"
                            color="error"
                            label="BLOCKED"
                            sx={{ mt: 1 }}
                          />
                        </Box>
                      </Grid>
                    ))}
                  </Grid>

                  <Box
                    sx={{
                      mt: 3,
                      p: 2,
                      textAlign: "center",
                      borderRadius: 2,
                      bgcolor: "#392539"
                    }}
                  >
                    <Typography color="#FCA5A5">
                      These processes cannot complete under
                      the current outstanding resource requests.
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Box
                  sx={{
                    p: 4,
                    borderRadius: 3,
                    bgcolor: "#153C39",
                    textAlign: "center"
                  }}
                >
                  <Typography
                    variant="h5"
                    fontWeight="bold"
                    color="#4ADE80"
                    mb={1}
                  >
                    NO DEADLOCK
                  </Typography>

                  <Typography color={muted}>
                    The system found no deadlocked processes.
                  </Typography>
                </Box>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper sx={{ ...panel, height: "100%" }}>
              <Typography variant="h6" fontWeight="bold" mb={2}>
                Detection Summary
              </Typography>

              <Stack spacing={2}>
                <Box>
                  <Typography variant="body2" color={muted}>
                    Deadlocked Processes
                  </Typography>

                  <Typography variant="h4" fontWeight="bold">
                    {deadlocked.length}
                  </Typography>
                </Box>

                <Divider sx={{ borderColor: "#30486D" }} />

                <Box>
                  <Typography variant="body2" color={muted}>
                    Completion Sequence
                  </Typography>

                  <Typography variant="h4" fontWeight="bold">
                    {result?.completion_sequence?.length || 0}
                  </Typography>
                </Box>

                <Divider sx={{ borderColor: "#30486D" }} />

                <Box>
                  <Typography variant="body2" color={muted}>
                    Automatically Completed
                  </Typography>

                  <Typography variant="h4" fontWeight="bold">
                    {completion?.total_completed || 0}
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Grid>
        </Grid>

        {/* COMPLETION SEQUENCE */}

        <Paper sx={{ ...panel, mb: 3 }}>
          <Typography variant="h6" fontWeight="bold" mb={2}>
            Simulated Completion Sequence
          </Typography>

          {!result?.completion_sequence?.length ? (
            <Typography color={muted}>
              No completion sequence available.
            </Typography>
          ) : (
            <Stack direction="row" flexWrap="wrap" gap={1.5}>
              {result.completion_sequence.map((pid, index) => (
                <Box
                  key={`${pid}-${index}`}
                  sx={{
                    px: 2,
                    py: 1.5,
                    borderRadius: 2,
                    bgcolor: "#172E54",
                    border: "1px solid #3B5B85"
                  }}
                >
                  <Typography fontWeight="bold">
                    {pid}
                  </Typography>
                </Box>
              ))}
            </Stack>
          )}

          <Typography
            variant="caption"
            color={muted}
            display="block"
            mt={2}
          >
            This sequence is calculated by the detector.
            It does not itself prove actual process completion.
          </Typography>
        </Paper>

        {/* AUTOMATIC COMPLETION */}

        {completion && (
          <Paper sx={{ ...panel, mb: 3 }}>
            <Typography variant="h6" fontWeight="bold" mb={2}>
              Automatic Process Completion
            </Typography>

            <Alert
              severity={completion.success ? "success" : "warning"}
              sx={{ mb: 2 }}
            >
              {completion.message}
            </Alert>

            <Grid container spacing={2}>
              {completed.map((process) => (
                <Grid item xs={12} md={6} key={process.process_id}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      bgcolor: "#173A3C",
                      border: "1px solid #2E7667"
                    }}
                  >
                    <Stack
                      direction="row"
                      justifyContent="space-between"
                      mb={1}
                    >
                      <Typography fontWeight="bold">
                        {process.process_id}
                      </Typography>

                      <Chip
                        size="small"
                        color="success"
                        label="TERMINATED"
                      />
                    </Stack>

                    <Typography color={muted} variant="body2">
                      Operation: {process.operation_id}
                    </Typography>

                    <Typography
                      color="#4ADE80"
                      variant="body2"
                      mt={1}
                    >
                      Business Status: {process.business_status}
                    </Typography>

                    <Typography color={muted} variant="caption">
                      Released:{" "}
                      {process.released_resources?.map(
                        (r) => `${r.resource_id} ×${r.units_released}`
                      ).join(", ") || "None"}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>

            {!!completion.errors?.length && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {completion.errors.map(
                  (e) => `${e.process_id}: ${e.message}`
                ).join("; ")}
              </Alert>
            )}
          </Paper>
        )}

        {/* DEADLOCK RECOVERY */}

        {result?.deadlock && (
          <Paper sx={{ ...panel, mb: 3 }}>
            <Typography variant="h6" fontWeight="bold" mb={2}>
              Deadlock Recovery Simulator
            </Typography>

            {!recovery ? (
              <Alert severity="warning">
                Deadlock detected. Click Resolve Deadlock
                to begin recovery.
              </Alert>
            ) : (
              <>
                <Alert
                  severity={
                    recovery.resolved ? "success" : "warning"
                  }
                  sx={{ mb: 3 }}
                >
                  {recovery.message}
                </Alert>

                <Stepper
                  activeStep={recovery.resolved ? 4 : 1}
                  alternativeLabel
                  sx={{
                    mb: 3,
                    "& .MuiStepLabel-label": {
                      color: "#AFC1DB !important",
                      fontSize: 12
                    }
                  }}
                >
                  {[
                    "Deadlock Identified",
                    "Victim Selected",
                    "Resources Released",
                    "Recovery Recorded"
                  ].map((step) => (
                    <Step key={step}>
                      <StepLabel>{step}</StepLabel>
                    </Step>
                  ))}
                </Stepper>

                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Box
                      sx={{
                        p: 3,
                        borderRadius: 2,
                        bgcolor: "#172E54"
                      }}
                    >
                      <Typography color={muted}>
                        Selected Recovery Victim
                      </Typography>

                      <Typography
                        variant="h4"
                        fontWeight="bold"
                        mt={1}
                      >
                        {recovery.victim_process_id || "—"}
                      </Typography>

                      <Chip
                        label={recovery.process_state || "UNKNOWN"}
                        color="warning"
                        sx={{ mt: 2 }}
                      />
                    </Box>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Box
                      sx={{
                        p: 3,
                        borderRadius: 2,
                        bgcolor: "#172E54"
                      }}
                    >
                      <Typography color={muted}>
                        Resources Released
                      </Typography>

                      {recovery.released_resources?.length ? (
                        recovery.released_resources.map((r, index) => (
                          <Typography key={index} mt={1}>
                            {r.resource_id} × {r.units_released}
                          </Typography>
                        ))
                      ) : (
                        <Typography color={muted} mt={1}>
                          No resource release recorded.
                        </Typography>
                      )}
                    </Box>
                  </Grid>
                </Grid>

                <Typography color={muted} mt={3}>
                  Return to Resource Allocation Center
                  and click Allocate Resources to retry
                  eligible waiting processes.
                </Typography>
              </>
            )}
          </Paper>
        )}

        {/* FOOTER */}

        <Paper sx={panel}>
          <Typography variant="h6" fontWeight="bold" mb={1}>
            Oracle Database Integration
          </Typography>

          <Typography color={muted} variant="body2">
            Deadlock detection reads current resource
            availability, active allocations and outstanding
            requests. Recovery updates the process state,
            releases allocated instances and records recovery
            information in Oracle.
          </Typography>
        </Paper>

        <style>
          {`
            @keyframes deadlockPulse {
              0% { box-shadow: 0 0 0 0 rgba(248,113,113,.22); }
              50% { box-shadow: 0 0 0 9px rgba(248,113,113,0); }
              100% { box-shadow: 0 0 0 0 rgba(248,113,113,0); }
            }
          `}
        </style>
      </Box>
    </MainLayout>
  );
}

export default Deadlock;
