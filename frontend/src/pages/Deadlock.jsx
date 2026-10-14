import MainLayout from "../components/MainLayout";

import {
  Grid,
  Paper,
  Typography,
  Chip
} from "@mui/material";

function Deadlock() {

  return (

    <MainLayout>

      <Typography
        variant="h4"
        fontWeight="bold"
        color="white"
        mb={3}
      >

        Deadlock Resolver

      </Typography>

      <Grid container spacing={3}>

        {/* Current Status */}

        <Grid item xs={12}>

          <Paper
            elevation={8}
            sx={{
              p:3,
              borderRadius:3,
              background:"#102347"
            }}
          >

            <Typography
              variant="h6"
              color="white"
              mb={2}
            >

              Current Status

            </Typography>

            <Chip
              label="SAFE"
              color="success"
              sx={{
                fontSize:16,
                padding:2
              }}
            />

          </Paper>

        </Grid>

        {/* Safe Sequence */}

        <Grid item xs={12} md={6}>

          <Paper
            elevation={8}
            sx={{
              p:3,
              borderRadius:3,
              background:"#102347",
              minHeight:250
            }}
          >

            <Typography
              variant="h6"
              color="white"
              mb={2}
            >

              Safe Sequence

            </Typography>

            <Typography color="#B0BEC5">

              Safe sequence from Banker's Algorithm will appear here.

            </Typography>

          </Paper>

        </Grid>

        {/* Waiting Processes */}

        <Grid item xs={12} md={6}>

          <Paper
            elevation={8}
            sx={{
              p:3,
              borderRadius:3,
              background:"#102347",
              minHeight:250
            }}
          >

            <Typography
              variant="h6"
              color="white"
              mb={2}
            >

              Waiting Processes

            </Typography>

            <Typography color="#B0BEC5">

              Waiting processes will appear here.

            </Typography>

          </Paper>

        </Grid>

        {/* Resource Ownership */}

        <Grid item xs={12}>

          <Paper
            elevation={8}
            sx={{
              p:3,
              borderRadius:3,
              background:"#102347"
            }}
          >

            <Typography
              variant="h6"
              color="white"
              mb={2}
            >

              Resource Ownership

            </Typography>

            <Typography color="#B0BEC5">

              Current resource ownership will be loaded from Oracle Database.

            </Typography>

          </Paper>

        </Grid>

      </Grid>

    </MainLayout>

  );

}

export default Deadlock;