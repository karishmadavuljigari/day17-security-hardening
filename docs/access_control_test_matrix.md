\# Day 16 – Access Control Test Matrix



\## 1. Roles



| Role | Description |

|---|---|

| Anonymous | User is not logged in |

| Employee | Authenticated standard user |

| Admin | Authenticated administrator |



\## 2. Endpoint Access Matrix



| Endpoint | Anonymous | Employee | Admin |

|---|---|---|---|

| GET /register | Allow | Allow | Allow |

| GET /login | Allow | Allow | Allow |

| GET / | Redirect to login | Allow | Allow |

| POST /ask | Reject | Allow with valid CSRF | Allow with valid CSRF |

| POST /logout | Reject | Allow with valid CSRF | Allow with valid CSRF |

| GET /admin | 401 | 403 | 200 |

| GET /records/{record\_id} | 401 | Own record: 200 | Own record: 200 |



\## 3. Object-Level Ownership Matrix



The current application requires record ownership for both employees and admins.



| Authenticated role | Record relationship | Expected result |

|---|---|---|

| Employee | Own record | 200 OK |

| Employee | Another user's record | 404 Not Found |

| Employee | Nonexistent record | 404 Not Found |

| Admin | Own record | 200 OK |

| Admin | Another user's record | 404 Not Found |

| Admin | Nonexistent record | 404 Not Found |

| Anonymous | Any record | 401 Unauthorized |



\## 4. Security Test Evidence



| Security scenario | Expected behaviour | Test evidence |

|---|---|---|

| Anonymous homepage access | Redirect to login | `test\_homepage\_requires\_login` |

| Employee accesses admin endpoint | 403 Forbidden | `test\_employee\_cannot\_access\_admin\_endpoint` |

| Admin accesses admin endpoint | 200 OK | `test\_admin\_can\_access\_admin\_endpoint` |

| Anonymous record access | 401 Unauthorized | `test\_record\_endpoint\_requires\_login` |

| Employee accesses own record | 200 OK | `test\_users\_can\_only\_access\_their\_own\_records` |

| Employee accesses another user's record | 404 Not Found | `test\_users\_can\_only\_access\_their\_own\_records` |

| Admin accesses own record | 200 OK | `test\_admin\_can\_only\_access\_their\_own\_records` |

| Admin accesses another user's record | 404 Not Found | `test\_admin\_can\_only\_access\_their\_own\_records` |

| Admin accesses nonexistent record | 404 Not Found | `test\_admin\_can\_only\_access\_their\_own\_records` |

\## 5. Access Control Decisions



\- Authentication is checked before protected endpoint access.

\- Role checks are centralised in `src/auth/permissions.py`.

\- Record ownership is checked in `src/auth/ownership.py`.

\- The record query filters by both record ID and owner user ID.

\- Inaccessible records return 404 to avoid disclosing their existence.

\- Failed role checks and inaccessible record attempts are audited.



\## 6. Result Summary



Automated tests verify anonymous access, employee/admin role restrictions, and object-level ownership for both employees and admins.



The tests confirm:



\- Employees can access their own records but not other users' records.

\- Admins can access their own records but cannot bypass ownership checks.

\- Inaccessible and nonexistent records return the same 404 response.

\- Unauthenticated users receive 401 for protected record access.
