## Access levels 

POP implements a structured, **role-based access control (RBAC)** system combined with **project-based permissions**. Each user is assigned a global Access Level and may receive additional permissions within specific projects. These levels determine what actions a user can perform and what data they can access.

Each access level corresponds to a defined **Role** that governs what actions a user can perform and what types of data they can access.

| Access Level | Role | Description
|:-----:|:---------:|:-----------------|
| 0 | External | Limited, non-member access to basic, aggregated public data|
| 1 | Member | Registered user that can view data and can participate in projects|
| 2 | Project Manager | Manages research projects and project memberships |
| 3 | Platform Manager | Full operational control of the platform, except backend/system config |
| 4 | Administrator | Complete control, including platform configuration and system maintenance |

#### Level 0 - Externals

Users with minimal rights, typically external collaborators or new users pending access review.

*Permissions*:

- View basic aggregated database-wide statistics only.

By default, newly created users or users authenticated via SSO (Single Sign-On) for the first time are assigned to this role.
They can access the platform but have extremely limited permissions, primarily to view publicly aggregated statistics.

#### Level 1 - Members

Users who can browse anonymized data but cannot modify or export it.

*Permissions*:

- View anonymized patient case data, including audit trails.
- View research projects, cohort and their audit trails.
- Create and manage cohorts for ongoing projects where they are members

#### Level 2 - Project leaders

Leaders of individual research projects with authority over project scope and team members.

*Permissions*:

- Create and manage research projects.
- Manage project members and assign roles within their projects.
- Grant temporary data management rights (e.g., Data Contributor, Data Analyst) to project members.
- Export anonymized and pseudonymized data related to their projects.

!!! important "Compliance notice"

    As this role can access pseudonymized data, assignment to this role or higher should be restricted to authorized personnel such as clinicians or principal investigators.

#### Level 3 - Platform managers

Operational managers responsible for the oversight of platform usage and user management.

*Permissions*:

- Add, deactivate, or delete user accounts.
- Adjust access levels for any user.
- View platform-wide statistics and settings.

#### Level 4 - System administrators

Technical system administrators with unrestricted access. Server superusers are assigned this role automatically. 

*Permissions*:

- Full access to platform configuration, infrastructure, database management, and system maintenance.
- Manage application settings, environment variables, and integrations.
- Typically restricted to IT or DevOps teams.

## Permission enforcement

### API-Level Enforcement

At the core of POP’s security model is API-level permission enforcement. Every request to a protected API endpoint is evaluated against the current user’s Access Level.

**How it works:**

- Each API view or endpoint defines a required minimum access level (or specific permission) for interaction.
- When a user makes a request, their access level is verified via their authenticated session or token.
- If the access level is insufficient, the API responds with an HTTP `403 Forbidden` status code, indicating the user does not have permission to perform the requested action.

**Example:**

A *Member* (Level 1) attempting to access a pseudonymized data endpoint (Level 2+) will immediately receive a `403 Forbidden` response.

**Benefits:**

- Ensures security even if frontend protections are bypassed.
- Centralized enforcement simplifies auditing and maintenance.
- API permission checks are logged for traceability (if logging is enabled).

### Frontend-Level Enforcement

The Angular frontend complements backend security by proactively managing the user interface based on the logged-in user’s access level.

**Key behaviors:**

- UI elements (such as buttons, navigation links, export options) that require higher permissions are hidden or disabled for users without the necessary access.
- Route guards are implemented to prevent unauthorized users from accessing restricted views or pages.
- User notifications inform the user when an action is restricted, often explaining the required access level.

**Example:**

A *Member* (Level 1) will not see buttons to add new patient cases or export data.
Attempting to navigate directly to a restricted route via URL will redirect the user or show an access denied message.

**Benefits**:

- Improves user experience by removing unavailable options.
- Reduces accidental or unauthorized data access attempts.
- Aligns the visible UI with the user’s role-based permissions.