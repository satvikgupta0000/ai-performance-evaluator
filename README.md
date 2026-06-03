# 📊 AI-Based Employee Performance Evaluation System

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?logo=openai)
![AWS EC2](https://img.shields.io/badge/AWS-EC2-FF9900?logo=amazonaws)
![AWS RDS](https://img.shields.io/badge/AWS-RDS%20MySQL-FF9900?logo=amazonaws)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?logo=terraform)
![Ansible](https://img.shields.io/badge/Ansible-Automation-EE0000?logo=ansible)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?logo=githubactions)

An AI-driven employee performance appraisal system built with Python, Streamlit, and OpenAI GPT-4o. Employees log daily tasks, managers trigger evaluations, and the system generates data-driven band recommendations, AI-written feedback, and skill radar charts — all deployed on AWS using Terraform, Ansible, and Docker.

---

## 🖥️ Live Application Screenshots

### Manager Dashboard — Team Overview
> Managers see task summaries for their entire team with completion rates, quality scores, and last activity.

<img width="494" height="203" alt="image" src="https://github.com/user-attachments/assets/e1bac65e-5838-48fe-9a91-f682555ac6af" />
<img width="494" height="244" alt="image" src="https://github.com/user-attachments/assets/49fbd7ac-b366-485a-81ab-7e2cee32ebd0" />


### Manager Dashboard — Run Evaluation
> With one click, the manager triggers GPT-4o evaluation for all 4 team members. Results show band and composite score instantly.

<img width="494" height="178" alt="image" src="https://github.com/user-attachments/assets/54788e5c-d1b6-4892-8fe4-bf9a3e9a2d62" />


### Evaluation Results with AI Feedback
> Each employee gets a band (A/B/C/D), a composite score out of 100, and a 3-sentence AI-generated feedback paragraph.

<img width="494" height="282" alt="image" src="https://github.com/user-attachments/assets/5078c35c-49f7-4e1d-95ce-63aef91293ba" />


### Employee View — Task History
> Employees log daily tasks and view their recent task history with completion %, quality score, priority, and deadline.

<img width="583" height="262" alt="image" src="https://github.com/user-attachments/assets/e5f6979f-a03a-433b-a3bf-4551de2507ff" />
<img width="583" height="275" alt="image" src="https://github.com/user-attachments/assets/3ac10044-c61d-4c10-85fc-38040e2b42ae" />
<img width="583" height="271" alt="image" src="https://github.com/user-attachments/assets/30121cc9-dd47-476e-8d1c-d7105dbdc1df" />


### Employee View — Evaluation Pending
> Employees see their evaluation only after the manager publishes it. Until then they see a clean pending message.

<img width="494" height="228" alt="image" src="https://github.com/user-attachments/assets/8aee23b1-aa17-43a3-b8cf-6b014fe1718f" />


---

## 🏗️ System Architecture

```
Employee fills daily task form
            ↓
    Amazon RDS (MySQL)          ← stores all task rows
            ↓
Manager triggers evaluation
  OR March 15 scheduled cron
            ↓
  Aggregation → Scorer          ← deterministic band logic (no AI)
            ↓
       GPT-4o API               ← generates feedback paragraph only
            ↓
  Results saved to RDS
            ↓
  HR publishes results
            ↓
  Employee sees band + radar chart + feedback
```

---

## 👥 User Roles

| Role | Permissions |
|---|---|
| **Employee** | Log daily tasks, view own published evaluation |
| **Manager** | View team task summary, trigger team evaluation, view all team results |
| **HR** | View company-wide data, publish / unpublish evaluation results |

> Managers can only see and evaluate **their own team**. HR cannot trigger evaluations — only managers can.

---

## 🧠 How Evaluation Works

### Step 1 — Metrics aggregated from daily tasks (5 dimensions)

| Dimension | Derived From |
|---|---|
| Task Completion | avg completion % across all tasks |
| Deadline Adherence | % of completed tasks delivered on time |
| Priority Management | completion % on high-priority tasks (priority ≥ 4) |
| Work Quality | avg quality score (1–10) normalized to 0–100 |
| Productivity | tasks per working day, capped at 100 |

### Step 2 — Deterministic band assignment (no AI involved)

```python
composite = (task_completion × 0.25) + (deadline_adherence × 0.25) +
            (priority_management × 0.20) + (work_quality × 0.20) +
            (productivity × 0.10)

A → composite ≥ 85   (Exceeds Expectations)
B → composite ≥ 70   (Meets Expectations)
C → composite ≥ 55   (Partially Meets)
D → composite < 55   (Below Expectations)
```

### Step 3 — GPT-4o generates feedback paragraph only

The band is always deterministic. GPT-4o only writes the 3-sentence narrative — keeping evaluation **consistent and unbiased** regardless of AI variability.

### Scheduled Annual Evaluation

APScheduler automatically triggers evaluation for all teams at **midnight IST on March 15 every year**. Skips employees already evaluated for that year (idempotent).

---

## 🗄️ Database Schema (MySQL on Amazon RDS)

```
departments    → id, name
roles          → id, name (employee / manager / hr)
users          → id, name, email, password_hash, role_id, department_id, manager_id
daily_tasks    → id, employee_id, task_date, task_name, priority, status,
                 completion_pct, quality_score, deadline, notes
evaluations    → id, employee_id, year, band, composite_score, ai_feedback,
                 radar_scores (JSON), published, triggered_by
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI Backend | OpenAI GPT-4o |
| Database | Amazon RDS (MySQL 8.0) |
| Server | AWS EC2 (t2.micro) |
| Containerization | Docker + Docker Compose |
| Reverse Proxy | Nginx |
| Infrastructure as Code | Terraform |
| Configuration Management | Ansible |
| CI/CD | GitHub Actions |
| Monitoring | AWS CloudWatch + SNS alerts |
| Scheduler | APScheduler |

---

## 📁 Project Structure

```
ai-performance-evaluator/
├── app/
│   ├── main.py                  ← Streamlit router (login → role-based view)
│   ├── scheduler.py             ← APScheduler March 15 annual evaluation
│   ├── views/
│   │   ├── employee_view.py     ← Task form + own results
│   │   ├── manager_view.py      ← Team overview + trigger evaluation
│   │   └── hr_view.py           ← All employees + publish results
│   └── core/
│       ├── auth.py              ← Login, session, bcrypt password hashing
│       ├── db.py                ← SQLAlchemy RDS connection pool
│       ├── parser.py            ← Aggregate daily_tasks → 5 metric scores
│       ├── scorer.py            ← Deterministic band logic
│       ├── evaluator.py         ← GPT-4o API call + save to RDS
│       ├── prompt_builder.py    ← Per-employee prompt template
│       └── charts.py            ← Plotly radar chart
├── db/
│   ├── schema.sql               ← MySQL CREATE TABLE statements
│   └── seed.py                  ← Seeds 2 HR + 5 managers + 20 employees + 600 task rows
├── infra/
│   ├── terraform/
│   │   ├── main.tf              ← EC2, RDS, VPC, IAM, Security Groups, CloudWatch
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── ansible/
│       ├── playbook.yml         ← Install Docker, deploy app, run migrations
│       └── inventory.ini        ← EC2 host configuration
├── tests/
│   ├── test_scorer.py           ← Unit tests for band logic
│   └── test_parser.py           ← Unit tests for metric computation
├── .github/workflows/
│   └── deploy.yml               ← GitHub Actions CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
└── requirements.txt
```

---

## 🚀 Deployment Guide

### Prerequisites
- AWS account (free tier)
- Terraform installed
- Ansible installed (Linux/WSL)
- OpenAI API key
- Python 3.11+

### Step 1 — Provision AWS infrastructure with Terraform

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# fill in your values: key_pair_name, db_password, alert_email
terraform init
terraform apply
# saves EC2 public IP and RDS endpoint as outputs
```

### Step 2 — Configure and deploy with Ansible

```bash
cd infra/ansible
# create vars.yml with your RDS endpoint, DB credentials, OpenAI key
ansible-playbook -i inventory.ini playbook.yml
```

Ansible will automatically:
- Install Docker from official repository
- Clone this repo onto EC2
- Write `.env` with credentials
- Build and start Docker containers
- Run `schema.sql` and `seed.py`

### Step 3 — Access the app

```
http://YOUR_EC2_PUBLIC_IP
```

### CI/CD — Every push to `main` auto-deploys

Add these secrets to GitHub → Settings → Secrets:

| Secret | Value |
|---|---|
| `EC2_HOST` | EC2 public IP |
| `EC2_SSH_KEY` | Contents of `.pem` file |
| `DB_HOST` | RDS endpoint |
| `DB_NAME` | perfeval |
| `DB_USER` | perfadmin |
| `DB_PASSWORD` | your password |
| `OPENAI_API_KEY` | sk-... |
| `APP_REPO_URL` | this repo URL |

---

## 🔐 Default Credentials (seed data)

| Role | Email | Password |
|---|---|---|
| HR | priya.sharma@company.com | Password@123 |
| HR | rahul.verma@company.com | Password@123 |
| Manager (Engineering) | arun.kumar@company.com | Password@123 |
| Manager (Product) | sneha.patel@company.com | Password@123 |
| Manager (Design) | vikram.singh@company.com | Password@123 |
| Manager (QA) | ananya.gupta@company.com | Password@123 |
| Manager (Operations) | rohit.mehta@company.com | Password@123 |
| Employee | arjun.nair@company.com | Password@123 |

> All 20 employees follow the same pattern: `firstname.lastname@company.com` / `Password@123`

---

## ☁️ AWS Infrastructure (Free Tier)

| Resource | Type | Purpose |
|---|---|---|
| EC2 | t2.micro | Runs Docker + Streamlit app |
| RDS | db.t3.micro MySQL 8.0 | Stores all application data |
| VPC | Custom | Isolated network with public/private subnets |
| IAM Role | EC2 Instance Profile | CloudWatch access (no hardcoded keys) |
| Security Groups | EC2 (22, 80) / RDS (3306 from EC2 only) | Least-privilege access |
| CloudWatch | Metric Alarm | CPU > 80% triggers SNS email alert |
| SNS | Email subscription | Alert notifications |

---

## 🧪 Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

Tests cover deterministic scoring logic and metric computation — no database or API calls required.

---

