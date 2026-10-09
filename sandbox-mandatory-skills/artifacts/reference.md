# Command reference

Every command of `scripts/artifact.py`, and how roles and sharing work. The flow
(when to make an artifact, the working folder, editing in place) is in `SKILL.md`.

## How to use it

The script lives beside this file, at `scripts/artifact.py`. The examples below assume
you are in this skill's directory; from anywhere else, give the full path. `<workdir>`
stands for the absolute path `workdir` printed, written out in full.

```bash
# The person referred to an artifact: a link, an id or a name. Always first.
python3 scripts/artifact.py resolve "https://…/artifacts/<artifact_id>"
python3 scripts/artifact.py resolve "informe de ventas"
# They alluded to one ("el de ayer"): what this project touched, last first
python3 scripts/artifact.py recent --page-size 10

# The artifact's working folder, under $ARTIFACT_WORKDIR: created and printed
python3 scripts/artifact.py workdir "Q3 sales report"

# Check the pages before saving them: the entry first, with the title it will get
python3 scripts/artifact.py check <workdir>/index.html <workdir>/anexos/detalle.html \
    --title "Q3 sales report"

# Create, from the files in its working folder, with a one-sentence description and
# 3-5 lowercase topic tags. --base is what keeps the directories: without it every
# file lands flat at the root of the artifact.
python3 scripts/artifact.py create --title "Q3 sales report" --type html \
    --description "Ventas del tercer trimestre por tienda y categoría, con conclusiones." \
    --tags ventas,q3,informe --base <workdir> --file <workdir>/index.html \
    --file <workdir>/anexos/detalle.html --file <workdir>/css/site.css \
    --file <workdir>/img/logo.png

# Read before editing. Always. A large file goes to its working folder, not into the
# conversation.
python3 scripts/artifact.py files <artifact_id>
python3 scripts/artifact.py read <artifact_id> index.html
python3 scripts/artifact.py read <artifact_id> index.html > <workdir>/index.html

# Edit in place: change the file in the working folder, then write it back
python3 scripts/artifact.py write <artifact_id> index.html --from-file <workdir>/index.html
python3 scripts/artifact.py rm <artifact_id> anexos/old.html
# Add or replace an image, a font or a clip a page uses (a stylesheet or a script: write)
python3 scripts/artifact.py upload <artifact_id> img/logo.png --from-file <workdir>/img/logo.png
python3 scripts/artifact.py rename <artifact_id> "Q3 sales report"
python3 scripts/artifact.py tag <artifact_id> --set ventas,q3,informe   # replaces all
python3 scripts/artifact.py tag <artifact_id> --clear

# A separate document from an existing one: the copy is the caller's, and private
python3 scripts/artifact.py copy <artifact_id> --title "Q3 report (EMEA)"

# Share. Adds to the list (--replace overwrites it, --remove takes ids off it);
# --role applies to the ids of this call, and sharing again changes a role.
python3 scripts/artifact.py share <artifact_id> --user alice --group analysts
python3 scripts/artifact.py share <artifact_id> --user bob --role editor
python3 scripts/artifact.py share <artifact_id> --user carol --role owner   # co-owner
python3 scripts/artifact.py share <artifact_id> --link on    # any Stratio user can read
python3 scripts/artifact.py share <artifact_id> --remove --user alice
python3 scripts/artifact.py members <artifact_id>             # who has it, and how

# Only when the person asks for a list. --tags needs all of them; --search also
# matches tags.
python3 scripts/artifact.py list --scope shared --type html --tags ventas,q3 --favorite

# Everything the API knows about one artifact, and the link on its own
python3 scripts/artifact.py get <artifact_id>
python3 scripts/artifact.py url <artifact_id>

# Owners only, and only when the person explicitly asked for it
python3 scripts/artifact.py delete <artifact_id>
```

Every command prints JSON on stdout, except `read`, which prints the file's text raw so
you can edit it and write it back, and `url` and `workdir`, which print the link and the
folder. `check` prints one entry per file with its findings (an empty list is clean);
`create` and `write` print the same findings on stderr as `check: …` lines, as warnings.
On failure a command prints one line on stderr and exits non-zero. `list` and `recent`
print one page; when more follow, a line on stderr says how many there are and which
`--page` comes next — fetch it only if what you are looking for is not on this one.

## Roles

Every artifact `resolve`, `list`, `recent`, `create` and `copy` print comes with the
person's `access_role`, `can_edit` and `can_manage` on it. Check them before you offer
to change anything; you already have them, so do not `get` the artifact again just
for that.

- **owner** (`can_manage`) — everything: edit the content, the title and the tags,
  share it (and change or remove other people's roles) and delete it. The
  person who created it is always an owner; others can be made owners too.
- **editor** (`can_edit`) — edits the content, the title and the tags. Cannot share it
  and cannot delete it.
- **reader** — read only. Can read it and `copy` it, nothing else.

These roles are per artifact. A **new** artifact is different: `create` and `copy`
answer `403` when the person has no GenAI role.

An owner shares it with users and groups, each as `reader`, `editor` or `owner`, and
can turn on **link sharing** (`share --link on`): then any authenticated Stratio user
who has the link can read it. Link sharing never grants editing. Share only with the
people the person names, with the role they ask for, and turn link sharing on only
when they ask for it. Making someone an `owner` hands them delete and re-share rights:
do it only when the person explicitly asks for owner (or co-owner) access, never as a
default and never because "editor" seemed not enough.

**Only an owner changes who can access an artifact.** Before any `share` (adding,
removing or changing a role, or turning the link on or off), check `can_manage`. If it
is not `true`, do not run `share`: say that only an owner of that artifact can change
its permissions, and who its owner is (`get` gives it, as `user_id`).

If a call comes back `403`, the role does not allow it: do not retry, and do not
rebuild the artifact from its content to get around it. Tell the person what their
role lets them do and who can do the rest (an owner). If they wanted their own
editable version, offer `copy`.
