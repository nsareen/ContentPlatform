
Epic 1: Tenant Onboarding & Management
ID	Story	Acceptance Criteria
US-T1	Create Tenant
As an Admin, I want to create a new Tenant (brand workspace) via the UI or API so that each brand’s data is isolated.	1. Given I’m authenticated as an Admin
When I submit a valid POST /tenants payload (name, config)
Then response is 201 Created with tenant_id and default settings.
2. Given required fields are missing or invalid
When I submit the same request
Then response is 400 Bad Request with field-level error messages.
3. Given a tenant with that name already exists
When I submit creation
Then response is 409 Conflict.
US-T2	Assign Roles
As an Admin, I want to assign roles (Business User, Content Specialist) to users within a Tenant so that permissions are enforced.	1. Given I’m Admin of Tenant X
When I call POST /tenants/{X}/users/{userId}/roles with a valid role list
Then the user’s roles are updated and I receive 200 OK.
2. Given I specify an invalid role name
When I call the same endpoint
Then response is 400 Bad Request with “Invalid role” error.
3. Given I’m not admin
When I call that endpoint
Then response is 403 Forbidden.
US-T3	List Tenants
As an Admin, I want to view all Tenants and their status (Active/Deactivated) so that I can manage onboarding and retirements.	1. Given I’m authenticated as a global Admin
When I call GET /tenants
Then I receive 200 OK with a list of tenants, each with id, name, status.
2. Given there are no tenants
When I call the same endpoint
Then I receive an empty array ([]).

Epic 2: Brand Voice Creation & Lifecycle
ID	Story	Acceptance Criteria
US-BV1a	Upload Corpus (Text)
As a Business User, I want to paste up to 500 words of brand content into a text area so the system can analyze it.	1. Given I’m on the “Create Brand Voice” screen
When I paste ≤500 words and hit “Analyze”
Then I see a loading indicator and later the generated voice draft (name, description, Do’s & Don’ts).
2. Given I exceed 500 words
When I paste and hit “Analyze”
Then I see a client-side validation error: “Max 500 words allowed.”
US-BV1b	Upload Corpus (File)
As a Business User, I want to upload an Excel/CSV (≤10 MB) containing brand guidelines so the system can reverse-engineer my voice.	1. Given a valid Excel/CSV ≤10 MB
When I upload and click “Analyze”
Then the draft Brand Voice appears.
2. Given a file >10 MB or wrong format
When I upload
Then I see “File must be Excel or CSV ≤ 10 MB.”
US-BV2	Manual Guidelines
As a Business User, I want to enter Do’s & Don’ts manually so that the AI can incorporate precise brand rules.	1. Given I’m editing a draft voice
When I fill Do’s & Don’ts and hit “Save Guidelines”
Then the draft updates and displays my entries.
2. Given I leave both fields blank
When I save
Then I see “Please provide at least one guideline.”
US-BV3	Preview & Edit Draft
As a Business User, I want to preview the generated voice (name, description, personality, tonality) and edit fields inline before publishing.	1. Given a generated draft exists
When I navigate to “Preview” tab
Then I see all attributes editable in-place.
2. Given I change a field
When I click “Save Draft”
Then the UI shows “Draft saved” and edits persist.
US-BV4	Publish Voice
As a Business User, I want to publish my voice draft so it becomes available to tasks in all downstream workflows.	1. Given I’m on a draft voice
When I click “Publish”
Then voice status → “Published”; timestamp and publishedBy are recorded.
2. Given draft has missing mandatory fields (e.g., no name)
When I publish
Then I see “Please complete all required fields.”
US-BV5	Version History
As a Business User, I want to view past versions and restore one so I can roll back if needed.	1. Given a voice has ≥1 previous version
When I open “History”
Then I see a list of versions with date, author, and a “Restore” action.
2. Given I click “Restore” on version Vn
When I confirm
Then Vn becomes the active draft and UI shows “Version restored.”
US-BV6	Deactivate Voice
As a Business User, I want to deactivate an old voice so it no longer appears in new task dropdowns.	1. Given a voice is “Published”
When I click “Deactivate”
Then status → “Inactive,” and in API GET /voices?status=active it no longer appears.
2. Given I try to use an inactive voice in a new task
When I submit
Then I get 400 Bad Request “Voice is inactive.”

Epic 3: Content Project & Schema Definition
ID	Story	Acceptance Criteria
US-CP1	Define Project Schema
As a Business User, I want to upload/enter a JSON or CSV schema so that batch imports validate automatically.	1. Given a valid JSON Schema or CSV header row
When I upload and click “Save”
Then schema persists, and import-preview shows sample of how data will map.
2. Given an invalid schema
When I save
Then I see field-level errors with line numbers.
US-CP2	Link Brand Voice
As a Business User, I want to select a Brand Voice for my project so that all tasks default to that voice.	1. Given at least one Published voice exists
When I open project settings
Then I see a dropdown of active voices.
2. Given I select Voice A and save
When I create tasks
Then their payload includes voice_id = A.
US-CP3	Fetch Schema via API
As an API Consumer, I want GET /projects/{id}/schema so I can validate my own batch payloads client-side.	1. Given Project X exists with a schema
When I call the endpoint
Then I get 200 OK with the full JSON schema or CSV template.
2. Given Project X does not exist
When I call the same endpoint
Then I get 404 Not Found.

Epic 4: Workflow Task Management
ID	Story	Acceptance Criteria
US-WM1	Create Translate Task
As a Content Specialist, I want to create a “Translate” task by providing text or file so that localization can begin.	1. Given I’m on a project with linked voice
When I click “New Task” → Choose “Translate,” supply text/file, then “Create”
Then I get 201 Created with task_id and status=Open.
2. Given no text/file provided
When I submit
Then client-side prevents submission with “Input required.”
US-WM2	Assign & Due Date
As a Content Specialist, I want to assign a task to a user or team with a due date so responsibilities are clear.	1. Given task T1 is Open
When I select assignee and due date and click “Assign”
Then task metadata updates, and assignee receives notification.
2. Given due date is in the past
When I assign
Then I see “Due date must be ≥ today.”
US-WM3	Update Task Status
As a Content Specialist, I want to move a task through statuses (Open → In-Progress → Review → Closed) so I can track progress.	1. Given a task is Open
When I click “Start”
Then status → In-Progress.
2. Given In-Progress
When I click “Submit for Review”
Then status → Review.
3. Given Review
When I click “Close”
Then status → Closed, and close timestamp is set.
US-WM4	Batch Grouping
As a Content Specialist, I want to group multiple tasks into a Batch so I can bulk-assign or bulk-close workflows.	1. Given I select ≥2 tasks
When I click “Create Batch”
Then a new Batch appears listing those tasks.
2. Given a Batch exists
When I bulk-close it
Then all included tasks transition to Closed.

Epic 5: Brand-Aware Translation API
ID	Story	Acceptance Criteria
US-API1	POST /translate
As an API Consumer, I want to send { text, voice_id } to get a brand-aligned translation so I can integrate with my CMS.	1. Given valid text and active voice_id
When I call the endpoint
Then I get 200 OK with { translatedText }.
2. Given invalid/missing fields
When I call it
Then I get 400 Bad Request with schema validation errors.
3. Given voice_id is inactive
When I call
Then I get 400 “Voice is inactive.”.
US-API2	Schema Validation Errors
As an API Consumer, I want clear error messages when my payload does not match the project schema so I can correct and retry.	1. Given input payload missing required keys
When I POST
Then I get 422 Unprocessable Entity with field-specific messages.
2. Given a string value where number expected
When I send it
Then response details the mismatch.

Epic 6: Explainability & Feedback
ID	Story	Acceptance Criteria
US-EX1	Explain Panel
As a Content Specialist, I want to see which prompt fragments and tokens influenced the output so I understand the AI’s rationale.	1. Given I’ve just viewed a task’s result
When I click “Explain”
Then I see a panel with prompt text, model version, and token-level highlights or attention weights.
2. Given no explanation data (e.g. model doesn’t support it)
When I click “Explain”
Then I see “Not available for this model.”
US-EX2	Submit Feedback
As a Content Specialist, I want to rate each output (1–5) and leave comments so the system can learn and improve its prompts.	1. Given I’m on a completed task in Review status
When I select rating and add a comment, then click “Submit Feedback”
Then feedback persists and status changes to Closed.
2. Given no rating selected
When I submit
Then I see “Please rate before submitting.”

Epic 7: UI Theming & Dynamic Design System
ID	Story	Acceptance Criteria
US-UI1	Select Theme
As a Business User, I want to choose from pre-built UI themes (colors, fonts, layouts) so the app matches my brand identity.	1. Given I’m in Tenant settings
When I open “Themes”
Then I see a gallery of theme thumbnails.
2. Given I click “Apply” on Theme A
When I reload any page
Then UI reflects Theme A’s colors/fonts.
US-UI2	Preview Theme
As a Business User, I want to preview a theme in a sandbox before applying so I can verify readability and style.	1. Given I hover over Theme B
When I click “Preview”
Then the current screen updates to show Theme B without saving.
2. Given the preview shows poor contrast
When I decide not to apply and click “Revert”
Then the UI returns to the previously applied theme.
6. Updated User Stories

Epic: Navigation & Layout

US-N1: As a Business User, I want to click “My Desk” in the sidebar so I can see a quick start panel for creating a new Brand Voice.

US-N2: As a Business User, I want distinct sidebar items (Projects, My Assignments) so I can navigate between main areas of the application.

Epic: Voice Library Enhancements

US-L1: As a Business User, I want a toggle to switch between grid and list layouts for Brand Voices so I can view details or thumbnails as needed.

US-L2: As a Business User, I want to search Brand Voices by name using a search input so I can quickly find a specific voice.

US-L3: As a Business User, I want to sort Brand Voices by columns (Name, Tone, Version, Status) so I can organize the list.

US-L4: As a Business User, I want to filter Brand Voices by their status (Draft, Published, Under Review) using a Filters dropdown, so I can focus on relevant voices.

Epic: Contextual Actions

US-A1: As a Business User, I want an overflow menu (⋯) on each voice item so I can access actions like Edit, Clone, Delete or Publish.

US-A2: As a Business User, I want the action menu icons to reflect available status transitions, e.g. Publish for Draft voices.

Epic: My Assignments Dashboard

US-T1: As a Content Specialist, I want to view the “My Assignments” tab with a count badge, so I know how many tasks are pending.

US-T2: As a Content Specialist, I want to see a list of my tasks (title, due date, status) so I can pick up work directly from my dashboard.

6. Updated User Stories

Epic: Navigation & Layout

US-N1: As a Business User, I want to click “My Desk” in the sidebar so I can see a quick start panel for creating a new Brand Voice.

US-N2: As a Business User, I want distinct sidebar items (Projects, My Assignments) so I can navigate between main areas of the application.

Epic: Voice Library Enhancements

US-L1: As a Business User, I want a toggle to switch between grid and list layouts for Brand Voices so I can view details or thumbnails as needed.

US-L2: As a Business User, I want to search Brand Voices by name using a search input so I can quickly find a specific voice.

US-L3: As a Business User, I want to sort Brand Voices by columns (Name, Tone, Version, Status) so I can organize the list.

US-L4: As a Business User, I want to filter Brand Voices by their status (Draft, Published, Under Review) using a Filters dropdown, so I can focus on relevant voices.

Epic: Contextual Actions

US-A1: As a Business User, I want an overflow menu (⋯) on each voice item so I can access actions like Edit, Clone, Delete or Publish.

US-A2: As a Business User, I want the action menu icons to reflect available status transitions, e.g. Publish for Draft voices.

Epic: My Assignments Dashboard

US-T1: As a Content Specialist, I want to view the “My Assignments” tab with a count badge, so I know how many tasks are pending.

US-T2: As a Content Specialist, I want to see a list of my tasks (title, due date, status) so I can pick up work directly from my dashboard.