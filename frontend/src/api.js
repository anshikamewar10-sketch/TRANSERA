const BASE_URL = "http://127.0.0.1:8000";

const api = {

    // Authentication

    login: `${BASE_URL}/auth/login`,

    // Operation Hub

    createOperation: `${BASE_URL}/operations/create`,

    getOperations: `${BASE_URL}/operations/all`,

    searchOperation: (keyword) =>
        `${BASE_URL}/operations/search/${keyword}`,

    operationDetails: (id) =>
        `${BASE_URL}/operations/details/${id}`,

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

    // Resource

    resourceHistory: `${BASE_URL}/resources/history`,

    // Deadlock

    deadlock: `${BASE_URL}/deadlock/check`

};

export default api;