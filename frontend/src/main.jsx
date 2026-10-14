import React from "react";
import ReactDOM from "react-dom/client";

import { BrowserRouter } from "react-router-dom";

import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

import "./theme.css";

import App from "./App";

const theme = createTheme({

  palette: {

    mode: "dark",

    primary: {
      main: "#F4C542"
    },

    background: {
      default: "#0E0E0E",
      paper: "#1B1B1B"
    },

    text: {
      primary: "#FFFFFF",
      secondary: "#D0D0D0"
    }

  },

  typography: {

    fontFamily: [
      "Inter",
      "Segoe UI",
      "sans-serif"
    ].join(","),

    h4: {

      fontWeight: 700

    },

    h5: {

      fontWeight: 600

    }

  },

  shape: {

    borderRadius: 12

  }

});

ReactDOM.createRoot(document.getElementById("root")).render(

  <React.StrictMode>

    <ThemeProvider theme={theme}>

      <CssBaseline />

      <BrowserRouter>

        <App />

      </BrowserRouter>

    </ThemeProvider>

  </React.StrictMode>

);