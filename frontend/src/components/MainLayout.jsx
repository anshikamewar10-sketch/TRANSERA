import { Box } from "@mui/material";

import Header from "./Header";
import Sidebar from "./Sidebar";

function MainLayout({ children }) {

    return (

        <Box
            sx={{
                display: "flex",
                minHeight: "100vh",
                background: "#0E0E0E"
            }}
        >

            {/* Sidebar */}

            <Sidebar />

            {/* Right Section */}

            <Box
                sx={{
                    flex: 1,
                    display: "flex",
                    flexDirection: "column"
                }}
            >

                {/* Header */}

                <Header />

                {/* Page Content */}

                <Box
                    sx={{
                        flex: 1,
                        padding: "25px",
                        background: "#0E0E0E"
                    }}
                >

                    {children}

                </Box>

            </Box>

        </Box>

    );

}

export default MainLayout;