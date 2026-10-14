import { AppBar, Toolbar, Typography, Button } from "@mui/material";
import LogoutIcon from "@mui/icons-material/Logout";
import { useNavigate } from "react-router-dom";

function Header() {

    const navigate = useNavigate();

    const logout = () => {

        localStorage.removeItem("isLoggedIn");

        navigate("/");

    };

    return (

        <AppBar

            position="static"

            elevation={0}

            sx={{

                background:"#141414",

                borderBottom:"1px solid #2A2A2A"

            }}

        >

            <Toolbar

                sx={{

                    display:"flex",

                    justifyContent:"space-between"

                }}

            >

                <Typography

                    variant="h5"

                    fontWeight="bold"

                    color="#F4C542"

                >

                    TRANSERA

                </Typography>

                <Button

                    variant="contained"

                    color="warning"

                    startIcon={<LogoutIcon />}

                    onClick={logout}

                    sx={{

                        fontWeight:"bold",

                        px:3

                    }}

                >

                    Logout

                </Button>

            </Toolbar>

        </AppBar>

    );

}

export default Header;