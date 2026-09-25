# Semester 11

Eleventh-semester coursework and Obsidian vault.

| Course | Folder |
| --- | --- |
| Проблеми багатозначного аналізу | [multivalued-analysis](./multivalued-analysis/) |
| Numerical modelling techniques (ТЧМ) | [numerical-modelling-techniques](./numerical-modelling-techniques/) |
| _(add more courses here as the schedule is confirmed)_ | |

## Obsidian vault

This folder is also an Obsidian vault. Open it via **File → Open folder as vault**
and point Obsidian at `11-sem/`.

### Layout

- `Tasks/Kanban.md` — kanban board for tasks and research (To Do / In Progress / Done).
- `Subjects/` — one note per course: book sources + notes. Copy
  `Templates/Subject Template.md` into `Subjects/<Course Name>.md` for each
  new course.
- `Templates/` — note templates.

### One-time setup

The **Kanban** plugin (by mgmeyers) is required for `Tasks/Kanban.md` to
render as a board. It's already marked enabled in
`.obsidian/community-plugins.json`, but Obsidian still needs to download it
once:

1. Settings → Community plugins → Browse.
2. Search "Kanban", install, then enable it.
3. Reopen `Tasks/Kanban.md` — it should now open as a board view (right-click
   the tab → "Open as kanban board" if it opens as plain markdown first).
