# Cross-application coverage modules

Select every module that applies. These are minimum probes, not feature requirements. Mark irrelevant states `not applicable` and unavailable checks `not run`.

## Universal web-interface module

- Purpose and primary action at first meaningful render
- Navigation, current location, addressability, back/forward, and reload
- Pointer, keyboard, focus, zoom/reflow, and small-screen operation
- Loading, empty, error, success, disabled, stale, and permission states that actually exist
- Feedback for every state-changing or asynchronous action
- Headings, landmarks, names, roles, relationships, live updates, and contrast
- Content specificity, terminology consistency, hierarchy, density, and identity
- Runtime performance when a trace is available
- Shared implementation blockers when source is available

## Reference, course, or documentation

- Find a known term and an unfamiliar term
- Resume after interruption
- Link/bookmark/share a specific unit
- Traverse sequentially and jump non-sequentially
- Reveal, quiz, transcript, print/export, media, and completion behavior when present
- Long-page readability and sparse-page composition

## SaaS dashboard or operations surface

- Identify the decision each summary supports
- Filter, sort, paginate, change scope, and clear state
- Empty, stale, partial, delayed, and contradictory data
- Drill down and return without losing context
- Role/permission differences and destructive-action confirmation
- Dense-table keyboard and responsive behavior

## Transactional, ecommerce, booking, or payment

- Search/browse → detail → selection → cart/booking → confirmation
- Price, fee, availability, inventory, and date changes
- Validation, retry, cancellation, duplicate submission, and idempotent feedback
- Authentication interruption and return to task
- Trust-critical copy and irreversible-action review

## Form, onboarding, settings, or account management

- Initial, partial, invalid, valid, saving, saved, and failed states
- Labels, help, errors, required/optional distinction, and review-before-submit
- Back/forward, draft persistence, abandonment, resume, and reset
- Conditional fields, progressive disclosure, permission requests, and defaults
- Keyboard order and focus movement after validation

## Data-heavy, analytic, or developer tool

- Query/input → running → partial → complete → failed → retry
- Large result sets, truncation, pagination/virtualization, export, and copy
- Filters and URL/state reproducibility
- Units, precision, time zones, provenance, freshness, and comparison baselines
- Dense keyboard interaction and non-color status encoding

## Collaboration, messaging, or realtime

- Create/edit/delete, optimistic state, conflict, reconnect, and duplicate events
- Read/unread, presence, ordering, timestamps, and notification control
- Permission and ownership changes
- Offline queue and reconciliation when applicable
- Dynamic announcements without focus theft

## Media, creative, canvas, or editor

- Load/import, edit, undo/redo, save/export, failure, and recovery
- Selection, focus, shortcuts, context menus, and direct manipulation
- Large-file or long-session behavior
- Playback/recording permission and capability states
- Unsaved work, autosave truthfulness, version history, and destructive reset

## Marketing, landing, or static content

- Audience/outcome clarity and primary conversion path
- Navigation, anchor/deep-link behavior, forms, and external destinations
- Content credibility, proof provenance, mobile reading, and reduced motion
- Image/media loading, layout stability, and print/share behavior when relevant
- Avoid inventing application-state requirements the page does not need

## Ceremonial, shared display, or physical print

- Classify each output as close-interaction, shared presentation, printed sign, or invitation-like artifact before applying size and density rules
- Record intended audience, physical or pixel size, likely viewing distance, orientation, lighting, trim, and safe area
- Preserve the subject or event identity as the dominant ceremonial layer without letting ornament obscure names, state, instructions, or participation cues
- Verify venue-screen and projector content at native presentation sizes; separate audience-facing content from operator-only chrome
- Verify printed output at intended paper dimensions, including trim, safe area, contrast, QR prominence, and legibility without editor zoom
- Stress short, long, compound, and localized names plus real event dates and venues; inspect line boxes against adjacent media and ornaments
- Check the handoff between ceremonial and operational surfaces: the gallery or sign may invite, while the upload, recovery, or setup flow must remain literal and task-efficient
- Treat unavailable physical-distance, lighting, printer, or device evidence as `not run`, never as a pass

## Hybrid or unknown product

Start with the universal module. Derive three to five tasks from visible behavior, supplied intent, and source structure. Add modules only when the interface exposes that application shape. Record uncertain classification as an inference and keep the coverage ledger explicit.
