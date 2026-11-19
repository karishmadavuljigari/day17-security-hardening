\# IDOR Attempt Log — Day 16 Authentication Project



\## 1. Purpose



This log documents object-level authorization checks and IDOR-related attempts recorded by the application's audit system.



The application verifies record ownership before returning private record data.



\## 2. Audit Evidence



The `audit\_events` table was queried for events where `event\_type = 'IDOR\_ATTEMPT'`.



\*\*Total recorded events: 8\*\*



| Audit ID | User ID | Requested Record ID | Timestamp |

|---:|---:|---:|---|

| 17 | 1 | 2 | 2026-11-18 11:16:07 |

| 18 | 2 | 1 | 2026-11-18 11:16:07 |

| 89 | 32 | 4 | 2026-11-18 11:46:29 |

| 112 | 42 | 6 | 2026-11-18 12:08:22 |

| 157 | 59 | 8 | 2026-11-18 12:12:01 |

| 204 | 76 | 10 | 2026-11-18 12:15:45 |

| 211 | 79 | 12 | 2026-11-18 12:15:46 |

| 212 | 79 | 999999999 | 2026-11-18 12:15:46 |



These entries are audit records generated during application testing. They should not all be interpreted as independent malicious attacks.



\## 3. Authorization Behavior



The application uses an ownership-filtered database query:



\- A user can retrieve their own record.

\- A user cannot retrieve another user's record.

\- Admin role does not bypass record ownership.

\- Inaccessible and nonexistent records both return HTTP 404.

\- Unauthenticated users receive HTTP 401.



\## 4. Test Evidence



The following automated tests verify the behavior:



\- `test\_users\_can\_only\_access\_their\_own\_records`

\- `test\_admin\_can\_only\_access\_their\_own\_records`

\- `test\_record\_endpoint\_requires\_login`



The tests verify that unauthorized record content is not disclosed and that IDOR attempts are recorded.



\## 5. Logging Design



When a requested record cannot be found under the authenticated user's ownership, the application records:



\- Event type: `IDOR\_ATTEMPT`

\- User ID

\- Requested record ID

\- Event timestamp



The audit log does not store the private record content, password, password hash, or session token.



\## 6. Conclusion



The application enforces object-level ownership checks for both employee and admin users. Attempts to access records outside the user's ownership are denied and logged. Returning the same 404 response for inaccessible and nonexistent records avoids revealing whether another user's record exists.
