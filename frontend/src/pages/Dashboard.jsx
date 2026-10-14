import MainLayout from "../components/MainLayout";

import {
    Box,
    Typography,
    Paper
} from "@mui/material";

function Dashboard() {

    return (

        <MainLayout>

            <Paper

                elevation={8}

                sx={{

                    background: "#102347",

                    color: "white",

                    padding: 5,

                    borderRadius: 4

                }}

            >

                <Typography

                    variant="h3"

                    fontWeight="bold"

                    mb={2}

                >

                    Welcome to TRANSERA

                </Typography>

                <Typography

                    sx={{

                        color: "#90CAF9",

                        fontSize: 18,

                        lineHeight: 2

                    }}

                >

                    Business Execution & Operating System Simulator

                </Typography>

                <Box mt={5}>

                    <Typography
                        variant="h5"
                        fontWeight="bold"
                        mb={2}
                    >

                        Select any module from the sidebar to begin.

                    </Typography>

                    <Typography
                        sx={{
                            color: "#B0BEC5",
                            lineHeight: 2
                        }}
                    >

                        • Operation Hub

                        <br />

                        • Simulation Engine

                        <br />

                        • Execution Scheduler

                        <br />

                        • Resource Center

                        <br />

                        • Deadlock Resolver

                        <br />

                        • Transaction Center (Coming Soon)

                        <br />

                        • System Logs (Coming Soon)

                        <br />

                        • Analytics (Coming Soon)

                    </Typography>

                </Box>

            </Paper>

        </MainLayout>

    );

}

export default Dashboard;