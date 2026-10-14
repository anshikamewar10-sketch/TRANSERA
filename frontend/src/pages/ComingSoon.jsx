import { Box, Button, Paper, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

function ComingSoon({ title }) {

    const navigate = useNavigate();

    return (

        <Box
            sx={{
                minHeight: "100vh",
                background: "#071330",
                display: "flex",
                justifyContent: "center",
                alignItems: "center"
            }}
        >

            <Paper
                elevation={10}
                sx={{
                    width: 500,
                    padding: 5,
                    borderRadius: 4,
                    background: "#102347",
                    color: "white",
                    textAlign: "center"
                }}
            >

                <Typography
                    variant="h4"
                    fontWeight="bold"
                    mb={2}
                >
                    {title}
                </Typography>

                <Typography
                    sx={{
                        color: "#90CAF9",
                        mb: 4
                    }}
                >
                    This module will be implemented in the next phase of Transera.
                </Typography>

                <Button
                    variant="contained"
                    onClick={() => navigate("/dashboard")}
                >
                    Back to Dashboard
                </Button>

            </Paper>

        </Box>

    );

}

export default ComingSoon;