import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert
} from "@mui/material";

function Login() {

  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async () => {

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            username,
            password
          })
        }
      );

      const data = await response.json();

      if (data.success) {

        localStorage.setItem("isLoggedIn", "true");

        navigate("/dashboard");

      } else {

        setError(data.message);

      }

    } catch {

      setError("Backend Server Not Running");

    }

  };

  return (

    <Box
      sx={{
        minHeight: "100vh",
        background: "#0E0E0E",
        display: "flex",
        justifyContent: "center",
        alignItems: "center"
      }}
    >

      <Paper
        elevation={12}
        sx={{
          width: 380,
          p: 4,
          borderRadius: 3,
          background: "#1B1B1B",
          border: "1px solid #333"
        }}
      >

        <Typography
          variant="h4"
          fontWeight="bold"
          textAlign="center"
          color="#F4C542"
        >
          TRANSERA
        </Typography>

        <Typography
          textAlign="center"
          color="#CFCFCF"
          mt={1}
          mb={4}
        >
          Business Execution & Operating System Simulator
        </Typography>

        {error && (

          <Alert
            severity="error"
            sx={{ mb: 2 }}
          >
            {error}
          </Alert>

        )}

        <TextField
          fullWidth
          label="Username"
          margin="normal"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <TextField
          fullWidth
          type="password"
          label="Password"
          margin="normal"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <Button
          fullWidth
          variant="contained"
          sx={{
            mt: 3,
            height: 42,
            fontWeight: "bold"
          }}
          onClick={handleLogin}
        >
          LOGIN
        </Button>

      </Paper>

    </Box>

  );

}

export default Login;