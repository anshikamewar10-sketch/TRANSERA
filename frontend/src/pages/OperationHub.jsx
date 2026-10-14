
import { useState, useEffect } from "react";
import MainLayout from "../components/MainLayout";
import api from "../api";

import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Chip,
  Alert,
  CircularProgress,
} from "@mui/material";

function OperationHub() {
  const [open, setOpen] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedOperation, setSelectedOperation] = useState(null);
  const [search, setSearch] = useState("");
  const [operations, setOperations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const initialForm = {
    user_id: "",
    product_id: "",
    operation_type: "",
    department: "",
    quantity: "",
    priority: "",
    description: "",
  };

  const [form, setForm] = useState(initialForm);

  // Load operations when the component opens
  useEffect(() => {
    loadOperations();
  }, []);

  // Fetch operations from the backend
  async function loadOperations() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(api.getOperations);

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setOperations(
          Array.isArray(data.operations) ? data.operations : []
        );
      } else {
        throw new Error(data.message || "Failed to load operations.");
      }
    } catch (err) {
      console.error("Error loading operations:", err);
      setError(err.message || "Unable to load operations.");
    } finally {
      setLoading(false);
    }
  }

  async function loadOperationDetails(operationId) {

    try {

      const response = await fetch(
        api.operationDetails(operationId)
      );

      const data = await response.json();

      if (data.success) {

        setSelectedOperation(data.operation);

        setDetailsOpen(true);

      }

    } catch (error) {

      console.log(error);

      setError("Unable to load operation details.");

    }

  }

  // Update form fields
  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  // Close dialog and reset form
  function handleClose() {
    if (saving) return;

    setOpen(false);
    setForm(initialForm);
    setError("");
  }

  // Save a new business operation
  async function handleSave() {
    setError("");
    setSuccess("");

    if (
      !form.user_id.trim() ||
      !form.product_id.trim() ||
      !form.operation_type.trim() ||
      !form.department.trim() ||
      !form.quantity ||
      !form.priority
    ) {
      setError("Please fill in all required fields.");
      return;
    }

    const quantity = Number(form.quantity);

    if (!Number.isInteger(quantity) || quantity <= 0) {
      setError("Quantity must be a positive whole number.");
      return;
    }

    setSaving(true);

    try {
      /*
       * IMPORTANT:
       * Replace api.createOperation with your actual POST endpoint
       * if your backend uses a different route.
       */
      const response = await fetch(api.createOperation, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({

          user_id: form.user_id.trim(),

          product_id: form.product_id.trim(),

          operation_type: form.operation_type.trim(),

          description: form.description.trim(),

          department: form.department.trim(),

          operation_quantity: quantity,

          operation_mode: "MANUAL",

          priority: form.priority

        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {

        throw new Error(
          data.message || "Failed to create business operation."
        );

      }

      setSuccess("Business operation created successfully.");

      setError("");

      setOpen(false);

      setForm(initialForm);

      await loadOperations();
      setSuccess("Operation Created Successfully.");
    } catch (err) {
      console.error("Error saving operation:", err);
      setError(err.message || "Unable to save operation.");
    } finally {
      setSaving(false);
    }
  }

  // Filter operations using the search box
  const filteredOperations = operations.filter((row) => {

    const value = search.toLowerCase().trim();

    if (value === "") return true;

    return (

      String(row.operation_id ?? "")
        .toLowerCase()
        .includes(value)

      ||

      String(row.user_id ?? "")
        .toLowerCase()
        .includes(value)

      ||

      String(row.product_id ?? "")
        .toLowerCase()
        .includes(value)

      ||

      String(row.department ?? "")
        .toLowerCase()
        .includes(value)

      ||

      String(row.operation_type ?? "")
        .toLowerCase()
        .includes(value)

      ||

      String(row.priority ?? "")
        .toLowerCase()
        .includes(value)

    );

  });

  return (
    <MainLayout>
      <Typography className="page-title">
        Operation Hub
      </Typography>

      <Typography className="page-subtitle">
        Business Operation Management
      </Typography>

      {error && !open && (
        <Alert
          severity="error"
          sx={{ mb: 2 }}
          onClose={() => setError("")}
        >
          {error}
        </Alert>
      )}

      {success && (
        <Alert
          severity="success"
          sx={{ mb: 2 }}
          onClose={() => setSuccess("")}
        >
          {success}
        </Alert>
      )}

      <Paper className="card" sx={{ p: 3 }}>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          gap={2}
          flexWrap="wrap"
          mb={3}
        >
          <Typography variant="h6" fontWeight="bold">
            Business Operations
          </Typography>

          <Button
            variant="contained"
            onClick={() => {
              setError("");
              setSuccess("");
              setOpen(true);
            }}
          >
            + New Business Operation
          </Button>
        </Box>

        <TextField
          fullWidth
          placeholder="Search by Operation ID, User ID or Product ID"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />

        <TableContainer sx={{ mt: 3 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Operation ID</TableCell>
                <TableCell>User</TableCell>
                <TableCell>Product</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Priority</TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <CircularProgress size={28} sx={{ my: 2 }} />
                    <Typography variant="body2">
                      Loading operations...
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : filteredOperations.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    {search
                      ? "No matching operations found."
                      : "No operations found."}
                  </TableCell>
                </TableRow>
              ) : (
                filteredOperations.map((row) => (
                  <TableRow
                    hover
                    key={row.operation_id}
                    sx={{ cursor: "pointer" }}
                    onClick={() => loadOperationDetails(row.operation_id)}
                  >
                    <TableCell>
                      {row.operation_id ?? "—"}
                    </TableCell>

                    <TableCell>
                      {row.user_id ?? "—"}
                    </TableCell>

                    <TableCell>
                      {row.product_id ?? "—"}
                    </TableCell>

                    <TableCell>
                      {row.department ?? "—"}
                    </TableCell>

                    <TableCell>
                      <Chip
                        label={row.business_status || "Pending"}
                        color={
                          String(row.business_status || "")
                            .toLowerCase() === "completed"
                            ? "success"
                            : "primary"
                        }
                        size="small"
                      />
                    </TableCell>

                    <TableCell>
                      {row.priority ?? "—"}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <Box display="flex" justifyContent="flex-end" mt={2}>
          <Button
            variant="outlined"
            onClick={loadOperations}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Paper>

      {/* Create Operation Dialog */}
      <Dialog
        open={open}
        onClose={handleClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Create New Business Operation
        </DialogTitle>

        <DialogContent>
          {error && (
            <Alert
              severity="error"
              sx={{ mt: 1, mb: 2 }}
              onClose={() => setError("")}
            >
              {error}
            </Alert>
          )}

          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                required
                name="user_id"
                label="User ID"
                value={form.user_id}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                required
                name="product_id"
                label="Product ID"
                value={form.product_id}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                required
                name="operation_type"
                label="Operation Type"
                value={form.operation_type}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                required
                name="department"
                label="Department"
                value={form.department}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                required
                type="number"
                name="quantity"
                label="Quantity"
                value={form.quantity}
                onChange={handleChange}
                slotProps={{
                  htmlInput: { min: 1, step: 1 },
                }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                required
                select
                name="priority"
                label="Priority"
                value={form.priority}
                onChange={handleChange}
                slotProps={{
                  select: { native: true },
                }}
              >
                <option value="">Select Priority</option>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Critical">Critical</option>
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                name="description"
                label="Description"
                value={form.description}
                onChange={handleChange}
              />
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ p: 2 }}>
          <Button
            onClick={handleClose}
            disabled={saving}
          >
            Cancel
          </Button>

          <Button
            variant="contained"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? "Saving..." : "Save Operation"}
          </Button>
        </DialogActions>
      </Dialog>
      {/* Operation Details Dialog */}

      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>

          Operation Details

        </DialogTitle>

        <DialogContent dividers>

          {selectedOperation && (

            <Grid container spacing={2}>

              <Grid item xs={6}>
                <Typography fontWeight="bold">
                  Operation ID
                </Typography>
                <Typography>
                  {selectedOperation.operation_id}
                </Typography>
              </Grid>

              <Grid item xs={6}>
                <Typography fontWeight="bold">
                  User ID
                </Typography>
                <Typography>
                  {selectedOperation.user_id}
                </Typography>
              </Grid>

              <Grid item xs={6}>
                <Typography fontWeight="bold">
                  Product ID
                </Typography>
                <Typography>
                  {selectedOperation.product_id}
                </Typography>
              </Grid>

              <Grid item xs={6}>
                <Typography fontWeight="bold">
                  Department
                </Typography>
                <Typography>
                  {selectedOperation.department}
                </Typography>
              </Grid>

              <Grid item xs={6}>
                <Typography fontWeight="bold">
                  Operation Type
                </Typography>
                <Typography>
                  {selectedOperation.operation_type}
                </Typography>
              </Grid>

              <Grid item xs={6}>
                <Typography fontWeight="bold">
                  Quantity
                </Typography>
                <Typography>
                  {selectedOperation.operation_quantity}
                </Typography>
              </Grid>

              <Grid item xs={6}>
                <Typography fontWeight="bold">
                  Priority
                </Typography>
                <Typography>
                  {selectedOperation.priority}
                </Typography>
              </Grid>

              <Grid item xs={6}>
                <Typography fontWeight="bold">
                  Status
                </Typography>
                <Typography>
                  {selectedOperation.business_status}
                </Typography>
              </Grid>

              <Grid item xs={12}>
                <Typography fontWeight="bold">
                  Description
                </Typography>
                <Typography>
                  {selectedOperation.description}
                </Typography>
              </Grid>

              <Grid item xs={12}>
                <Typography fontWeight="bold">
                  Created At
                </Typography>
                <Typography>
                  {selectedOperation.created_at}
                </Typography>
              </Grid>

            </Grid>

          )}

        </DialogContent>

        <DialogActions>

          <Button
            variant="contained"
            onClick={() => setDetailsOpen(false)}
          >
            Close
          </Button>

        </DialogActions>

      </Dialog>
    </MainLayout>
  );
}

export default OperationHub;