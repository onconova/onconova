The Precision Oncology Platform (POP) provides a transparent and robust auditing system to track all changes to clinical and research data within the platform. This ensures traceability, accountability, and data integrity — crucial for compliance in sensitive healthcare and research environments.

## How Events are Tracked

### Data Changes
Ever
y operation performed on a data resource — whether a **create**, **update**, or **delete** — is automatically logged at the database level using **PostgreSQL triggers**.

Whenever a change occurs:

- A new audit log entry is created in a dedicated audit table.

The log records:

- The timestamp of the operation.
- The user responsible for the change.
- The type of operation performed.
- The state of the affected data.
- Other metadata

#### Data Diffs and Rollbacks

For every audited data change:

- A *differential* can be generated showing the precise modifications made.
- **Rollback functionality** allows authorized users to revert a data resource to a previous state based on the recorded audit history.

This makes it easy to trace errors, reverse unauthorized changes, or review the evolution of a particular data record over time.

### Data Exports

POP also registers a detailed audit log entry each time data is exported from the platform.

This includes:

- The timestamp of the export.
- The user who initiated the export.
- A list of datapoints or cases included in the export.
- Other metadata requuired to recreate the exported dataset 

This ensures traceability of how and when sensitive data leaves the system — a key requirement for most clinical research data governance frameworks.


### Server Access Logs (Optional)

In addition to database-level auditing, POP can be configured to maintain traditional server logs capturing:

Every connection attempt to the server.

- The originating IP address.
- The associated authenticated user identity.

This is typically managed through the web server or Docker container’s logging subsystem and can be integrated with external log management or security tools for extended auditing.

## Public Audit Trail Access

One of POP’s key transparency features is that the audit trail is **publicly accessible to all authenticated platform users** irrespective of access level.

This means that:

- Any user can view the full audit history of any data resource.
- Data changes, exports, and user actions can be inspected at any time.

This fosters trust, ensures accountability, and allows for transparent collaboration within and between institutions.
