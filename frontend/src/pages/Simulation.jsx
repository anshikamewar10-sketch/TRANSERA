import { useState } from "react";
import MainLayout from "../components/MainLayout";
import api from "../api";

import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  List,
  ListItem,
  ListItemText
} from "@mui/material";

function Simulation() {

  const [running, setRunning] = useState(false);

  const [completed, setCompleted] = useState(false);

  const [summaryOpen, setSummaryOpen] = useState(false);

  const [logs, setLogs] = useState([
    "Waiting to start..."
  ]);

  const [summary, setSummary] = useState(null);

  async function startSimulation() {

    setRunning(true);

    setCompleted(false);

    setLogs([
      "⏳ Reading Pending Operations..."
    ]);

    try {

      const response = await fetch(api.simulation, {

        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({

          simulate_all: true,

          number_of_operations: 0

        })

      });

      const data = await response.json();
      console.log("Simulation Response:", data);

      if (!data.success) {

        setStatus(data.message);

        setRunning(false);

        return;

      }

      setSummary(data);

      setTimeout(() => {

        setLogs((prev) => [
          ...prev,
          "✔ Reading Pending Operations...",
          "⏳ Creating Processes..."
        ]);

      }, 1000);

      setTimeout(() => {

        setLogs((prev) => [
          ...prev,
          "✔ Creating Processes...",
          "⏳ Updating Business Operations...",
          "⏳ Moving Processes to READY Queue..."
        ]);

      }, 2000);

      setTimeout(() => {
        setLogs((prev) => [
          ...prev,
          "✔ Updating Business Operations...",
          "✔ Moving Processes to READY Queue...",
          "✔ Simulation Completed Successfully."
        ]);

        setCompleted(true);

        setRunning(false);

      }, 3000);

    } catch (error) {

      console.log(error);

      setStatus("Unable to connect to backend.");

      setRunning(false);

    }

  }

  return (

    <MainLayout>

      <Typography className="page-title">

        Simulation Engine

      </Typography>

      <Typography className="page-subtitle">

        Business Operation → Process Converter

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

            Simulation

          </Typography>

          <Button
            variant="contained"
            disabled={running || completed}
            onClick={startSimulation}
          >

            Start Simulation

          </Button>

        </Box>

        <Box mt={4}>

          <Typography
            variant="h6"
            fontWeight="bold"
            mb={2}
          >
            Simulation Log
          </Typography>

          <Paper
            elevation={0}
            sx={{
              background: "#111",
              border: "1px solid #333",
              p: 2,
              minHeight: 180,
              borderRadius: 2
            }}
          >

            <Box>

              {logs.map((log, index) => (

                <Typography
                  key={index}
                  sx={{
                    color: "#F4C542",
                    fontFamily: "monospace",
                    mb: 1
                  }}
                >

                  {log}

                </Typography>

              ))}

            </Box>

            {running && (

              <LinearProgress
                sx={{ mt: 2 }}
              />

            )}

          </Paper>

          {running && (

            <LinearProgress sx={{ mt: 2 }} />

          )}

        </Box>

        {completed && (

          <Box mt={4}>

            <Button
              variant="outlined"
              onClick={() => setSummaryOpen(true)}
            >

              View Simulation Summary

            </Button>

          </Box>

        )}

      </Paper>
      {/* Simulation Summary Dialog */}

      <Dialog
        open={summaryOpen}
        onClose={() => setSummaryOpen(false)}
        maxWidth="sm"
        fullWidth
      >

        <DialogTitle>

          Simulation Summary

        </DialogTitle>

        <DialogContent dividers>

          {summary && (

            <Grid container spacing={2}>

              <Grid item xs={12}>

                <Typography fontWeight="bold">

                  Pending Operations

                </Typography>

                <Typography>

                  {summary.summary.pending_operations}

                </Typography>

              </Grid>

              <Grid item xs={12}>

                <Typography fontWeight="bold">

                  Processes Created

                </Typography>

                <Typography>

                  {summary.summary.processes_created}

                </Typography>

              </Grid>

              <Grid item xs={12}>

                <Typography fontWeight="bold">

                  READY Queue Size

                </Typography>

                <Typography>

                  {summary.summary.ready_queue_size}

                </Typography>


              </Grid>

              <Grid item xs={12}>

                <Typography
                  fontWeight="bold"
                  sx={{ mt: 2 }}
                >

                  READY Queue

                </Typography>

                <List>

                  {summary.ready_queue.map((process) => (

                    <ListItem
                      key={process.process_id}
                    >

                      <ListItemText

                        primary={process.process_id}

                        secondary={`Operation : ${process.operation_id} | Priority : ${process.priority} | State : ${process.state}`}

                      />

                    </ListItem>

                  ))}

                </List>

              </Grid>

            </Grid>

          )}

        </DialogContent>

        <DialogActions>

          <Button

            variant="contained"

            onClick={() => setSummaryOpen(false)}

          >

            Close

          </Button>

        </DialogActions>

      </Dialog>

    </MainLayout>

  );

}

export default Simulation;