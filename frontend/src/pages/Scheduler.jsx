import { useState, useEffect } from "react";
import MainLayout from "../components/MainLayout";
import api from "../api";

import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Chip
} from "@mui/material";

function Scheduler() {

  const [running, setRunning] = useState(false);

  const [readyQueue, setReadyQueue] = useState([]);

  const [runningProcess, setRunningProcess] = useState(null);

  const [terminatedQueue, setTerminatedQueue] = useState([]);

  const [progress, setProgress] = useState(0);
 /* useEffect(() => {

    if (!runningProcess) return;

    let value = 0;

    const timer = setInterval(() => {

      value += 20;

      setProgress(value);

      if (value >= 100) {

        clearInterval(timer);
        setLogs((prev)=>([

        ...prev,

        `✔ ${runningProcess.process_id} CPU Burst Completed.`

    ]));

    setRunningProcess(null);
    setLogs((prev)=>([

    ...prev,

    "✔ FCFS Scheduling Completed.",

    "⏳ Waiting For Resource Allocation..."

]));

}

    }, 500);

    return () => clearInterval(timer);

  }, [runningProcess]);*/

  const [logs, setLogs] = useState([]);

  const [fcfsResult, setFcfsResult] = useState(null);

  async function startExecution() {
    console.log("Start Execution Clicked");

try {

    setRunning(true);

    setProgress(0);

    setLogs([]);

    setRunningProcess(null);

    setTerminatedQueue([]);

    const response = await fetch(api.fcfs, {

        method: "POST"

    });

    const data = await response.json();

    console.log("Scheduler Response:", data);

    if (!data.success) {

        setLogs(["❌ " + data.message]);

        setRunning(false);

        return;

    }

    setFcfsResult(data);

    const queue = [...data.ready_queue];

    setReadyQueue(queue);

    setLogs([

        "✔ FCFS Scheduling Started.",

        `✔ ${queue.length} READY Processes Loaded.`

    ]);

    executeNextProcess(queue, 0);

}
catch(error){

    console.log(error);

    setRunning(false);

}

  }
  async function markProcessRunning(processId) {

    try {

        await fetch(api.runProcess(processId), {

            method: "POST"

        });

        console.log(processId + " is now RUNNING");

    } catch (error) {

        console.log(error);

    }

}

async function executeNextProcess(queue, index) {

    // All processes have finished CPU scheduling
    if (index >= queue.length) {

        setRunning(false);
        setRunningProcess(null);
        setReadyQueue([]);
        setProgress(100);

        setLogs((prev) => [
            ...prev,
            "✔ FCFS Scheduling Completed.",
            "⏳ All processes are awaiting resource allocation."
        ]);

        return;
    }

    const process = queue[index];

    try {

        // Start process in Oracle first
        const response = await fetch(
            api.runProcess(process.process_id),
            { method: "POST" }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.message || "Failed to start process."
            );
        }

        // Update frontend after backend confirms RUNNING
        setReadyQueue(queue.slice(index + 1));
        setRunningProcess(process);
        setProgress(0);

        setLogs((prev) => [
            ...prev,
            `✔ ${process.process_id} Selected by FCFS.`,
            `✔ ${process.process_id} is RUNNING.`
        ]);

        // Use actual burst time
        const burstTime = Math.max(
            1,
            Number(process.burst_time) || 5
        );

        for (let second = 1; second <= burstTime; second++) {

            await new Promise((resolve) =>
                setTimeout(resolve, 1000)
            );

            setProgress((second / burstTime) * 100);
        }

        // Tell Oracle the CPU burst has completed
        const completeResponse = await fetch(
            api.completeBurst(process.process_id),
            { method: "POST" }
        );

        const completeData = await completeResponse.json();

        if (!completeResponse.ok || !completeData.success) {
            throw new Error(
                completeData.message ||
                "CPU burst completion failed."
            );
        }

        setLogs((prev) => [
            ...prev,
            `✔ ${process.process_id} CPU Burst Completed.`,
            `✔ ${process.process_id} moved to AWAITING_RESOURCES.`
        ]);

        // Clear CPU before starting the next process
        setRunningProcess(null);

        await new Promise((resolve) =>
            setTimeout(resolve, 500)
        );

        // Execute next process in FCFS order
        await executeNextProcess(queue, index + 1);

    } catch (error) {

        console.error("FCFS Error:", error);

        setLogs((prev) => [
            ...prev,
            `❌ ${process.process_id}: ${error.message}`
        ]);

        setRunning(false);
    }
}


  return (

    <MainLayout>

      <Typography className="page-title">

        Execution Scheduler

      </Typography>

      <Typography className="page-subtitle">

        First Come First Serve (FCFS)

      </Typography>

      <Paper className="card" sx={{ p: 3 }}>

        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}
        >

          <Typography
            variant="h6"
            fontWeight="bold"
          >

            FCFS Scheduler

          </Typography>

          <Button

            variant="contained"

            disabled={running}

            onClick={startExecution}

          >

            Start Execution

          </Button>

        </Box>

      </Paper>

      <Grid
        container
        spacing={3}
        sx={{ mt: 1 }}
      >

        {/* READY QUEUE */}

        <Grid item xs={12} md={4}>

          <Paper className="card">

            <Typography
              variant="h6"
              fontWeight="bold"
              mb={2}
            >

              READY Queue

            </Typography>

            <List>

              {readyQueue.length === 0 ? (

                <Typography>

                  No READY Processes

                </Typography>

              ) : (

                readyQueue.map((process) => (

                  <ListItem
                    key={process.process_id}
                  >

                    <Chip

                      label={process.process_id}

                    />

                  </ListItem>
                ))

              )}

            </List>

          </Paper>

        </Grid>

        {/* RUNNING */}

        <Grid item xs={12} md={4}>

          <Paper className="card">

            <Typography
              variant="h6"
              fontWeight="bold"
            >

              Running Process

            </Typography>

            <Box mt={3}>

              {runningProcess ? (

                <>

                  <Typography
                    variant="h5"
                    fontWeight="bold"
                  >

                    {runningProcess.process_id}

                  </Typography>

                  <LinearProgress
                    variant="determinate"
                    value={progress}
                    sx={{ mt: 2 }}
                  />

                </>

              ) : (

                <Typography>

                  Waiting...

                </Typography>

              )}

            </Box>

          </Paper>

        </Grid>

        {/* TERMINATED */}

        <Grid item xs={12} md={4}>

          <Paper className="card">

            <Typography
              variant="h6"
              fontWeight="bold"
              mb={2}
            >

              Terminated

            </Typography>

            <List>

              {terminatedQueue.length === 0 ? (

                <Typography>

                  None

                </Typography>

              ) : (

                terminatedQueue.map((process) => (

                  <ListItem
                    key={process.process_id}
                  >

                    <Chip
                      color="success"
                      label={process.process_id}
                    />

                  </ListItem>

                ))

              )}

            </List>

          </Paper>

        </Grid>

      </Grid>
      {/* Execution Log */}

      <Paper className="card" sx={{ mt: 3, p: 3 }}>

        <Typography
          variant="h6"
          fontWeight="bold"
          mb={2}
        >
          Execution Log
        </Typography>

        <List>

          {logs.length === 0 ? (

            <Typography>

              Waiting to start...

            </Typography>

          ) : (

            logs.map((log, index) => (

              <ListItem key={index}>

                <ListItemText primary={log} />

              </ListItem>

            ))

          )}

        </List>

      </Paper>

      {/* Summary */}

      <Paper className="card" sx={{ mt: 3, p: 3 }}>

        <Grid container spacing={2}>

          <Grid item xs={4}>

            <Typography variant="h6">

              READY

            </Typography>

            <Typography variant="h4">

              {readyQueue.length}

            </Typography>

          </Grid>

          <Grid item xs={4}>

            <Typography variant="h6">

              RUNNING

            </Typography>

            <Typography variant="h4">

              {runningProcess ? 1 : 0}

            </Typography>

          </Grid>

          <Grid item xs={4}>

            <Typography variant="h6">

              TERMINATED

            </Typography>

            <Typography variant="h4">

              {terminatedQueue.length}

            </Typography>

          </Grid>

        </Grid>

      </Paper>

    </MainLayout>

  );

}

export default Scheduler;