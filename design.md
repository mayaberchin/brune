# System Blueprint
## TNPG: brunes
## Project: 
## TARGET SHIP DATE: {yyyy-mm-dd} 

---
<div align="center">

## Roster

| Name           | Email                         | Primary Role    | Secondary Role |
|----------------|-------------------------------|-----------------|----------------|
| Maya Berchin   | mayab97@nycstudents.net       | Project Manager | Developer      |
| Megan Kwok     | megank21@nycstudents.net      | Developer       |                |
| Christine Chen | christinec109@nycstudents.net | Developer       |                |

</div>

---

## Summary
> Description here...

### Problem Being Solved
Text here...

### Target Users
- _________
- _________

### Why This Project Matters
Text here...

---

## Minimum Viable Product (MVP) Scope

### Core Features (Required for Final Submission)
Features that **must** be completed:
1. a
2. b
3. c

### Stretch Features (Only if MVP is Complete)
1. a
2. b
3. c

### Eplicit Non-Goals
Features intentionally **excluded**:
1. a
2. b
3. c

---

## Technology Stack

<div align="center>

| Layer              | Selected Tool  |
|--------------------|----------------|
| Backend Framework  | Flask          |
| Frontend Framework | Bootstrap      |
| Database           | SQLite         |
| Authentication     | Flask Sessions |
| ORM / DB Library   | SQLAlchemy (?) |

</div>

### Why This Stack Was Chosen
> Recap/summary here...

---

## Team Ownership Plan

<div align="center">
  
Each members meaningful deliverables
| Team Member    | Primary Ownership | Secondary Ownership | Specific Deliverables |
|----------------|-------------------|---------------------|-----------------------|
| Maya Berchin   |                   |                     |                       |
| Megan Kwok     |                   |                     |                       |
| Christine Chen |                   |                     |                       |

</div>

---

## Component Map

{Insert your mermaid(or equivalent)-generated diagram here}

## Site Map

{Insert your mermaid(or equivalent)-generated diagram here}
eg...
```
Landing Page
   ↓
Login / Register
   ↓
Dashboard
   ├── Feature A
   ├── Feature B
   └── Profile
```

---

## Key User Stories
### eg0
As a __________, I want to __________ so that...

### eg1
As a __________, I want to __________ so that...

### eg2
As a __________, I want to __________ so that...

---

## Database Design

### Database Type
**Relational**
> Explanation here...

### Tables

<div align="center">
  
_users_
| Variable Type | Variable Name | Variable Attribute(s)      |
|---------------|---------------|----------------------------|
| INTEGER       | user_id       | PRIMARY KEY AUTOINCREMENT  |
| TEXT          | email         | UNIQUE NOT NULL            |
| TEXT          | name          | NOT NULL                   |
| TEXT          | password_hash | NOT NULL                   |
| TEXT          | role          | NOT NULL DEFAULT 'student' |

<br>

_posts_
| Variable Type | Variable Name | Variable Attribute(s)                  |
|---------------|---------------|----------------------------------------|
| INTEGER       | post_id       | PRIMARY KEY AUTOINCREMENT              |
| INTEGER       | poster_id     | FOREIGN KEY references user_id         |
| INTEGER       | class_id      | FOREIGN KEY references class_id        |
| TEXT          | title         | NOT NULL                               |
| TEXT          | body          | NOT NULL                               |
| TEXT          | category      | NOT NULL (e.g. announcement, question) |
| TEXT          | status        | (e.g. open, closed)                    |
| TEXT          | created_at    | CURRENT_TIMESTAMP                      |
| TEXT          | updated_at    | CURRENT_TIMESTAMP                      |

<br>

_tablename_
| Variable Type | Variable Name | Variable Attribute(s) |
|---------------|---------------|-----------------------|
|               |               |                       |
|               |               |                       |
|               |               |                       |

</div>

---

## Testing Plan

{Delineate here your plan for testing each component}

---

## Timeline

### Week 1 Goals:

### Week 2 Goals:

### Week 3 Goals:

### Internal Deadlines:
{List milestones your team has identified, in the order they must be completed. Set a target completion date for each.}

---

## Completion Criteria (Definition of Done)
Project is considered **complete** when all of the following are true:
1. a
2. b
3. c

---

## Open Questions
{Delineate anything undecided here}

## Appendix
{Any relevant info that is useful but would have interrupted narrative flow above, or cluttered the information portrayed}

## Other
{Put here anything that did not sensibly fit under above headings. This section will inform evolution of SoftDev.}

---











# (OLD STUFF, MAYBE NEED, DELETE LATER!)

## PROGRAM COMPONENTS + EXPLANATION:

### Python Files
- `__init__.py`: the main file; serves app
- `data.py`: handles SQLite3 database 
- <TBA>:

### Templates
- `login.html`: the user will be directed onto the login page first. They will be redirected to the homepage once they are logged in (automatic if they are already logged in). If they don’t have an account, they can be redirected to register.
- `register.html`: the user will be able to register. They will be redirected to the homepage once they do this.
- `home.html`: the homepage, which <...>
- <TBA>:

### JS Files
- <TBA>:
---






