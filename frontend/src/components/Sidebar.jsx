import {
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Divider
} from "@mui/material";

import DashboardIcon from "@mui/icons-material/Dashboard";
import BusinessCenterIcon from "@mui/icons-material/BusinessCenter";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import MemoryIcon from "@mui/icons-material/Memory";
import StorageIcon from "@mui/icons-material/Storage";
import SecurityIcon from "@mui/icons-material/Security";
import ReceiptLongIcon from "@mui/icons-material/ReceiptLong";
import DescriptionIcon from "@mui/icons-material/Description";
import AnalyticsIcon from "@mui/icons-material/Analytics";

import { useLocation, useNavigate } from "react-router-dom";

const drawerWidth = 240;

function Sidebar() {

  const navigate = useNavigate();
  const location = useLocation();

  const menu = [

    {
      title: "Dashboard",
      icon: <DashboardIcon />,
      path: "/dashboard"
    },

    {
      title: "Operation Hub",
      icon: <BusinessCenterIcon />,
      path: "/operation"
    },

    {
      title: "Simulation Engine",
      icon: <PlayCircleIcon />,
      path: "/simulation"
    },

    {
      title: "Execution Scheduler",
      icon: <MemoryIcon />,
      path: "/scheduler"
    },

    {
      title: "Resource Center",
      icon: <StorageIcon />,
      path: "/resource"
    },

    {
      title: "Deadlock Resolver",
      icon: <SecurityIcon />,
      path: "/deadlock"
    },

    {
      title: "Transaction Center",
      icon: <ReceiptLongIcon />,
      path: "/transactions"
    },

    {
      title: "System Logs",
      icon: <DescriptionIcon />,
      path: "/logs"
    },

    {
      title: "Analytics",
      icon: <AnalyticsIcon />,
      path: "/analytics"
    }

  ];

  return (

    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,

        "& .MuiDrawer-paper": {

          width: drawerWidth,

          background: "#141414",

          borderRight: "1px solid #2A2A2A",

          color: "white"

        }

      }}
    >

      <Toolbar>

        <Typography
          variant="h6"
          fontWeight="bold"
          color="#F4C542"
        >

          MENU

        </Typography>

      </Toolbar>

      <Divider sx={{ background: "#2A2A2A" }} />

      <List>

        {menu.map((item) => (

          <ListItemButton

            key={item.title}

            selected={location.pathname === item.path}

            onClick={() => navigate(item.path)}

            sx={{

              margin: "6px 10px",

              borderRadius: "10px",

              "&.Mui-selected": {

                background: "#F4C542",

                color: "#000"

              },

              "&.Mui-selected .MuiListItemIcon-root": {

                color: "#000"

              }

            }}

          >

            <ListItemIcon
              sx={{ color: "white", minWidth: 40 }}
            >
              {item.icon}
            </ListItemIcon>

            <ListItemText primary={item.title} />

          </ListItemButton>

        ))}

      </List>

    </Drawer>

  );

}

export default Sidebar;