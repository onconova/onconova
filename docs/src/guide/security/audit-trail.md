Onconova provides a transparent and robust auditing system to track all changes to clinical and research data within the platform. This ensures traceability, accountability, and data integrity, crucial for compliance in sensitive healthcare and research environments.

## How Events are Tracked

### Data Changes
Every operation performed on a data resource, whether a **create**, **update**, or **delete**, is automatically logged at the database level using **PostgreSQL triggers**.

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

Onconova also registers a detailed audit log entry each time data is exported from the platform.

This includes:

- The timestamp of the export.
- The user who initiated the export.
- A list of datapoints or cases included in the export.
- Other metadata required to recreate the exported dataset 

This ensures traceability of how and when sensitive data leaves the system, a key requirement for most clinical research data governance frameworks.


### Public Audit Trail Access

One of Onconova’s key transparency features is that the audit trail is **publicly accessible to all authenticated platform users** irrespective of access level.

This means that:

- Any user can view the full audit history of any data resource.
- Data changes, exports, and user actions can be inspected at any time.

This fosters trust, ensures accountability, and allows for transparent collaboration within and between institutions.


## Server Access Logs

In addition to database-level auditing, Onconova maintains traditional server logs capturing every connection attempt to the Onconova server in a format that is both **GDPR** and **HIPAA** aligned. All HTTP requests are recorded in a `logfile.log` file in `logFmt` format containing the following data points:

| Field             | Description                                         | Example                               |
|------------------|-----------------------------------------------------|----------------------------------------|
| `timestamp`      | Timestamp of the request in ISO format              | `2025-07-16T14:22:09+0000`             |
| `level`          | Log level                                           | `INFO`                                 |
| `user.username`  | Authenticated user ID or `"anonymous"`              | `"e13ea837-ada4-4ba0"`                 |
| `user.id`        | Authenticated username or `"anonymous"`             | `johnsm`                               |
| `user.level`     | Authenticated user access level                     | `3`                                    |
| `request.ip`     | Source IP address                                   | `"192.168.1.5"`                        |
| `request.agent`  | User agent of the request                           | `"Mozilla/5.0 "`                       |
| `request.method` | HTTP method used                                    | `POST`                                 |
| `request.path`   | Full request path                                   | `"/api/auth/sessions"`                 |
| `request.data`   | Query or redacted JSON body data (gzip-compressed and base64-encoded)| `KaWd2gC/6tWSk4sTvVMUbJSSrK0t...`|
| `response.status`| HTTP response status code                           | `201`                                  |
| `response.duration`| Total response time in milliseconds               | `87`                                   |
| `response.data`   | Redacted JSON response (gzip-compressed and base64-encoded)| `LzE1VslJKSi1PtTA0UdJRysnMzSw...`|


These logs can typically be managed through Docker volumes or the container’s logging subsystem and can be integrated with external log management or security tools for extended auditing.

!!! warning "Security Notes"

    - Sensitive fields like password, token, and secret are automatically redacted.
    - Log files should be protected with file permissions (e.g., `chmod 600`).
    - For production, ensure logs are encrypted and immutable where required.

