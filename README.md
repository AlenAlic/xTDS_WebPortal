# NTDS_webportal
Version [0.7.0][CHANGELOG]

A web portal for registration and selection for the NTDS.

Based on Flask and Python


## Planned pages
- Publicly available
  - [x] Home
  - [x] Login
  - [x] General information on main site
  - [x] Password reset


- Logged in - General
  - [x] Profile page
    - [x] Change password


- Logged in - Teamcaptains
  - [x] Dashboard
  - [x] Enable treasurer in profile page
  - [x] Finances overview
  - [x] Registration period
    - [x] Register dancers
    - [x] Change dancer data (except name)
      - [x] Name change can be requested
      - [x] Cancel registration/Re-register
    - [x] Overview of couples
    - [x] Select who is the teamcaptain
    - [x] Request couples between teams
  - [ ] Raffle period
    - [ ] Overview of dancers with their status
      - [ ] Request for selected and confirmed dancers to de-register


- Logged in - Treasurer
  - [x] Dashboard
  - [x] Finances overview (see Logged in - Teamcaptains)


- Logged in - Organisation
  - [x] Dashboard
  - [x] Registration overview (total and per team)
  - [x] Name change requests
  - [x] Payments overview (per team and total)
  - [ ] Raffle pages
    - [ ] Raffle system
      - [ ] Export to BAD
    - [ ] Statistics
    - [ ] Requests for cancellations


- Logged in - Blind date support
  - [x] Dashboard
  - [ ] Registration page for blind date couples
  - [ ] Overview of available blind daters (name, team, id, per category) - Requires an extra password


## General features
Messagin system for users
  - [x] Send to specific (group of) users
  - [x] Read/Unread status
  - [x] Archive
  - [ ] Soft delete


[CHANGELOG]: ./CHANGELOG.md