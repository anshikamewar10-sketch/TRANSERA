
const BASE_URL = "http://127.0.0.1:8000";

const api = {
  // Authentication
  login: `${BASE_URL}/auth/login`,

  // Operation Hub
  createOperation: `${BASE_URL}/operations/create`,
  getOperations: `${BASE_URL}/operations/all`,
  searchOperation: (keyword) =>
    `${BASE_URL}/operations/search/${encodeURIComponent(keyword)}`,
  operationDetails: (id) =>
    `${BASE_URL}/operations/details/${encodeURIComponent(id)}`,

  // Simulation
  simulation: `${BASE_URL}/simulation/start`,

  // Scheduler
  fcfs: `${BASE_URL}/scheduler/fcfs`,
  runProcess: (processId) =>
    `${BASE_URL}/scheduler/run/${processId}`,
  completeBurst: (processId) =>
    `${BASE_URL}/scheduler/complete-burst/${processId}`,
  sjf: `${BASE_URL}/scheduler/sjf`,
  priority: `${BASE_URL}/scheduler/priority`,
  roundRobin: `${BASE_URL}/scheduler/round-robin`,
  completeQuantum: (processId, duration) =>
  `${BASE_URL}/scheduler/complete-quantum/${processId}?duration=${duration}`,

  // Feature 4 - Resource Allocation
  allocateResources: `${BASE_URL}/resources/allocate`,
  resourceHistory: `${BASE_URL}/resources/history`,
  releaseResources: (processId) =>
    `${BASE_URL}/resources/release/${processId}`,

  // Feature 5 - Deadlock
  deadlock: `${BASE_URL}/deadlock/check`,
  detectDeadlock: `${BASE_URL}/deadlock/detect`,
  resolveDeadlock: `${BASE_URL}/deadlock/recover`,
  resumeProcess: (processId) =>
    `${BASE_URL}/deadlock/resume/${processId}`,

  // Feature 6 - Transaction Center

executeTransactions: `${BASE_URL}/transactions/execute`,

transactionHistory: `${BASE_URL}/transactions/history`,


// Feature 7 - Analytics

analyticsDashboard: `${BASE_URL}/analytics/dashboard`,
};

export default api;
