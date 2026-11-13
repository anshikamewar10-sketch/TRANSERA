
import { useState, useRef, useEffect } from "react";
import MainLayout from "../components/MainLayout";
import api from "../api";

import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  Stack,
  LinearProgress,
  Alert,
  FormControl,
  Select,
  MenuItem,
  Divider
} from "@mui/material";

const algorithms = {
  FCFS: {
    label: "First Come First Serve (FCFS)",
    endpoint: "fcfs"
  },
  SJF: {
    label: "Shortest Job First (SJF)",
    endpoint: "sjf"
  },
  PRIORITY: {
    label: "Priority Scheduling",
    endpoint: "priority"
  },
  ROUND_ROBIN: {
    label: "Round Robin (Quantum = 2)",
    endpoint: "roundRobin"
  }
};

const panel = {
  p: 3,
  borderRadius: 3,
  background: "#102347",
  border: "1px solid #29436C",
  color: "white",
  minWidth: 0
};

const wait = (ms) =>
  new Promise((resolve) => setTimeout(resolve, ms));

async function postJSON(url) {
  const response = await fetch(url, {
    method: "POST"
  });

  const data = await response.json();

  if (!response.ok || !data.success) {
    throw new Error(
      data.message ||
      data.detail ||
      "Scheduler request failed."
    );
  }

  return data;
}

function Scheduler() {
  const [algorithm, setAlgorithm] = useState("FCFS");
  const [running, setRunning] = useState(false);
  const [readyQueue, setReadyQueue] = useState([]);
  const [runningProcess, setRunningProcess] = useState(null);
  const [completedQueue, setCompletedQueue] = useState([]);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const activeRef = useRef(false);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
    };
  }, []);

  const addLog = (message) => {
    if (!mountedRef.current) return;

    setLogs((previous) => [
      ...previous,
      message
    ]);
  };

  const updateIfMounted = (callback) => {
    if (mountedRef.current) callback();
  };

  async function simulateDuration(duration) {
    const totalMilliseconds = Math.max(
      100,
      Number(duration) * 1000
    );

    const steps = Math.max(
      1,
      Math.ceil(totalMilliseconds / 200)
    );

    for (let step = 1; step <= steps; step++) {
      await wait(totalMilliseconds / steps);

      updateIfMounted(() => {
        setProgress((step / steps) * 100);
      });
    }
  }

  async function executeNonPreemptive(data, selectedAlgorithm) {
    const queue = [...data.ready_queue];
    const schedule = data.gantt_chart || [];

    for (let index = 0; index < queue.length; index++) {
      const process = queue[index];

      const runURL =
        `${api.runProcess(process.process_id)}` +
        `?algorithm=${selectedAlgorithm}`;

      await postJSON(runURL);

      updateIfMounted(() => {
        setRunningProcess(process);
        setReadyQueue(queue.slice(index + 1));
        setProgress(0);
      });

      addLog(
        `${process.process_id} selected by ${selectedAlgorithm}.`
      );

      addLog(`${process.process_id} is RUNNING.`);

      await simulateDuration(process.burst_time);

      await postJSON(
        api.completeBurst(process.process_id)
      );

      updateIfMounted(() => {
        setCompletedQueue((previous) => [
          ...previous,
          process
        ]);

        setTimeline((previous) => [
          ...previous,
          schedule[index] || {
            process_id: process.process_id,
            duration: process.burst_time
          }
        ]);

        setRunningProcess(null);
      });

      addLog(
        `${process.process_id} CPU burst completed.`
      );

      addLog(
        `${process.process_id} moved to AWAITING_RESOURCES.`
      );

      await wait(400);
    }
  }

  async function executeRoundRobin(data) {
    const slices = data.gantt_chart || [];

    const original = data.ready_queue || [];

    const processMap = Object.fromEntries(
      original.map((process) => [
        process.process_id,
        process
      ])
    );

    const completed = new Set();

    for (let index = 0; index < slices.length; index++) {
      const slice = slices[index];

      const process = processMap[slice.process_id];

      if (!process) {
        throw new Error(
          `Unknown process ${slice.process_id}.`
        );
      }

      const runURL =
        `${api.runProcess(slice.process_id)}` +
        "?algorithm=ROUND_ROBIN";

      await postJSON(runURL);

      updateIfMounted(() => {
        setRunningProcess({
          ...process,
          current_slice: slice.duration,
          remaining_after: slice.remaining_after
        });

        setReadyQueue(
          slices
            .slice(index + 1)
            .filter(
              (item, position, array) =>
                array.findIndex(
                  (other) =>
                    other.process_id === item.process_id
                ) === position
            )
            .map((item) => ({
              ...processMap[item.process_id],
              remaining_burst_time: item.remaining_after
            }))
        );

        setProgress(0);
      });

      addLog(
        `${slice.process_id} RUNNING for ${slice.duration} CPU unit(s).`
      );

      await simulateDuration(slice.duration);

      const quantumResult = await postJSON(
        api.completeQuantum(
          slice.process_id,
          slice.duration
        )
      );

      if (
        Number(quantumResult.remaining_burst_time) !==
        Number(slice.remaining_after)
      ) {
        throw new Error(
          "Oracle remaining burst differs from schedule."
        );
      }

      updateIfMounted(() => {
        setTimeline((previous) => [
          ...previous,
          slice
        ]);

        setRunningProcess(null);
      });

      if (quantumResult.completed) {
        completed.add(slice.process_id);

        updateIfMounted(() => {
          setCompletedQueue(
            original.filter((item) =>
              completed.has(item.process_id)
            )
          );
        });

        addLog(
          `${slice.process_id} CPU completed. Awaiting Resources.`
        );
      } else {
        addLog(
          `${slice.process_id} quantum expired. ` +
          `${slice.remaining_after} CPU units remaining.`
        );

        addLog(
          `${slice.process_id} returned to READY queue.`
        );
      }

      await wait(350);
    }
  }

  async function startExecution() {
    if (activeRef.current) return;

    activeRef.current = true;

    setRunning(true);
    setError("");
    setLogs([]);
    setProgress(0);
    setReadyQueue([]);
    setRunningProcess(null);
    setCompletedQueue([]);
    setTimeline([]);
    setResult(null);

    const selectedAlgorithm = algorithm;

    try {
      const endpoint = algorithms[selectedAlgorithm].endpoint;

      const data = await postJSON(api[endpoint]);

      if (
        !Array.isArray(data.ready_queue) ||
        !Array.isArray(data.gantt_chart)
      ) {
        throw new Error(
          "Invalid scheduling response from backend."
        );
      }

      setResult(data);
      setReadyQueue(data.ready_queue);

      addLog(
        `${selectedAlgorithm} Scheduling Started.`
      );

      addLog(
        `${data.ready_queue.length} READY processes loaded.`
      );

      if (selectedAlgorithm === "ROUND_ROBIN") {
        await executeRoundRobin(data);
      } else {
        await executeNonPreemptive(
          data,
          selectedAlgorithm
        );
      }

      updateIfMounted(() => {
        setReadyQueue([]);
        setRunningProcess(null);
        setProgress(100);
      });

      addLog(
        `${selectedAlgorithm} Scheduling Completed.`
      );

      addLog(
        "CPU-completed processes are awaiting resource allocation."
      );

    } catch (err) {
      console.error("Scheduler error:", err);

      updateIfMounted(() => {
        setError(err.message);
        setRunningProcess(null);
      });

      addLog(`ERROR: ${err.message}`);

    } finally {
      activeRef.current = false;

      updateIfMounted(() => {
        setRunning(false);
      });
    }
  }

  return (
    <MainLayout>
      <Box sx={{ color: "white", pb: 5 }}>
        <Typography
          variant="h4"
          fontWeight="bold"
          mb={1}
        >
          Execution Scheduler
        </Typography>

        <Typography
          color="#B0C4DE"
          mb={3}
        >
          CPU Scheduling & Process Execution Simulation
        </Typography>

        <Paper sx={{ ...panel, mb: 3 }}>
          <Stack
            direction={{ xs: "column", md: "row" }}
            justifyContent="space-between"
            alignItems={{ xs: "stretch", md: "center" }}
            spacing={2}
          >
            <Box>
              <Typography variant="h6" fontWeight="bold">
                CPU Scheduling Algorithm
              </Typography>

              <Typography
                color="#B0C4DE"
                variant="body2"
                mt={1}
              >
                Select an algorithm and execute READY processes.
              </Typography>
            </Box>

            <Stack
              direction={{ xs: "column", sm: "row" }}
              spacing={2}
            >
              <FormControl
                size="small"
                sx={{
                  minWidth: 240,
                  bgcolor: "#172E54",
                  borderRadius: 1
                }}
              >
                <Select
                  value={algorithm}
                  disabled={running}
                  onChange={(event) =>
                    setAlgorithm(event.target.value)
                  }
                  sx={{
                    color: "white",
                    "& .MuiSvgIcon-root": {
                      color: "white"
                    }
                  }}
                >
                  {Object.entries(algorithms).map(
                    ([key, item]) => (
                      <MenuItem key={key} value={key}>
                        {item.label}
                      </MenuItem>
                    )
                  )}
                </Select>
              </FormControl>

              <Button
                variant="contained"
                disabled={running}
                onClick={startExecution}
                sx={{
                  bgcolor: "#2563EB",
                  fontWeight: "bold",
                  px: 3,
                  "&:hover": {
                    bgcolor: "#1D4ED8"
                  }
                }}
              >
                {running
                  ? "Executing..."
                  : "Start Execution"}
              </Button>
            </Stack>
          </Stack>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: {
              xs: "1fr",
              md: "repeat(3, minmax(0, 1fr))"
            },
            gap: 3,
            mb: 3
          }}
        >
          <Paper sx={panel}>
            <Typography variant="h6" fontWeight="bold" mb={2}>
              READY Queue
            </Typography>

            <Stack spacing={1.5}>
              {readyQueue.length === 0 ? (
                <Typography color="#B0C4DE">
                  No READY processes
                </Typography>
              ) : (
                readyQueue.map((process, index) => (
                  <Box
                    key={`${process.process_id}-${index}`}
                    sx={{
                      bgcolor: "#172E54",
                      borderRadius: 2,
                      p: 1.5
                    }}
                  >
                    <Stack
                      direction="row"
                      justifyContent="space-between"
                      alignItems="center"
                    >
                      <Chip
                        label={process.process_id}
                        color="primary"
                        size="small"
                      />

                      <Typography
                        variant="caption"
                        color="#B0C4DE"
                      >
                        #{index + 1}
                      </Typography>
                    </Stack>

                    <Typography
                      variant="caption"
                      color="#B0C4DE"
                      display="block"
                      mt={1}
                    >
                      Burst: {process.burst_time}
                      {" | "}
                      Priority: {process.priority}
                    </Typography>
                  </Box>
                ))
              )}
            </Stack>
          </Paper>

          <Paper sx={panel}>
            <Typography variant="h6" fontWeight="bold" mb={2}>
              RUNNING Process
            </Typography>

            {runningProcess ? (
              <Box>
                <Chip
                  label={runningProcess.process_id}
                  color="warning"
                  sx={{ mb: 2 }}
                />

                <Typography color="#B0C4DE" variant="body2">
                  {algorithm === "ROUND_ROBIN"
                    ? `Current quantum: ${runningProcess.current_slice}`
                    : `CPU Burst: ${runningProcess.burst_time}`}
                </Typography>

                <LinearProgress
                  variant="determinate"
                  value={progress}
                  sx={{
                    mt: 3,
                    height: 12,
                    borderRadius: 2
                  }}
                />

                <Typography
                  color="#B0C4DE"
                  variant="body2"
                  mt={1}
                >
                  {Math.round(progress)}% of current CPU execution
                </Typography>
              </Box>
            ) : (
              <Typography color="#B0C4DE">
                Waiting for CPU execution...
              </Typography>
            )}
          </Paper>

          <Paper sx={panel}>
            <Typography variant="h6" fontWeight="bold" mb={2}>
              CPU Completed
            </Typography>

            <Typography
              variant="caption"
              color="#B0C4DE"
              display="block"
              mb={2}
            >
              Processes moved to AWAITING_RESOURCES
            </Typography>

            <Stack spacing={1}>
              {completedQueue.length === 0 ? (
                <Typography color="#B0C4DE">
                  None
                </Typography>
              ) : (
                completedQueue.map((process) => (
                  <Chip
                    key={process.process_id}
                    label={process.process_id}
                    color="success"
                    variant="outlined"
                  />
                ))
              )}
            </Stack>
          </Paper>
        </Box>

        <Paper sx={{ ...panel, mb: 3 }}>
          <Typography variant="h6" fontWeight="bold" mb={2}>
            CPU Execution Timeline
          </Typography>

          {timeline.length === 0 ? (
            <Typography color="#B0C4DE">
              Execution timeline will appear here.
            </Typography>
          ) : (
            <Box
              sx={{
                display: "flex",
                gap: 1,
                overflowX: "auto",
                pb: 2
              }}
            >
              {timeline.map((slice, index) => (
                <Box
                  key={`${slice.process_id}-${index}`}
                  sx={{
                    minWidth: 100,
                    p: 2,
                    bgcolor:
                      index % 2 === 0
                        ? "#2563EB"
                        : "#385B94",
                    borderRadius: 2,
                    textAlign: "center"
                  }}
                >
                  <Typography fontWeight="bold">
                    {slice.process_id}
                  </Typography>

                  <Typography variant="caption">
                    {slice.start_time ?? "—"}
                    {" - "}
                    {slice.end_time ?? "—"}
                  </Typography>
                </Box>
              ))}
            </Box>
          )}
        </Paper>

        <Paper sx={{ ...panel, mb: 3 }}>
          <Typography variant="h6" fontWeight="bold" mb={2}>
            Execution Log
          </Typography>

          <Divider sx={{ borderColor: "#29436C", mb: 2 }} />

          <Stack spacing={1}>
            {logs.length === 0 ? (
              <Typography color="#B0C4DE">
                Waiting to start...
              </Typography>
            ) : (
              logs.map((log, index) => (
                <Typography
                  key={index}
                  variant="body2"
                  color="#B0C4DE"
                >
                  {log}
                </Typography>
              ))
            )}
          </Stack>
        </Paper>

        <Paper sx={panel}>
          <Typography variant="h6" fontWeight="bold" mb={2}>
            Scheduling Summary
          </Typography>

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: {
                xs: "repeat(2, 1fr)",
                md: "repeat(4, 1fr)"
              },
              gap: 2
            }}
          >
            {[
              {
                label: "READY",
                value: readyQueue.length
              },
              {
                label: "RUNNING",
                value: runningProcess ? 1 : 0
              },
              {
                label: "CPU COMPLETED",
                value: completedQueue.length
              },
              {
                label: "CPU SLICES",
                value: timeline.length
              }
            ].map((item) => (
              <Box
                key={item.label}
                sx={{
                  bgcolor: "#172E54",
                  borderRadius: 2,
                  p: 2
                }}
              >
                <Typography
                  color="#B0C4DE"
                  variant="caption"
                >
                  {item.label}
                </Typography>

                <Typography
                  variant="h4"
                  fontWeight="bold"
                  mt={1}
                >
                  {item.value}
                </Typography>
              </Box>
            ))}
          </Box>

          {result && (
            <Typography
              color="#B0C4DE"
              variant="body2"
              mt={2}
            >
              Algorithm: {result.algorithm}
              {result.time_quantum
                ? ` | Quantum: ${result.time_quantum}`
                : ""}
            </Typography>
          )}
        </Paper>
      </Box>
    </MainLayout>
  );
}

export default Scheduler;
