# 🛍️ Bazaar

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com) [![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org) [![Docker](https://img.shields.io/badge/Docker-20.10+-2496ED.svg)](https://www.docker.com)

**Bazaar** is an open-source, microservices-based e-commerce platform designed to give sellers freedom from centralized marketplaces. Built with **FastAPI**, **PostgreSQL**, and **React**, it offers a flexible, scalable, and vendor-neutral solution for online retail.

- **Flexible Product Model**: Supports any product type with dynamic EAV attributes — from clothing to electronics.
- **Microservices Architecture**: Independently scalable services for users, products, orders, payments, and notifications.
- **Event-Driven**: Asynchronous communication via Kafka for loose coupling and reliability.
- **Modern Stack**: FastAPI (Python), React + Tailwind CSS, PostgreSQL, Docker.

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/TemaDrakoshef/bazaar.git
cd bazaar

# Copy environment variables
cp .env.example .env

# Build and run all services with Docker Compose
docker compose up -d

# Access the application
# Frontend: http://localhost:3000
# API Gateway: http://localhost:8000
# API Docs: http://localhost:8000/docs