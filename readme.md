# TRANSERA
### Business Execution & System Operations Console

TRANSERA is a full-stack application that integrates **Operating System concepts and Database Management System principles** into a unified business operations platform.

The system demonstrates how business operations are converted into processes, scheduled for CPU execution, allocated resources, checked for deadlocks, and processed through Oracle database transactions.

It also provides an analytics dashboard that displays system performance, resource utilization, transaction reliability, and database integrity.

## Technology Stack

**Frontend**
- React.js
- Material UI
- Recharts
- JavaScript

**Backend**
- Python
- FastAPI
- REST APIs

**Database**
- Oracle Database
- SQL
- Database constraints, joins, views, and transaction management

## Key Features

### 1. Operation Hub
Creates and manages business operations, including inventory receipts, sales orders, purchase orders, and other business activities.

### 2. Simulation Engine
Converts pending business operations into operating-system processes and generates process resource requirements.

### 3. Execution Scheduler
Implements four CPU scheduling algorithms:
- First Come First Serve (FCFS)
- Shortest Job First (SJF)
- Priority Scheduling
- Round Robin

Displays process execution, READY queues, CPU progress, and scheduling timelines.

### 4. Resource Allocation Center
Manages resource allocation, available resource instances, waiting processes, and allocation history.

### 5. Deadlock Detection & Recovery
Detects deadlocked processes, supports recovery, releases resources, and allows waiting processes to retry allocation.

### 6. Transaction Center
Executes Oracle database transactions for eligible completed business operations.

Supports:
- Inventory Receipt
- Sales Order
- Inventory Audit
- COMMIT and ROLLBACK
- Transaction history and audit logs

### 7. Analytics & Insights
Provides Oracle SQL-based analytics covering:
- Business operation completion
- Process completion
- Resource utilization
- Transaction reliability
- Database integrity
- System activity

## Application Workflow

Operation Hub → Simulation Engine → Execution Scheduler → Resource Allocation → Deadlock Detection & Recovery → Transaction Center → Analytics & Insights

## Database Design

TRANSERA uses Oracle tables for business operations, processes, resources, allocations, transactions, inventory, and system activity.

The database includes primary keys, foreign keys, transaction records, and analytical SQL views.

## Running the Project

### Backend

Install the dependencies from `requirements.txt`, configure the Oracle connection, and start the FastAPI server:

```bash
uvicorn main:app --reload
```

API documentation is available at:

`http://127.0.0.1:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs locally using the Vite development server.

## Project Purpose

TRANSERA was developed as an academic project to demonstrate the practical integration of Operating System and DBMS concepts through a full-stack application.

## Future Improvements

- Expanded scheduling performance analytics
- Enhanced database reporting
- Additional business transaction types
- Deployment and multi-user support
