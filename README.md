# Qwerty — Main and Recruitment Discord Bot

One Qwerty Discord application serves two servers with isolated responsibilities:

- The **main server** keeps Qwerty's established attendance, community, birthday, role, resource, and game features.
- The **recruitment server** receives a recruitment calendar, codeword attendance, anonymous questions, and a tracked path into the main server.

Slash commands are registered per server, not globally. Main-server members therefore do not see recruitment administration commands, and recruitment members do not see the legacy command set. Legacy `!` commands are also restricted to the configured main server.

## Recruitment commands

### Calendar

- `/calendar` — Show the next ten recruitment events
- `/calendar-add` — Add an event (staff)
- `/calendar-manage` — List events and their IDs (staff)
- `/calendar-remove` — Remove an event (staff)

### Recruitment information

- Qwerty creates or updates the introductions, rush schedule, and FAQ posts when it starts
- `/publish-recruitment-info` — Manually create or refresh all three posts (staff)

### PNM onboarding

- Members who receive the configured `PNM` role receive a private information form by DM
- Completed forms are posted automatically to the private PNM join log
- `/pnm-form-send` — Send or resend the form to one PNM (staff)
- `/pnm-form-send-all` — Resend the form to every PNM who has not completed it (staff)

### Attendance

- PNMs send an active codeword directly to Qwerty to check in
- `/attendance-code-add` — Open attendance and set a codeword (staff)
- `/attendance-code-list` — List active codewords (staff)
- `/attendance-code-remove` — Close an attendance event (staff)
- `/attendance-export` — Download all attendance records as CSV (staff)

Each recruitment-server member can check in only once per event. Main-server-only users cannot submit recruitment codewords.

### Anonymous questions

- `/ask-anonymously` — Forward a question to a private staff channel

The implementation does not log, save, or forward the submitter's identity. Qwerty necessarily receives the original Discord interaction in order to process it.

### Main-server transition

- `/transition-invite` — Send one member the main-server invite (staff)
- `/transition-invite-all` — Send invites to all members holding the configured source role (staff, explicit confirmation required)
- `/transition-status` — Show delivered, pending, joined, and failed totals (staff)

Discord requires every person to choose to join the main server. Qwerty does not copy or force-add accounts. It sends the invite, tracks delivery, notices a successful join, and attempts to assign the configured new-member role.

## Staff access

Recruitment staff commands allow members who have either Discord's **Manage Server** permission or the exact role configured by `RECRUITMENT_ADMIN_ROLE`.

See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for configuration and launch
instructions. The complete member, staff, and successor tutorial is in
[docs/COMMAND_TUTORIAL.md](docs/COMMAND_TUTORIAL.md).

Server-specific values are read from the ignored `server_config.json` file, using
`server_config.example.json` as its documented template. Environment variables
with the same names take precedence when deployed on a hosting platform.
