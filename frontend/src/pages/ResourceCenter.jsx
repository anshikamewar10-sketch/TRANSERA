import MainLayout from "../components/MainLayout";

import {
  Grid,
  Paper,
  Typography,
  Box
} from "@mui/material";

function ResourceCenter() {

  return (

    <MainLayout>

      <Typography
        variant="h4"
        fontWeight="bold"
        color="white"
        mb={3}
      >

        Resource Center

      </Typography>

      <Grid container spacing={3}>

        {/* Running Process */}

        <Grid item xs={12} md={4}>

          <Paper
            elevation={8}
            sx={{
              p:3,
              borderRadius:3,
              background:"#102347",
              minHeight:220
            }}
          >

            <Typography
              variant="h6"
              color="white"
              mb={2}
            >

              Running Process

            </Typography>

            <Typography color="#B0BEC5">

              Process will appear here.

            </Typography>

          </Paper>

        </Grid>

        {/* Resources */}

        <Grid item xs={12} md={4}>

          <Paper
            elevation={8}
            sx={{
              p:3,
              borderRadius:3,
              background:"#102347",
              minHeight:220
            }}
          >

            <Typography
              variant="h6"
              color="white"
              mb={2}
            >

              Resources

            </Typography>

            <Box color="#B0BEC5">

              Resource allocation will appear here.

            </Box>

          </Paper>

        </Grid>

        {/* Waiting Queue */}

        <Grid item xs={12} md={4}>

          <Paper
            elevation={8}
            sx={{
              p:3,
              borderRadius:3,
              background:"#102347",
              minHeight:220
            }}
          >

            <Typography
              variant="h6"
              color="white"
              mb={2}
            >

              Waiting Queue

            </Typography>

            <Typography color="#B0BEC5">

              Waiting queue will appear here.

            </Typography>

          </Paper>

        </Grid>

        {/* Resource History */}

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

              Resource History

            </Typography>

            <Typography color="#B0BEC5">

              Resource allocation history will be loaded from Oracle Database.

            </Typography>

          </Paper>

        </Grid>

      </Grid>

    </MainLayout>

  );

}

export default ResourceCenter;