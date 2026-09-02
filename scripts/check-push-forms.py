#!/usr/bin/env python3
"""Push-form absence gate — fail if any tracked file teaches an agent-side
remote-mutating VCS or forge command.

Under the coordination doctrine an agent never publishes a branch or lands a
merge with its own keystrokes: it calls the daemon tools instead (a branch
publication tool for worker/lead, a lead-only landing request). A shipped skill
that still spells a remote-mutating command teaches the retired mechanic, and
the failure is silent — the reader follows the skill, the floor guard refuses,
and the session is stuck. This gate makes that class impossible to reintroduce.

Structural, not a regex. A literal search for the two-word form misses every
variant the floor guard denies, so this scanner reproduces the guard's rule
table (stated here rather than shared as code: the skills repository is
content-only and may not import from the container repository).

THAT CLAIM WAS OVERSTATED UNTIL SOMEONE MEASURED IT, and the correction is why
several of the rules below exist. "Reproduces the guard's rule table" had been
checked on the SHELL model — the quote forms, the carriers, the per-shell
arities — and never on the VOCABULARIES, which is exactly where the two tables
had drifted. A differential run, one form per file through both sides, found
six CLASSES of form the guard refuses and this gate did not: the VCS's two-word
publishing families, its inline alias, a `${…}` in any operation position, the
dashed family executables, the forge CLI's non-PR families, and the rest of its
pull-request vocabulary. Two more went the other way, this gate reporting what
the guard permits: a terminal global behind which nothing runs, and a
request-body flag under an explicit GET. All are folded in below. Counts are
deliberately not quoted — the number is a function of two rule tables and goes
stale when either moves, which is the failure mode class (e) exists for — but
the differential itself is re-runnable and was empty in both directions when
this paragraph was written, save the deliberate content-gate findings named
under "Known false-positive residuals".

Normalization, in order:

  * **Markdown prefixes are stripped from every PHYSICAL line first** —
    blockquote (`>`, with or without a following space, nested), bullet,
    checklist, numbered list, and ATX heading — so a list item or a quoted line
    is parsed as the command it spells and not as a program named "-" or ">",
    and so a continuation whose lines are each quoted still joins.
  * **Backslash-newline continuations are then joined**: a line ending in an
    ODD run of backslashes is joined with the next (an even run is an escaped
    backslash and ends the line). A finding is reported at the FIRST physical
    line of the joined span.
  * Each logical line is read three ways, and the findings are unioned:
      (a) as a shell command line, quote-aware — what a shell would run;
      (b) each Markdown code span (backtick-delimited) as its own command line
          — an apostrophe earlier in the prose cannot hide it;
      (c) quote-NAIVE, but only when the line's shell quoting is unbalanced —
          i.e. when the quotes cannot be meant literally, which is what an
          apostrophe in prose looks like. A balanced line is read only as a
          shell reads it, so a genuinely quoted argument (`echo "a; ..."`) is
          an argument, not a command.
  * The shell's QUOTING model lives in ONE place (`_quote_at` / `_quote_end` /
    `_quote_value`), and the balance check, the splitter, the substitution
    reader, the tokenizer and the quoted-span reader all ask it. Bash has FOUR
    quote forms, not two, and the two that a per-loop model kept missing are
    executable: `$'…'` decodes its escapes (so a word — including the PROGRAM
    name — can be spelled entirely in hex or octal, with no literal word on the
    line at all), and `$"…"` is a double-quoted string carrying a translation
    marker. A quoted region contributes its VALUE to the current word, so
    `pu$'sh'` and `$'pu'$'sh'` are one word each. Inside DOUBLE quotes a
    backslash escapes only a dollar, a backtick, a double quote, another
    backslash and a newline (DQ_ESCAPABLE) — before anything else it stays
    literal, which is what lets a `$'…'` region survive an enclosing
    double-quoted `-c` string intact for the inner shell to decode.
  * A line is split on shell separators (";", "&&", "||", "|", "&", newline,
    command substitution and parentheses, the backtick, and HTML comment
    delimiters). A command substitution — `$(…)` or a backtick pair, quoted or
    not — is not a separator: its BODY is lifted out as its own command line
    (recursively) and the surrounding command continues unbroken, so
    `echo $(true) <words>` still emits its words. Finding the body's end is
    quote-aware, so a `)` inside the body's own quotes does not close it.
    Inside DOUBLE quotes `;`/`|`/`&` and a BARE parenthesis are literal text;
    inside single quotes nothing is live. A bare `(` outside quotes IS a
    separator — a subshell really does start a new command.
  * Per command: leading VAR=value assignments, shell control keywords
    (`if`/`while`/`!`/`{`/…), and a prose label or mapping key (a first token
    ending in ":", e.g. "Run:" or a YAML "run:") are stripped, then the
    execution carriers — `command`, `builtin`, `exec`, `env`, `nice`, `ionice`,
    `nohup`, `setsid`, `stdbuf`, `sudo`, `doas`, `time`, `timeout`, `xargs` —
    each with its own argument shape: an option with a MANDATORY operand takes
    the next token, one with an OPTIONAL operand takes none, and `timeout`'s
    duration is a positional. Short options CLUSTER, and that is read the same
    way for every carrier and for the forge CLI: within one dash token the
    FIRST letter that takes an operand consumes the rest of the token, or —
    when it ends the token and its operand is MANDATORY — the following one. So
    `env -vu <x>`, `xargs -tE <x>`, `time -po <x>` and `exec -ca <x>` all
    consume `<x>` and reach the command behind it, while a cluster of
    no-operand letters (`xargs -rt`) consumes nothing and an operand-taking
    letter EARLIER in the cluster hides what follows it (`env -uSx` unsets a
    variable named "Sx" and splits nothing). A letter whose operand is OPTIONAL
    (GNU `xargs -e`/`-i`/`-l`) takes an attached remainder and never the
    following token, so `xargs -lE <x>` leaves `<x>` as the program — the real
    tool rejects that invocation outright.
    Two parsers here do NOT follow that rule and are modelled separately. The
    VCS accepts neither an attached nor a clustered short global option — it
    rejects `-C<path>`, `-cfoo=bar` and `-pc` alike — so its globals are read by
    exact match. The SHELLS do not follow it either, and — unlike the carriers —
    they do not agree with EACH OTHER, so every shell carries its own letter
    map — one per IMPLEMENTATION, not per name. THREE arities occur: bash's and
    dash's `-o`, and bash's `-O`, take the next argv element and NEVER an
    attached remainder, so the cluster continues through the letter and
    `bash -oc <opt> <script>` runs `<script>`; zsh's `-o` and ksh93's `-T`/`-R`
    take an ATTACHED remainder when the token has one and terminate the
    cluster, so `zsh -oc <opt> <script>` has no `-c` in it at all; and ksh93's
    `-o` does that but DECLINES a separate operand that is itself an option, so
    `ksh -o -c <script>` still reaches the `-c`. A bare `+` splits them the same
    way — bash and dash skip it, zsh and ksh93 end options at it — and a `+`
    token whose body holds a dash splits them three ways again (bash/dash
    reject, zsh takes exactly `+-`, ksh93 parses through).
    `-c` (and `+c`) means the script is the first remaining OPERAND. WITHOUT a
    `-c` the shells split once more, and this is the divergence that needs no
    option spelling at all: on bash, dash and zsh the first operand is a script
    FILE and there is nothing to scan, while ksh93 opens it as a file and, when
    that open FAILS, executes the operand TEXT as a command line — so `ksh
    <cmd>` runs `<cmd>`, and so do `ksh -oc <cmd>`, `ksh -o c <cmd>`, `ksh +oc
    <cmd>`, `ksh +-xoc <cmd>` and `ksh -- <cmd>`. The operands BEHIND that
    first one are appended to the command line as WORDS (ksh93 runs the text
    with a literal `"$@"` after it), so the form need not sit inside one
    token — `ksh X=1 <vcs> <publish> origin main` publishes, unquoted and
    unescaped — and each keeps its own boundary, so `ksh 'sh -c' '<vcs>
    <publish>'` publishes too and must not be re-split into source.
    A NAME is not an implementation: `sh` and `ksh` are both ambiguous
    and each is read as the UNION of the models it could be, every model's
    candidate script being scanned, because on a gate a model that consumes one
    token too many loses the script outright. Both unions include ksh93 — and
    ksh93 keeps the first-operand behaviour when it IS `/bin/sh`, which was
    probed rather than assumed — so the `sh` spelling carries it too.
    `eval` and `env -S` operands ARE command lines
    and are
    recursed into — `env -S` together with the operands that follow it, which
    are its arguments. That operand may be SEPARATE (`-S x`), attached (`-Sx`,
    `--split-string=x`) or behind a cluster (`-vSx`).
    The program token is reduced to its basename, with
    Markdown emphasis and sentence punctuation trimmed off it and off the
    subcommand.
  * The **quoted operands (either quote style) of any program that is not
    purely text-emitting** (`echo`, `printf`, `true`, `false`) are themselves
    read as command lines. That is what catches an execution carrier this table
    does not know by name — `ssh host "<cmd>"`, `ssh host '<cmd>'` — and prose
    that spells a command inside quotes, without flagging `echo "a; ..."`.
  * A segment whose own rule found nothing — prose, an unknown program, or the
    VCS/forge itself used harmlessly — has the VCS / forge rule tables applied
    at every token position in it, so `Never run <vcs> <publish> from a
    session` and `<vcs> users must never run <vcs> <publish>` are both
    reported — the DASHED executables included, both the plumbing ones and the
    family ones, because a shipped sentence names a command far more often than
    it heads a line with one. Only the text-emitters and the shells are exempt:
    `echo <vcs> <publish>` prints a string and must stay clean **by contract**,
    and `sh -c <vcs> <publish>` really does pass the second word as `$0`.
  * Because the file is Markdown, each line is ALSO read as it RENDERS: code
    spans, emphasis, strikethrough and link labels reduced to their contents (a
    link destination is SCANNED, so balanced parentheses and escapes inside it
    cannot hide the label). And each adjacent pair of non-blank lines that is
    genuinely one paragraph is read as one soft-wrapped sentence: the two must
    sit at the same blockquote depth, the SECOND must not open a new block, and
    the first must not be a heading / fence / table row / comment. A LIST ITEM
    may open such a pair — its own paragraph soft-wraps onto the next indented
    line ("- Never run <vcs>" / "  <publish> from a session" is one sentence) —
    while "- <vcs>" / "- <publish> notifications" stays two items. Block
    markers are read THROUGH the quoting, so "> - <vcs>" is a list item. So
    "never run `<vcs>` `<publish>`", "never run [<vcs>](u) [<publish>](u)" and
    a form straddling a soft line break are caught, reported at the first of
    the two lines, and only when neither line yields the form on its own.
  * For the VCS: the global options that take a SEPARATE operand (-C <p>,
    -c <k=v>, --git-dir, --work-tree, --namespace, --config-env,
    --shallow-file, --attr-source) consume it,
    and any other dash token — an attached `--opt=value`, and the options that
    accept an attached operand ONLY, such as --exec-path — is skipped as a lone
    flag. A TERMINAL global (the bare --version / -v / -h / --help /
    --exec-path / --super-prefix / the three path queries) ends the walk with
    NOTHING: the tool prints and exits, so the word behind it is not a command.
    Only the exact bare token is terminal; every attached spelling sets a value
    and the subcommand behind it does run.
    Either way the walk reaches the first subcommand, which is reported
    when it publishes to a remote (the push subcommand, or the low-level pack
    sender). The dashed plumbing executables of the same names (as a bare
    basename or an absolute git-core path) are reported directly.
    THREE further shapes reach a remote without the publish word in subcommand
    position, and each is its own entry in the one table rather than a special
    case beside it:
      - a TWO-WORD FAMILY (the sub-project, Subversion, Perforce and large-file
        families) whose own OPERATION publishes. The operation is the first
        argument that is neither an option nor an option's operand, so each
        family's option arity is modelled — an operand that happens to equal the
        operation name is an operand. Only that first operand counts.
      - the same family named in the PROGRAM instead, as a dashed executable,
        which enters the same walk one level further along.
      - an INLINE ALIAS. The tool resolves an alias defined by `-c` on its own
        command line before dispatching, so the visible subcommand can be any
        name. The value is split with the tool's own splitter (a backslash
        escapes, either quote quotes) and SPLICED INTO ARGV with the walk
        restarted, because an expansion may introduce further globals or name
        another alias; a value behind `!` is a shell command line and is
        recursed into instead. The config KEY is case-insensitive in full —
        section and name — while the VALUE is not, both measured. The alias is
        popped as it resolves, so a self-referential definition terminates, and
        a CHAIN past the hop bound is REPORTED rather than passed.
  * For the forge CLI: PR mutations (create / merge / close / ready / edit /
    update-branch / revert / reopen — its whole publishing vocabulary, against
    that CLI's own help rather than the handful the doctrine listed; the
    discussion-state actions comment / review / lock / unlock stay out because
    they change conversation, not published code) and a raw API call that
    MUTATES are reported. Attached operands (-XPOST, -fkey=value) and CLUSTERED
    ones (-iX POST, -iFkey=value) alike: that CLI parses with pflag, which
    clusters exactly as getopt does, so its own operand-taking short options
    are modelled too and a mutation letter behind one of them is that option's
    VALUE, not a flag (`-qX POST` is a jq query, and no method is set).
    Whether the API call mutates is decided from the WHOLE option set, not at
    the first flag, because the method and the parameters interact: a
    request-body flag alone implies POST and IS a mutation, while the same
    flags under an EXPLICIT GET are a query string — that CLI's own documented
    search idiom, which the gate used to report as a publish.
    Its non-PR families are read too, each with the condition that makes the
    action a publish rather than a setting change: creating a repository WITH
    the publishing flag (that flag is a pflag BOOLEAN, so `--<flag>=<false>` in
    any of its false spellings publishes nothing and is not a finding, and a
    REPEATED flag is LAST-WINS in both directions — the effective value is
    tracked in encounter order rather than accumulated, or `--<flag>
    --<flag>=false` reads as a publish the tool never performs), syncing
    a DESTINATION repository (with no destination it updates the local checkout
    and touches no remote), and creating OR uploading to a release — the second
    attaches assets to an already-published release, which is the same publish
    one step later. An ACTION's own operand-taking options are modelled where
    the condition is a positional, because there the option's VALUE would
    otherwise be counted as the destination; that table is read with the
    opposite bias from the global one — only real arities, since an option
    wrongly listed swallows the destination and LOSES the finding. Forking,
    deleting,
    archiving, renaming and the metadata families stay out with their reasons
    recorded at the table — destructive is not the same question as publishing,
    and publishing TEXT is an exfiltration question this table does not answer.
  * A `${…}` in an OPERATION position is read for the literal it could expand
    to, at every one of those positions — subcommand, family, family operation,
    forge subcommand, PR action, forge family, family action. The parameter's
    value is unknowable from the line; the literal in the expansion is not.
    Only the word that can BECOME the value counts: a default or alternate
    (`:-` `-` `:=` `=` `:+`) and the REPLACEMENT side of a substitution, never
    a prefix/suffix removal (whose result is a substring of the parameter), the
    error-message form, or a case / length / substring / indirection. A bare
    `${x}` names nothing and passes, which is the same variable-indirection
    boundary this gate documents below.
    ESCAPES AND QUOTES inside an expansion belong to the expansion's grammar,
    not to the shell's word splitting, so the tokenizer hands `${…}` bodies
    over verbatim — backslashes AND quoted spans, quotes included — and the
    body walk, the operator search and the separator search all re-read them
    the same way. The replacement word (and the default/alternate word, which
    is the identical fact under a different operator) is then unescaped and
    de-quoted before it is compared, because the shell drops those backslashes
    and those quotes. Reading it either way round is wrong in both directions
    at once — a real replacement whose PATTERN carries an escaped slash is
    missed, and a pattern-only expansion carrying one is reported.
    The one place the measured shells DISAGREE is a quoted SEPARATOR, so
    neither reading may be adopted alone: `${x/"a/b"/<publish>}` publishes on
    ksh93 (quote-aware) and `${x/"a/<publish>"}` publishes on bash 3.2 (not
    quote-aware), each a silent miss under the other reading. The separator
    search is therefore run BOTH ways and the words UNIONED, which is the
    candidate-LIST lesson one position further in: an ambiguous operand has a
    SET of meanings and picking one decides the rest away. A quoted BRACE is
    not ambiguous — bash, zsh and ksh93 all agree it closes nothing — and is
    read quote-aware unconditionally.
    The union has exactly ONE asymmetry, and it is asymmetric because the
    measurements are: a naive separator that lands inside an UNTERMINATED
    quoted span leaves an empty pattern, which no measured shell runs (two
    reject the line, the third never substitutes), so the naive reading skips
    an empty pattern. The quote-aware reading does NOT, because a balanced
    empty pattern IS real there — `${x/""/<publish>}` yields the publishing
    word on zsh and ksh93 when the parameter is empty. Applying the
    restriction to both readings would drop that, which is a miss.
  * Shell command strings (sh|bash|zsh|dash|ksh) are recursed into at **any**
    depth, as are every other nested command line above: the walk is an explicit
    worklist, and it terminates on a LEXICOGRAPHIC PAIR whose first component
    depends on the reading: quote-aware, (sum of token-value lengths,
    serialized length); quote-naive, (token count, serialized length). No
    single one of those quantities does the job — the SERIALIZED length is the
    bound this walk used to carry and the ksh93 operand reconstruction can grow
    it (that bound silently dropped real work), the token-value sum does not
    fall across the quoted-operand pass, which can hand a QUOTED PROGRAM TOKEN
    back whole, and the token count does not fall when a quoted multi-word
    operand splits into its words. `scan_command_text` carries the full
    argument and the numbers it was checked on. There is no
    fixed depth cap. Finding the script is a parse, not a scan: the shell's own
    invocation options are consumed with their operands under THAT SHELL's
    arity map (bash `-o`/`-O` and dash `-o` from the next token, zsh `-o` and
    ksh93 `-T`/`-R` attached-or-next, ksh93 `-o` attached-or-next but declining
    a separate operand that is itself an option, bash `--rcfile`/`--init-file`
    and zsh `--emulate` from the next token, the `+` forms identically), so the
    script is the first remaining OPERAND and not an option's value. Usually
    that operand only counts after a `-c`; on ksh93 — and therefore under the
    `ksh` and `sh` unions — the first operand is a command line with or without
    one, which is why a bare `ksh <cmd>` is recursed into at all.

NOT a finding, deliberately: LOCAL branch deletion (the branch subcommand with
-d / -D) touches no remote and stays in the doctrine as-is.

Scope boundary — what this gate does NOT see, stated so the claim is honest:

  * inside a FILE a skill tells the reader to execute (`bash helper.sh`) — the
    credential wall, not this gate, is the control there;
  * a program named through a variable or a command substitution (`$GIT …`,
    `$(which …) …`) — neither can the floor guard, which reads the same
    command text;
  * an unquoted operand of a carrier in none of the tables above (a
    `find -exec`) — the quoted form IS caught, and adding a name to a table is
    the fix when one shows up. The string-exec carriers are the worked example
    of that fix: their command-bearing OPTIONS are modelled now
    (`STRING_EXEC_SPEC`), and their trailing operands are still reached only by
    the prose pass — which reports them, so the gap is in the reading, not the
    verdict;
  * an inline alias whose VALUE comes from the ENVIRONMENT rather than from
    the line (`<vcs> --config-env <alias-prefix><name>=VAR <name>`) — the value
    is not on the command line at all, which is the same boundary as a program
    named through a variable, and the floor guard cannot see it either;
  * a mechanic described without spelling its command;
  * **the UNMEASURED-AND-UNPROBED residual class** — named here so the next
    reader knows its shape instead of rediscovering it one review round at a
    time. It was called the "unmeasured-arity" class and described as the one
    open class left; both halves of that name were too narrow. Not every gap
    is an ARITY (ksh93's first operand is a command line, which no arity
    describes), and not every gap is UNMEASURED (that one was found on a
    binary every arity in the file had already been measured on) — see (d)
    below.

    Every SHELL arity in this file is measured; the carrier tables are measured
    except for the FreeBSD-only entries, which are marked DOCUMENTED at that
    table (see the platform-union note). Measurement is bounded by what this
    host can run: bash 3.2.57(1) (also its /bin/sh), dash, zsh 5.9, ksh93u+
    2012-08-01, and the GNU/BSD carriers installed here. The LETTERED entries
    below sit outside that boundary — every one of them, not a number: this
    note used to say "FOUR things", which was true of (a)-(d) and had already
    gone stale when (e) was appended, and (f) makes the same point twice. A
    count of a list that grows is a claim that falsifies itself on the next
    edit, which is exactly what (e) is about. The list is the list.

      (a) a shell IMPLEMENTATION that is not installed here — mksh, pdksh /
          OpenBSD ksh, busybox ash, yash, posh. No map claims to describe them.
          Both ambiguous NAMES are read as a union that includes the minimal
          POSIX map (dash's — the one measured map where only `-o` takes an
          operand), so an unmeasured shell whose extra letters are BARE still
          yields its script as a candidate. What is NOT covered is the reverse:
          an unmeasured shell that takes an OPERAND for a letter every measured
          map reads as bare, which would leave its script one token further on.
      (b) a platform variant of a CARRIER — those tables are a documented
          platform UNION, and the FreeBSD-only entries (`env -L/-U`) are
          documented rather than observed, as marked at that table.
      (c) VERSION drift in a measured tool — bash 5.x, a newer ksh93, a future
          option. Only the installed versions were run.
      (d) an UNPROBED INTERACTION or FALLBACK inside a tool that IS measured.
          The three above are all "a thing we could not run"; this one is a
          thing we ran and did not ask the right question of, and it is the
          class with the worst record here. ksh93's first-operand fallback
          belongs to it: every arity in the letter map was measured on that
          binary, and the binary still executed a command line in a shape no
          probe had covered, because every probe had put a `-c` somewhere in
          the invocation. So did the THIRD `-o` arity (visible only when the
          neighbouring token is an option) and the dashed-`+` shape. A measured
          implementation is measured over the probes actually run, never over
          its behaviour; a new question asked of an old binary is as likely to
          find something as a new binary is.

          A SECOND kind of failure lives here too, and it is worse because it
          leaves no gap to find: a behaviour that WAS probed, WAS recorded in
          these comments, and was not acted on by the walk. The operand join
          behind ksh93's first operand sat written down for a round while
          `ksh X=1 <vcs> <publish>` went unreported. When a probe is recorded,
          check that some branch consumes it.

      (e) a CLAIM ABOUT THIS FILE'S OWN INTERNALS — an invariant, an
          equivalence — checked against SOME of its producers or consumers and
          not all of them. Not a gap in what was measured about a tool: a gap
          between two parts of THIS file. Three instances so far, and the
          narrower wording this entry used to carry ("a stated invariant that a
          later producer falsifies") covered only the first of them:

            1. `scan_command_text` bounded its worklist by "every nested string
               is strictly shorter than its parent" — true of every producer
               that existed when it was written. The ksh93 operand
               reconstruction was the first that can grow a string, and the
               bound then discarded real work without a word. Invariant first,
               falsifying producer second.
            2. Its replacement, "every producer drops the program token, so the
               sum of token-value lengths strictly decreases", was falsified by
               a producer that ALREADY EXISTED: `quoted_spans` also scans a
               quoted PROGRAM token, so `'abc'` nests to 'abc' and the measure
               goes 3 -> 3. Producer first, invariant second — the reverse
               order, and the same defect.
            3. The note on always-quoting the appended operands argued the
               change was inert by showing the two serializations TOKENIZE
               identically. They do; and the reconstruction has a second,
               independent consumer — the raw `quoted_spans` pass — under which
               they differ, so the equivalence was argued over one consumer of
               a value that has two. Not an invariant at all.

          So the check is not "did I falsify a stated invariant": it is, for
          any claim you make about this file, ENUMERATE the producers or
          consumers it quantifies over and confirm the claim on each. A walk's
          termination argument and a "this change is inert" argument fail the
          same way, in both directions of time.

      (f) an EQUIVALENCE WITH AN ARTEFACT OUTSIDE THIS FILE, verified on some
          of its axes and asserted on all of them. (e) is a gap between two
          parts of this file; this is a gap between this file and the thing it
          claims to mirror, and it has one property (e) does not: NOTHING IN
          THIS REPOSITORY CAN FALSIFY IT. A tree has no oracle for what another
          tree contains, so the claim can only be checked by running both sides
          over the same inputs and comparing verdicts.

          The instance: the header said this scanner "reproduces the guard's
          rule table". It reproduced the SHELL model faithfully — that half had
          been probed for rounds — and had drifted from the VOCABULARIES
          entirely, in both directions at once. Six classes of form the guard
          refused went unreported here; two this gate reported the guard
          permitted. Every one of them had been sitting behind a claim that
          read as though it covered them, and no test in either repository
          could have said otherwise.

          The check, when you next make a claim of this shape: name the AXES
          the equivalence quantifies over and say which were measured. "The
          shell model matches, the vocabularies were never compared" is a true
          sentence and would have made this visible a long time before a
          differential did. And a differential is cheap — one form per file
          through both sides — so run it rather than restating the claim.

          What this class does NOT license is quietly relaxing this gate to
          match. The two artefacts answer different questions: the guard
          decides whether a command RUNS, this gate decides whether a document
          may TEACH one. Where they must agree is the rule table; where they
          need not is the reading — a form spelled in a trailing comment or
          inside a quoted prose mention is nothing for a runtime guard and is
          the whole point of a content gate. Those cases are named under "Known
          false-positive residuals" and are the only divergence this gate
          accepts by design.

    The shape of the residual is narrow but NOT as narrow as this note used to
    claim. It said a miss also required "an option spelling no shipped skill
    would plausibly contain", and that conjunct was FALSE: `ksh <cmd>` needs no
    option at all, and it was a miss until the first-operand flag landed. What
    is left, stated without that conjunct: a form is missed when an unmeasured
    or unprobed behaviour and an unquoted (or backslash-escaped) command string
    hold together. Even "unquoted" is not much of a narrowing on ksh93, where
    the appended operands are ordinary words: `ksh X=1 <vcs> <publish> origin
    main` needs no quoting, no escaping and no option at all. The QUOTED
    spelling of a SINGLE-TOKEN command string is reported regardless, by the
    quoted-operand pass, which does not consult the shell parse at all — that
    pass, not the narrowness of this conjunction, is what makes the residual
    small, and it does not reach a form spread across separate operands.

    A PREVIOUS VERSION OF THIS NOTE CLAIMED the token kinds a shell invocation
    can contain were enumerated in full, and that only new arities for known
    kinds remained. **That claim was false and is retracted.** It was made from
    a one-dimensional probe sweep, and the next review round falsified it twice
    over: ksh93's `-o` turned out to have a THIRD arity visible only when the
    following token is itself an option (`ksh -o -c <script>` runs <script>
    where every other shell consumes the `-c`), and a `+` token whose body
    contains a dash turned out to be a further token shape with three different
    per-shell behaviours (`ksh +- -c <script>` and `zsh -c +- <script>` both
    run <script>; bash and dash reject them). A LATER ROUND falsified it a
    third time, and from the axis nobody had varied: every probe on record had
    put a `-c` somewhere in the invocation, and ksh93 executes its first
    operand as a command line when there is none at all.

    The lesson, recorded so the next reader does not repeat it: the surface is
    not the set of token SHAPES. It is the cross-product of token shape x
    position relative to `-c` x PRESENCE of a `-c` x the class of the
    NEIGHBOURING token x implementation, and every entry in that product is an
    open question until a binary has answered it. Sweeping one axis and
    generalising is what produced three successive false closure claims. Treat
    this parser as MEASURED-COMPLETE over the probes actually run and recorded
    here — and only over what those probes were actually asked, which is not
    the same as what they printed: the operand JOIN behind ksh93's first
    operand was recorded in this file for a full round before anything acted
    on it, and until it did, `ksh X=1 <vcs> <publish>` was a live miss with
    its own evidence sitting in the comments. Never treat it as
    PROVEN-COMPLETE over the grammar; when a new divergence appears, add the
    per-model table entry, add its probe to the record, AND make the walk act
    on it.

Performance characteristic — NOT a residual class, and deliberately not lettered
alongside the classes above. Those classify what this gate cannot SEE; this is
what it COSTS, which is a different kind of fact and does not belong in a list of
blind spots. (This said "(a)-(e)" for a round after class (f) was opened, and
nothing noticed; naming the list rather than its last letter is what keeps the
reference from going stale the next time one is added.)

    The walk is QUADRATIC in the length of a single logical line, on the `eval`
    chain. `eval` nests by re-serializing its remaining tokens, dropping one
    token per step, and every step re-runs `split_commands` and `tokenize` over
    the whole remaining string — so a line of N chained `eval` tokens costs N
    steps of O(N) scanning. Measured here on python3, a line of 1600 tokens /
    7998 bytes (`" ".join(["eval"] * 1598 + [<vcs>, <publish>])`): 4.26s
    median of 3. The shape is unmistakable — the same construction at 200 / 400
    / 800 / 1600 TOTAL tokens (198 / 398 / 798 / 1598 of them `eval`) runs in
    0.062s / 0.258s / 1.03s / 4.11s, four times the time for twice the input —
    and a profile of the 800-token one puts ~99% of it in `split_commands` +
    `tokenize`, called 799 times each: once per worklist step, which is one per
    `eval` plus the final segment.

    It is PRE-EXISTING, not a cost of the recent shell work: the same line at
    `a7eb4aa` — before the ksh93 first-operand rule, the operand join and the
    reconstruction landed — measures 4.16s median of 3 against 4.26s at this
    commit, a difference inside the run-to-run spread.

    SIZE IS NOT THE TRIGGER, and saying so would be wrong here: the
    `shell-nested-deep` fixture is 8270 bytes — LONGER than the 7998-byte line
    above — and scans in 0.005s, because 12 levels of `sh -c` nesting is 26
    tokens and 13 worklist pops (the line itself plus its twelve nestings)
    where the 800-token `eval` line takes 799. The longest line in any shipped
    skill is 859 bytes. What costs is specifically a long CHAIN of `eval`
    tokens, which turns one line into one worklist step per token, and no
    fixture or shipped skill has that shape. It is a characteristic, not a
    defect, and it is
    recorded rather than fixed. It would matter if this gate were ever pointed
    at generated or minified content; the fix if that day comes is to hand the
    walk a token LIST rather than re-parsing a string at every step.

The authoritative control is that sessions hold no push credential; this gate is
content hygiene over that wall. Known false-positive residuals:

  * a line whose shell quoting is UNBALANCED is read as prose, so a quoted
    argument on such a line can be reported — write the line balanced;
  * the two words in an ordinary NOUN PHRASE are reported when they happen to
    spell the form — "Configure <vcs> <publish> notifications in your editor"
    is a finding. That is deliberate and it is not specific to the soft-wrap
    pass: the single-line sentence is reported too, by the same prose rule that
    catches "Never run <vcs> <publish> from a session". The gate cannot tell a
    noun phrase from an instruction without a heuristic that would make the
    pair pass weaker than the line pass and reopen the silent miss it exists to
    close. Since the acceptance is ZERO findings tree-wide, the cost of this
    residual is one rewording of a shipped sentence, and it is paid once; the
    cost of the opposite error is a skill that teaches a retired mechanic.
    The vocabularies folded in from the floor guard WIDEN this residual — a
    sentence naming a two-word family beside its operation, or the forge CLI
    beside a family action, is a finding on the same rule — and the trade is
    the same one, at the same price;
  * a `${…}` in an operation position is compared on its INTERIOR alone, so a
    token that could only ever expand to something LONGER is still reported:
    `<vcs> pre${x:+<publish>}` can only become `pre` or `pre<publish>`, neither
    of which is a subcommand, and it is a finding. Same for the reverse — an
    expansion nested deeper than the reader's cap contributes no candidate at
    all, which is a MISS rather than a false finding, and is bounded at a depth
    no shipped document reaches. Both are shared with the runtime rule table
    verbatim, and narrowing either here alone would break the lockstep in the
    direction that matters;
  * RETRACTED, third retraction in this file — "a forge family's own option
    grammar is not modelled, so an option VALUE in an action's operand
    position is read as a positional; shared with the runtime rule table, same
    trade". The residual was real when it was written and BOTH halves of the
    sentence are now false: the sync action's own value options are modelled
    (see FORGE_ACTION_VALUE_OPTS), and the "shared" half had gone false on its
    own, without an edit here, when the runtime table modelled them first.
    That is class (f) exactly — an equivalence with an artefact outside this
    file, which nothing in this repository can falsify — and it is why the
    differential is re-run against a fresh snapshot rather than trusting the
    sentence. A residual note is a claim like any other and goes stale the same
    way; the one below it, about the terminal globals, is the same shape and is
    still true only because it was re-measured;
  * a bare terminal global other than the exec-path one is rejected by the tool
    in its ATTACHED spelling, and the gate still reports the subcommand behind
    it — an invocation that runs nothing at all. Measured, shared with the
    runtime rule table, and recorded at VCS_TERMINAL_OPTS rather than narrowed.
  * NEW, and the reason `SSH_SEPARATOR_WS` is spelled out rather than reusing
    `str.isspace()`: the tokenizer splits words on Python's whitespace, which
    accepts VERTICAL TAB and FORM FEED, and neither the shell's default IFS nor
    ssh_config's separator grammar does. So `$'<vcs>\\v<publish>'` is one word
    to a shell and a nonexistent program, and two words here — a finding on a
    line that runs nothing. Left standing: it is over-detection, the direction
    this gate is biased in, and the line is a mention either way. It is written
    down because it is the reason a whole-line fixture cannot pin the ssh
    separator SET (both readings flag), which is why that set is pinned by
    parser-level cases against `analyze`'s nested output instead.

Lockstep with the runtime guard, stated so the asymmetry is not mistaken for
drift. The rule TABLES are meant to be identical and the differential is
re-runnable; what differs is the READING, and only in ways this gate owns:

  * a form spelled in a trailing `#` comment, or inside a quoted prose mention
    (`grep -rn "<vcs> <publish>" .`, `<vcs> commit -m "no more <vcs>
    <publish>"`), is nothing to a runtime guard and is precisely what a content
    gate exists to catch. Those are findings HERE by design.
  * a DASHED FAMILY EXECUTABLE named anywhere in a sentence rather than at the
    head of a command. The guard reaches it whenever a carrier it models hands
    the words over as an argv, which covers the ways a command actually gets
    run; a sentence is not one of those ways, and it is the only way a
    DOCUMENT carries the form. Findings here by design. (The guard's own prose
    pass is one entry short of this, which is a completeness item for it — see
    the routed note — but it is not what this difference is.)
  * a name behind a LOOKUP. The guard models the wrapper options that turn a
    carrier into a lookup instead of an invocation (measured on this host:
    `command -v <vcs> <publish>` prints the tool's path and answers
    "<publish>: not found", and the same letters inside a valid cluster do the
    same), and permits them, correctly — nothing executes. That entry is
    deliberately NOT mirrored: what a lookup leaves on the line is the two
    words as a MENTION, and a mention is a finding here on the same rule that
    reports the quoted one. The cost of not mirroring it is that the carrier
    walk still reads the name behind the lookup as the program, so the form is
    reported by the VCS rule rather than by the prose pass — same verdict,
    over-detection in the safe direction, and the difference is visible only in
    `analyze`'s program field.
  * a carrier the GUARD gives a real argument grammar and this gate gives HALF
    of one. AMENDED, and it is the fifth correction in this file: this bullet
    used to say "this gate has no such grammar — a quoted operand of any
    non-emitting program is read as a command line instead", and it drew the
    right conclusion (do not mirror the guard's PROSE EXEMPTION for these
    carriers) from a premise that was only half true and had a MISS hiding
    behind it. The quoted-operand pass reads such an operand as a command line
    and therefore gets the SHELL's reading of it, which is exactly wrong for an
    option whose operand is `Keyword=<command>`: `-o ProxyCommand=<vcs>
    <publish>` reads as an assignment prefix followed by a program named
    `<publish>`, and is clean. Every spelling of that was a miss here, the plain
    one included; what looked like coverage was the SPACE in the noisy
    spellings leaving the two words separate in the re-read. So the OPTION half
    of the guard's `STRING_EXEC_SPEC` is now mirrored (`STRING_EXEC_SPEC` here,
    with `_ssh_option_pair`) and the two halves that are not mirrored are named
    at that table with their reasons: the prose exemption (mirroring it would
    open a miss, as the old note said) and the joins-operands reconstruction
    (the prose pass already reports that shape more strictly). The positionless
    pass is still the only thing here that sees `ssh host echo <vcs>
    <publish>`, and that stays a finding.
  * the git SUBCOMMANDS that execute an operand (the submodule and bisect
    runners, the rebase exec option, the history-rewrite filters). The guard
    needs an explicit table for these because it has no quoted-operand pass;
    here the same forms are already reached by the quoted-operand pass and by
    the positionless one, so the table is not duplicated — the FORMS are
    pinned instead, positive and negative, in the fixtures below.
    Stating the axes, since this is a class (f) claim like any other: 26 forms
    were run through both sides — every subcommand and filter option in the
    guard's table, in the single-quoted, ANSI-C-quoted, attached-value and
    bare-word spellings, with a publishing operand and with a harmless one,
    plus the operand-taking filter deliberately ABSENT from it — and the two
    sides agreed on all 26. Measured over those forms, not proven over the
    grammar; a new spelling is an open question until it has been run.
  * A HANDFUL of rules are stricter here than the guard, knowingly. Each is a
    live gap in the GUARD rather than a reading difference — every one was
    measured against the real tool, and every one is routed back with the
    measurement and the fix. They fall into two shapes.
    Wrong CASE-FOLDING and one unasked position:
      - the inline alias's config KEY is case-insensitive IN FULL. MEASURED on
        2.54.0: a definition spelled in one case and invoked in the other
        reaches the push machinery in both directions. The guard folds only the
        section, so it permits both spellings.
      - the alias NAME reached through a `${…}`. Every other operation position
        consults the expansion reader; this one did not, on either side.
      - the dashed family executable in the guard's own prose pass, above.
    CROSS-RULE COMPOSITIONS, which is the shape worth naming because a rule
    table that is equal ENTRY BY ENTRY still says nothing about how two entries
    behave together — a differential built one form per rule cannot see them,
    and single-entry mutation testing stays fully sensitive while they escape:
      - a shell-valued alias runs its value AND the invocation's remaining
        operands. MEASURED: `<vcs> -c <prefix>p=!echo p one two` prints
        "one two", and the same shape with the VCS as the value publishes. Both
        tables dropped the operands, so the form was a miss whenever it was
        written unquoted (the quoted spelling was caught by another pass, which
        is what made the gap look closed).
      - an ESCAPED brace closes nothing, so an expansion body must be walked
        escape-aware. Both tables read the body as ending at the first `}` and
        lost the word behind it, even though the same tables already read the
        body's OPERATORS escape-aware.
      - one token can carry more than one `${…}`, so an operand has a LIST of
        candidate meanings. Both tables committed to the first, at three
        positions, and any later candidate decided nothing.
      - a quoted SEPARATOR is read only ONE way in the guard, and that is a
        REGRESSION its own most recent commits introduced. Measured against
        both snapshots: the guard REFUSED `<vcs> ${x/"a/<publish>"}` before
        those commits and PERMITS it after, while bash 3.2.57 really does
        expand that spelling to the publishing word as a single whole argument
        (`set --` reports argc=1). Making the separator search quote-aware
        bought ksh93's reading and sold bash's; the fix is the union, which is
        what this file now does. Recorded as a regression rather than a gap
        because the direction of travel is what makes it worth routing: a fix
        that closes one miss can open another in the same line of code, and
        neither side's test suite had a case for the one it opened.
    Each was closed here rather than left to wait, on the rule stated just
    above: over-detection costs one reworded sentence, under-detection ships a
    document that teaches the retired mechanic.

No opt-out marker: a shipped skill can state that agents do not publish branches
themselves without spelling the command. Fenced code blocks and multiline HTML
comments are NOT exemptions either — they are read for exactly one purpose,
which is to keep separate literal lines from being soft-wrap JOINED into one
sentence; a prohibited form spelled on a single literal line inside a fence or a
comment is still a finding, at that line.

Program and subcommand names are assembled from string fragments so this file
never contains a scannable form verbatim — the gate therefore covers every
tracked file, this one included, with no self-exemption (the check-denylist.py
idiom). The selftest pins those assembled names against INDEPENDENT fragments,
so a typo cannot make scanner and fixtures agree on the wrong word. It pins the
carrier and global-option tables the same way, written out by hand rather than
read from the rule tables: every execution carrier, every carrier option this
gate models as consuming an operand, the SHORT letters among them (which are
the whole input to the cluster walk), every VCS / forge global option it models
the same way, the VCS globals that TERMINATE (required disjoint from the ones
that consume an operand, since nothing runs after a terminal one), the forge
API's own operand-taking short options, and — not exhaustively, but covering
every optional-operand form, which is where that drift actually happens — the
flags that must consume nothing. So dropping an entry from a rule table, or
changing its arity, fails the selftest instead of silently widening the gate's
blind spot.

The VOCABULARY tables are pinned the same way and for the same reason, since
they are where the two rule tables had actually drifted: the two-word
publishing pairs and each family's option arity; BOTH halves of the forge PR
vocabulary, because an action missing from the publishing half is a silent miss
while one wrongly in it is a false finding on an ordinary read; each non-PR
family's CONDITION, spelled as a word rather than as the production sentinel so
renaming one cannot make the two sides agree by construction; the actions those
families deliberately do not refuse, pinned as absent from the rules; the three
`${…}` operator classes, as ordered lists and as mutually disjoint; and the
inline alias's shell marker and hop bound. Each generates its own parse-level
cases, so an entry cannot be pinned and unexercised.

Every entry is a statement of the tool's real arity, with ONE deliberate
widening: the carrier tables are the PLATFORM UNION rather than any single
platform's, so BSD-only options (`xargs -J/-R/-S`, `env -P`, and FreeBSD's
`env -L/-U`) sit beside GNU-only ones (`ionice`, `xargs --process-slot-var`,
`xargs -e/-i/-l`). A union can only over-detect, never under-detect: where the
option does not exist the invocation is a usage error that executes nothing.
Some entries are DOCUMENTED rather than observed — `env -L/-U` and every
FreeBSD-only arity cannot be exercised on a Darwin or GNU host — and are marked
as such at the table.

NUL-safe: files are read as raw bytes and decoded with surrogateescape.

Exit 0 = clean; 1 = finding(s); 2 = setup/usage error.
Usage:
  python3 scripts/check-push-forms.py             # every tracked file
  python3 scripts/check-push-forms.py <path>...   # those files only
  python3 scripts/check-push-forms.py --selftest  # embedded fixture cases
"""
import os
import shlex
import subprocess
import sys


def j(*parts: str) -> str:
    """Assemble a name from fragments (keeps this file scan-clean)."""
    return "".join(parts)


VCS = j("g", "it")                 # the version-control program
FORGE = j("g", "h")                # the forge CLI
PUBLISH = j("pu", "sh")            # its remote-publishing subcommand
PACK = j("send", "-pack")          # the low-level remote-publishing plumbing
PR_SUB = j("p", "r")               # the forge CLI's pull-request subcommand
API_SUB = j("a", "pi")             # the forge CLI's raw API subcommand

VCS_EGRESS = {PUBLISH, PACK}

# The VCS's TWO-WORD publishing forms: a family subcommand whose own operation
# reaches a remote. Nothing in the one-word table sees them, and each is a real
# execution path, so each is its own entry rather than a special case.
#
# OBSERVED on 2.54.0 on this host: the sub-project family really publishes
# (`--prefix=x <remote> <ref>` in its own usage), and the Perforce bridge ships
# here and lists its submit operation. The Subversion bridge and the large-file
# extension are NOT installed here, so those two pairs are DOCUMENTED from
# their manuals (the one commits to the SVN remote, the other uploads objects
# to the remote and exposes the same path as the hook plumbing) and are marked
# as such, in the same style as the FreeBSD-only carrier entries.
#
# The summary-only request-pull subcommand is deliberately ABSENT: it prints a
# message and touches no remote.
SUBTREE = j("sub", "tree")         # the sub-project family
SVN = j("s", "vn")                 # the Subversion bridge
DCOMMIT = j("dcom", "mit")         # …and its publishing operations
SVN_BRANCH = j("bran", "ch")
SVN_TAG = j("t", "ag")
SVN_SET_TREE = j("set", "-tree")
SVN_COMMIT_DIFF = j("commit", "-diff")
P4 = j("p", "4")                   # the Perforce bridge
SUBMIT = j("sub", "mit")           # …and its publishing operation
LFS = j("l", "fs")                 # the large-file extension
PRE_PUBLISH = j("pre-", PUBLISH)   # …its publish path as hook plumbing
VCS_EGRESS_PAIRS = {
    (SUBTREE, PUBLISH),
    (SVN, DCOMMIT),
    # The Subversion bridge has four more writers, all DOCUMENTED from its
    # manual exactly as its main one always has been (it is not installed
    # here): two create a ref in the SVN repository, and two commit a tree or
    # a diff to it. Read-only or local-only and deliberately absent: clone,
    # init, fetch, rebase, log, blame, info, find-rev, show-ignore, propget,
    # migrate, reset.
    (SVN, SVN_BRANCH),
    (SVN, SVN_TAG),
    (SVN, SVN_SET_TREE),
    (SVN, SVN_COMMIT_DIFF),
    (P4, SUBMIT),
    (LFS, PUBLISH),
    (LFS, PRE_PUBLISH),
}
VCS_PAIR_FAMILIES = {family for family, _op in VCS_EGRESS_PAIRS}

# A family's own options that consume a SEPARATE operand, so an operand that
# happens to equal the operation name is not read as the operation. OBSERVED
# from the sub-project family's usage on 2.54.0: -P/--prefix, --annotate,
# -b/--branch, --onto and -m/--message each take one; -q, -d, --squash,
# --rejoin and --ignore-joins take none, and -S/--gpg-sign takes an ATTACHED
# one only. So `<vcs> <subtree> --prefix <publish> split` runs the SPLIT
# operation and is not a finding.
#
# The other three families are deliberately EMPTY. Their arity is unverifiable
# here, and the failure mode of an empty set is a spurious finding on an option
# VALUE that happens to equal the operation name — the safe direction. Do NOT
# populate them from documentation: listing an option that takes no operand
# would swallow the operation itself, which is a MISS.
VCS_PAIR_VALUE_OPTS = {
    SUBTREE: {"-P", "--prefix", "--annotate", "-b", "--branch", "--onto",
              "-m", "--message"},
    SVN: set(),
    P4: set(),
    LFS: set(),
}

# The forge CLI's pull-request surface, classified EXHAUSTIVELY against that
# CLI's own help on 2.96.0 rather than kept as the handful of names the doctrine
# happened to list.
#   MUTATE (here): create, merge, close, ready, edit, update-branch, revert,
#     reopen — "update-branch" merges the base branch into the PR's branch
#     remote-side, "revert" opens a revert PR, and "reopen" is the state twin of
#     "close", which was already listed;
#   NOT here, deliberately — they change DISCUSSION state, not published code:
#     comment, review, lock, unlock;
#   READ-ONLY: checkout, checks, diff, list, status, view.
PR_MUTATIONS = {"merge", "create", "close", "ready", "edit", "update-branch",
                "revert", "reopen"}

# The forge CLI's OTHER families. One question decides membership: does it
# publish code or move a remote ref?
#
#   REFUSED here:
#     · the repository family's create action WITH the publishing flag — its own
#       help says the flag pushes local commits to the new repository;
#     · that family's sync action WITH a positional destination — its help says
#       it updates the matching branch on the destination repository, and the
#       force flag makes it a hard reset. With NO destination it syncs the LOCAL
#       checkout from its parent and touches no remote, so the destination is
#       the test;
#     · the release family's create action — it publishes a tag and its assets,
#       i.e. a remote ref, unconditionally, and its upload action, which
#       attaches assets to an already-published release: the same publish, one
#       step later. That family's edit / delete / delete-asset actions change
#       or remove metadata and publish nothing, so they stay out under this
#       table's own question.
#
#   CONSIDERED AND EXCLUDED, with the reason, so the next reader need not
#   re-derive it: forking creates a remote repository but publishes none of this
#   checkout's code; delete / archive / rename / edit / unarchive and the org,
#   project and skill families mutate settings or metadata, and DESTRUCTIVE is
#   not the same question as PUBLISHING; the issue, discussion and gist families
#   publish TEXT, which is an exfiltration question and not this table's; auth,
#   browse, codespace and the checkout alias touch no remote ref.
REPO = j("re", "po")               # the repository family
RELEASE = j("rele", "ase")         # the release family
FORGE_COND_PUSH_FLAG = "--" + PUBLISH      # publishes only with this flag
FORGE_COND_DESTINATION = "<destination>"   # publishes only with a positional
FORGE_FAMILY_RULES = {
    REPO: {"create": FORGE_COND_PUSH_FLAG, "sync": FORGE_COND_DESTINATION},
    RELEASE: {"create": None, "upload": None},
}
REPO_CREATE_PUSH_FLAGS = {FORGE_COND_PUSH_FLAG}
# The forge CLI parses with pflag, where a boolean flag may carry a VALUE:
# `--<flag>` is true and `--<flag>=<bool>` takes what it is given. These are the
# false spellings its boolean parser accepts. Discarding the value reported a
# create that publishes nothing. Anything NOT in this set counts as enabled —
# an unparsable value makes that CLI exit before publishing, so the
# conservative reading costs nothing.
PFLAG_FALSE = {"0", "f", "F", "false", "FALSE", "False"}

# The VCS resolves an alias defined on its OWN command line before dispatching,
# so the visible subcommand can be an arbitrary name and the publishing word
# need not appear in subcommand position at all. OBSERVED on 2.54.0: a
# `-c alias.<name>=<publish>` global followed by <name> reaches the push
# machinery ("fatal: No configured push destination"); a CHAIN of them resolves
# hop by hop; an expansion may itself introduce further globals; and a value
# beginning with the shell marker is a shell COMMAND LINE rather than a
# subcommand.
#
# The whole config KEY is case-insensitive, not just its section. MEASURED on
# 2.54.0 in a scratch repository, both directions: a definition spelled in one
# case and invoked in the other reaches the push machinery either way ("fatal:
# No configured push destination"). The VALUE is NOT folded, and that is the
# same measurement: an upper-cased subcommand is "cannot handle … as a builtin"
# and runs nothing, exactly as it does without an alias.
#
# NOT covered, and it cannot be: the environment-valued form
# (`--config-env alias.<name>=VAR`) takes the value from the ENVIRONMENT, which
# is not on the command line at all — the same boundary as a program named
# through a variable.
VCS_ALIAS_PREFIX = j("ali", "as.")
VCS_ALIAS_SHELL_PREFIX = "!"
# Resolution is bounded, and exhausting the bound is a FINDING rather than a
# pass: a chain that long is adversarial by construction, and the tool itself
# keeps resolving (observed at nine hops).
VCS_ALIAS_MAX_HOPS = 8
ALIAS_BOUND_FORM = "an unresolved %s alias chain" % VCS

# `${parameter<op>word}` operators, split by whether the WORD can become the
# expansion's VALUE. The parameter's value is unknowable from the line, but the
# literal in the expansion is right there, so a token in an OPERATION position
# that COULD expand to a forbidden word is reported.
#
# Only these produce the word:
#   a default or alternate value — `:-` `-` `:=` `=` `:+`
#   the REPLACEMENT side of a substitution — `/` `//` `/#` `/%` (the PATTERN
#     side never survives, so taking the operator's whole tail is wrong in the
#     lenient direction: it yields no candidate at all)
# And these CANNOT, so treating their word as a candidate is a false finding on
# a valid command:
#   prefix/suffix REMOVAL (`#` `##` `%` `%%`) — the result is a substring of the
#     PARAMETER, never of the pattern;
#   `:?` — the word is an ERROR MESSAGE and the shell exits;
#   length, case, substring and indirection — no literal word at all.
EXPANSION_VALUE_OPS = (":-", ":=", ":+", "-", "=", "+")
EXPANSION_REPLACE_OPS = ("//", "/#", "/%", "/")
EXPANSION_NON_VALUE_OPS = ("##", "#", "%%", "%", ":?", "?", "^^", "^",
                           ",,", ",", ":")
EXPANSION_MAX_DEPTH = 4
API_BODY_FLAGS = {"-f", "-F", "--field", "--raw-field", "--input"}
API_METHOD_FLAGS = {"-X", "--method"}

# A shell NAME -> the invocation-option ARITY MODELS a reader running that name
# may actually be running (see SHELL_OPTION_ARITY for the models themselves). A
# name is not an implementation, and TWO of these names are ambiguous:
#
#   * `sh` is bash on this host, dash on Debian/Ubuntu, busybox ash on Alpine,
#     and can be ksh or zsh anywhere;
#   * `ksh` is ksh93 here, but pdksh/OpenBSD ksh and mksh carry the same name.
#
# Both are read as the UNION of every model listed, and every model's candidate
# script is scanned. That is the conservative direction for a gate: a model that
# consumes one token too many swallows the script (a silent miss), and one that
# consumes too few calls an option's operand the script (also a miss), so only
# taking every model's answer is safe in both directions. The cost is
# over-detection on an invocation the reader's shell would have rejected.
#
# `dash` appears in both unions as the MINIMAL POSIX reading — it is the one
# measured map in which only `-o` takes an operand — so an unmeasured `ksh`
# whose `-T`/`-R` are bare still yields its script as a candidate. That is a
# modelling choice made from a MEASURED map, not an arity asserted for a shell
# this host cannot run: mksh, pdksh and busybox ash are NOT installed here and
# nothing in SHELL_OPTION_ARITY claims to describe them (see the scope note in
# the module docstring). Adding a guessed map for them would be the opposite
# trade — an unmeasured claim in a table whose whole standard is measurement.
SHELL_MODELS = {
    "bash": ("bash",),
    "dash": ("dash",),
    "zsh":  ("zsh",),
    "ksh":  ("ksh93", "dash"),
    "sh":   ("bash", "dash", "zsh", "ksh93"),
}
SHELLS = set(SHELL_MODELS)
KNOWN_PROGRAMS = {VCS, FORGE} | SHELLS

# Execution carriers this gate understands, each with its real argument shape:
#   "value"      — options whose MANDATORY operand is the following token (an
#                  attached operand, -n5 / --adjustment=5, is one token and
#                  consumes nothing extra, so only an exact match takes two);
#   "positional" — how many bare operands come before the command (timeout's
#                  duration).
# An option with an OPTIONAL operand (env --block-signal[=SIG], GNU xargs
# --max-lines[=N]) must NOT be listed: as a bare flag it consumes nothing, and
# listing it would swallow the program that follows — a hard MISS.
#
# The rule is to model each option's REAL arity, which is also the safer choice
# in both directions. Listing a genuinely mandatory-operand option is safe
# because the form it "swallows" (`xargs --process-slot-var <vcs> <publish>`)
# really does consume the program name as that option's value and never
# publishes; NOT listing one is safe because the stray operand becomes the head
# of the segment and the prose pass still reports the form. Where a tool's arity
# looks ambiguous across builds, check what the tool actually does rather than
# guessing a "safe" direction: this table once read sudo's -h as bare on that
# reasoning and the reasoning was simply wrong (see that entry).
WRAPPER_SPEC = {
    "command":  {"value": set(), "positional": 0},
    "builtin":  {"value": set(), "positional": 0},
    "nohup":    {"value": set(), "positional": 0},
    "setsid":   {"value": set(), "positional": 0},
    "nice":     {"value": {"-n", "--adjustment"}, "positional": 0},
    # -P/--pgid and -u/--uid take an operand exactly as -p/--pid does.
    "ionice":   {"value": {"-c", "--class", "-n", "--classdata", "-p", "--pid",
                           "-P", "--pgid", "-u", "--uid"},
                 "positional": 0},
    "stdbuf":   {"value": {"-i", "--input", "-o", "--output", "-e", "--error"},
                 "positional": 0},
    "exec":     {"value": {"-a"}, "positional": 0},
    "time":     {"value": {"-f", "--format", "-o", "--output"}, "positional": 0},
    "timeout":  {"value": {"-s", "--signal", "-k", "--kill-after"},
                 "positional": 1},
    # -i / --replace / -l / --max-lines have OPTIONAL operands and take
    # nothing; -I and -L are their mandatory-operand forms. (GNU findutils
    # declares --max-lines optional_argument, so it belongs with -l and NOT
    # with -L: listing it swallowed the program that followed.)
    # -J / -R / -S are BSD-only (see the platform-union note below). Observed on
    # Darwin: `xargs -J <name> <utility>` consumes <name> as the replacement
    # string and runs <utility>, and `xargs -I{} -R <name>` rejects <name> by
    # name ("-R <name>: invalid"), which is what proves it consumed it.
    "xargs":    {"value": {"-a", "--arg-file", "-d", "--delimiter", "-E",
                           "-I", "-J", "-L", "-n", "--max-args",
                           "-P", "--max-procs", "-R", "-S",
                           "-s", "--max-chars",
                           "--process-slot-var"},
                 "positional": 0},
    # -h DOES take an operand: sudo documents `-h host`, and its parser reaches
    # past the optional-argument rule to take the next non-option token as the
    # host — so reading it as bare MISSED `sudo -h <host> <vcs> <publish>`.
    # Consuming is correct on a help-only build too: there the invocation
    # prints help and executes nothing, so swallowing the token misses nothing.
    # -a/--auth-type and -c/--login-class take an operand wherever the platform
    # enables them.
    "sudo":     {"value": {"-u", "--user", "-g", "--group", "-C", "--close-from",
                           "-D", "--chdir", "-h", "--host", "-p", "--prompt",
                           "-R", "--chroot", "-r", "--role", "-t", "--type",
                           "-T", "--command-timeout", "-U", "--other-user",
                           "-a", "--auth-type", "-c", "--login-class"},
                 "positional": 0},
    # doas: -a <style> selects the authentication style, -C <config>, -u <user>.
    "doas":     {"value": {"-a", "-u", "-C"}, "positional": 0},
    # -P is BSD-only (`env -P utilpath`, in the Darwin usage string and manual).
    # -L/-U (`user[/class]`) are FreeBSD-only, per FreeBSD env(1) since 13.0 —
    # DOCUMENTED, not observed: Darwin's env rejects -L ("illegal option") and
    # its usage string is `[-0iv] [-C workdir] [-P utilpath] [-S string]
    # [-u name]`, so no build on this machine has them.
    "env":      {"value": {"-u", "--unset", "-C", "--chdir", "-a", "--argv0",
                           "-P", "-L", "-U"},
                 "positional": 0},
}
WRAPPERS = set(WRAPPER_SPEC)

# PLATFORM UNION, stated because the table above says "real arity": these sets
# are the union over the implementations a reader may be running, not any one
# platform's option table. `xargs -J/-R/-S` and `env -P` exist on BSD/Darwin and
# not in GNU coreutils/findutils, `env -L/-U` on FreeBSD only; `ionice` and GNU
# `xargs --process-slot-var` exist on GNU and not on BSD, and GNU `xargs
# -e/-i/-l` likewise (Darwin's xargs answers "invalid option"). The union can
# only OVER-detect a carrier option, never under-detect one: on the platform
# that lacks the option the invocation is a usage error that executes nothing,
# so consuming its operand misses nothing real. Where two platforms disagree on
# an option's ARITY rather than its existence, the reading that consumes MORE
# wins, for the same reason.


# carrier -> the SHORT options whose operand is OPTIONAL. getopt takes an
# attached remainder for these and NEVER the following token, so they terminate
# a cluster without consuming anything more. Modelling them is what keeps the
# walk from reporting a command the invocation never runs: observed on GNU
# findutils 4.10, `xargs -lE …` answers `invalid number "E" for -l option` and
# executes nothing, while `xargs -teX echo FOO` traces `echo FOO hi` and
# `xargs -tiX echo FOO` traces `echo FOO` — in both, the letter took the
# attached remainder and the emitter is the program. These are GNU-only: BSD
# xargs answers "invalid option" for all three.
WRAPPER_OPTIONAL_SHORT_CHARS = {"xargs": "eil"}

# env's split-string operand IS the head of the executed argv: it is recursed
# into TOGETHER WITH the remaining operands, which are its arguments.
ENV_SPLIT_OPTS = {"-S", "--split-string"}
ENV_SPLIT_CHAR = "S"


def _short_value_chars(opts) -> str:
    """The single-letter options of `opts` that take an operand, as a string.

    Short options CLUSTER (getopt(3), and pflag for the forge CLI): within one
    dash token the FIRST operand-taking letter consumes the rest of the token,
    or — when it ends the token — the following token. So the letter set, not
    the exact option spelling, is what a cluster has to be read against."""
    return "".join(sorted({o[1] for o in opts
                           if len(o) == 2 and o[0] == "-" and o[1] != "-"}))


# carrier -> its operand-taking SHORT letters, derived from the arity table
# above so the two can never disagree (the selftest pins the derivation against
# a hand-written letter table). Observed cluster behaviour, with printf/echo as
# a harmless stand-in for the program: BSD+GNU `env -vu FOO printf …`, BSD `env
# -vP /usr/bin printf …`, GNU `xargs -tE printf printf …`, BSD `xargs -tJ printf
# printf …`, BSD `time -po printf printf …`, bash `exec -ca printf printf …` and
# `sudo -nu printf …` ("unknown user printf") all consume the following token
# and reach the program behind it.
WRAPPER_SHORT_VALUE_CHARS = {name: _short_value_chars(spec["value"])
                             for name, spec in WRAPPER_SPEC.items()}
# -S is not in env's value set — its operand is a command line, not a plain
# value — but it clusters exactly like one, and the first operand-taking letter
# still wins: `-Sx` and `-vSx` split on "x", while `-uSx` unsets a variable
# named "Sx" and splits nothing. Verified against BSD env and GNU coreutils 9.7:
# `env -Sprintf FMT ARG` and `env -vSprintf FMT ARG` both execute printf,
# `env -uSprintf printf FMT ARG` does not.
WRAPPER_SHORT_VALUE_CHARS["env"] = _short_value_chars(
    WRAPPER_SPEC["env"]["value"] | {"-" + ENV_SPLIT_CHAR})
# `eval` concatenates its arguments and executes the result.
EVAL_WRAPPERS = {"eval"}
# Programs whose quoted arguments are text, never a command line. Every OTHER
# program's double-quoted arguments are scanned as command lines, which is what
# catches a carrier this table does not know (ssh host "<cmd>") and prose that
# spells a command inside quotes.
NON_EXECUTING = {"echo", "printf", "true", "false"}

# Carriers that hand a STRING to a shell somewhere else — on the far side of a
# connection, or under another user. They are here because one of their OPTIONS
# carries a command line inside a SINGLE argv token, which no other pass of this
# gate can see: the quoted-operand pass re-reads `ProxyCommand=<vcs> <publish>`
# as a command line and gets the SHELL's reading of it — an assignment prefix
# `ProxyCommand=<vcs>` followed by a program named `<publish>` — which is
# perfectly clean. Every spelling below was a MISS until this table existed, the
# plain `-o ProxyCommand=<cmd>` among them, and what looked like coverage was
# incidental: `-o 'ProxyCommand = <cmd>'` flags only because the SPACES in it
# leave the two words separate in the quoted-span re-read.
#
# LOCKSTEP with the runtime egress guard's `STRING_EXEC_SPEC`, and deliberately
# only the half that ADDS detection. Two things there are NOT mirrored:
#   · its `PROSE_EXEMPT |= STRING_EXEC_CARRIERS`. A runtime guard can exempt a
#     carrier once it has the carrier's real grammar; a documentation lint must
#     not, because `<carrier> host <vcs> <publish>` teaches the mechanic whether
#     or not this table understands the carrier. So these names stay OUT of
#     PROSE_EXEMPT and the prose pass still runs on them.
#   · its `joins_operands` reconstruction (the operands after the destination,
#     joined into one remote command line). The prose pass already reports that
#     shape more strictly than the reconstruction would, so mirroring it would
#     add no verdict and one more producer to the walk's termination argument.
# `destinations` IS mirrored, and it is load-bearing in the FALSE direction:
# options end at the destination for the carriers that join their trailing
# operands, so `<carrier> host echo -o "ProxyCommand=<cmd>"` — where the `-o` is
# an argument to the REMOTE echo — must not be read as a local option.
SSH_CMD_KEYWORDS = {"proxycommand", "remotecommand", "localcommand",
                    "knownhostscommand"}
# ssh_config's OWN separator whitespace, not Python's. `str.isspace()` also
# accepts VT and FF and OpenSSH does not — measured on the guard's side, an
# option whose keyword and value are separated by a VT is rejected outright
# ("Bad configuration option: proxycommand\013<vcs>"), so reading one as a
# separator would manufacture a command line the tool never runs. CR IS
# accepted (`ssh -G -o $'ProxyCommand\r<cmd>'` resolves to `proxycommand <cmd>`).
SSH_SEPARATOR_WS = " \t\r\n"
_SSH_VALUE_CHARS = "BbcDEeFIiJLlmOoPpQRSWw"
# Options that make the carrier PRINT SOMETHING AND EXIT, so nothing it was
# also told to run ever runs. Same shape as VCS_TERMINAL_OPTS, and the same
# direction of error without it: a command line reported on an invocation that
# executes nothing. MEASURED on OpenSSH 9.9p2 — `ssh -V -o <keyword-form>
# <host>` prints the version and exits, and `ssh -Q cipher -o <keyword-form>
# <host>` prints the query answer and exits. `su`'s are DOCUMENTED, not
# measured: this host's `su` is the BSD one and rejects long options outright,
# so every long entry in its row (including the command options themselves)
# comes from util-linux's manual and parser rather than from a run here.
_SSH_TERMINAL_OPTS = frozenset({"-V", "-Q"})
STRING_EXEC_SPEC = {
    "ssh": {"value_chars": _SSH_VALUE_CHARS, "long_value": frozenset(),
            "cmd_opts": {"-o"}, "cmd_keywords": SSH_CMD_KEYWORDS,
            "terminal": _SSH_TERMINAL_OPTS, "destinations": 1},
    "slogin": {"value_chars": _SSH_VALUE_CHARS, "long_value": frozenset(),
               "cmd_opts": {"-o"}, "cmd_keywords": SSH_CMD_KEYWORDS,
               "terminal": _SSH_TERMINAL_OPTS, "destinations": 1},
    # No command-bearing option at all: its row exists so the SET of carriers
    # matches the guard's, and so that adding one later is a table edit here
    # rather than a new branch.
    "rsh": {"value_chars": "kl", "long_value": frozenset(),
            "cmd_opts": frozenset(), "cmd_keywords": frozenset(),
            "terminal": frozenset(), "destinations": 1},
    # `su` takes its command from `-c` WHEREVER it appears, including after the
    # user name, so its option walk must not stop at an operand — `destinations`
    # None. Its trailing operands are the shell's arguments, not a command line.
    # `--session-command` is a second command-bearing option with NO short
    # spelling (util-linux's `su`; its parser assigns the operand to the same
    # command slot `-c` fills). DOCUMENTED, like the rest of this row.
    "su": {"value_chars": "cgGsw",
           "long_value": {"--command", "--session-command", "--shell",
                          "--group", "--supp-group",
                          "--whitelist-environment"},
           "cmd_opts": {"-c", "--command", "--session-command"},
           "cmd_keywords": frozenset(),
           "terminal": frozenset({"-h", "--help", "-V", "--version"}),
           "destinations": None},
}
STRING_EXEC_CARRIERS = set(STRING_EXEC_SPEC)

# Shell grammar words that can precede the real program in a command segment.
CONTROL_WORDS = {"if", "then", "else", "elif", "fi", "while", "until", "do",
                 "done", "case", "esac", "in", "for", "select", "function",
                 "coproc"}

# A segment whose head is NONE of these is prose (or an unknown program), and
# is additionally scanned for a forbidden form spelled later in it. Anything in
# here has already been analysed by its own rule — and the text-emitters are
# exempt by contract: `echo <vcs> <publish>` prints a string.
# The VCS and the forge CLI are deliberately NOT here: "<vcs> users must never
# run <vcs> <publish>" has a known program at its head and its own rule finds
# nothing, so the prose pass must still see the rest of the line. Shells are
# exempt because `sh -c <vcs> <publish>` really does pass the second word as $0.
PROSE_EXEMPT = ({""} | SHELLS | CONTROL_WORDS | NON_EXECUTING
                | WRAPPERS | EVAL_WRAPPERS)

# git global options that consume the following token as their value. Every
# other dash token — including the options that accept an ATTACHED operand ONLY
# (--exec-path[=<path>], which bare prints the path and exits, and
# --super-prefix=<path>) — is skipped as a lone flag, so the subcommand behind
# a bare one is still reached rather than swallowed.
VCS_VALUE_OPTS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace",
                  "--config-env", "--shallow-file", "--attr-source"}
# Globals that, in their BARE form, make the VCS print something and EXIT — no
# subcommand ever runs, so a word behind one of them is not a command. Observed
# on 2.54.0: the exec-path global prints the path and exits 0, and the
# super-prefix global is rejected outright as an unknown option, that option
# having been removed. Skipping them as "lone flags whose subcommand is still
# reached" described neither.
#
# Only the exact BARE token is terminal here, and what that means differs by
# option — MEASURED on 2.54.0, `<global>=x status`:
#   · the exec-path global really does continue ("On branch master"), so its
#     attached form is a value and the subcommand behind it runs;
#   · every other entry answers "unknown option" and runs NOTHING — the
#     super-prefix global, the version and help globals in both spellings, and
#     the three path queries.
# So on those the gate reports a form the tool would never run. That is
# OVER-detection, it is the direction this gate is deliberately biased in, and
# it matches the runtime rule table exactly — which is why the reading is not
# narrowed here. An earlier version of this comment said every attached form
# sets a value and the subcommand does run; that is true of ONE entry, and is
# corrected rather than left standing.
VCS_TERMINAL_OPTS = {"--exec-path", "--super-prefix", "--version", "-v",
                     "--help", "-h", "--man-path", "--html-path",
                     "--info-path"}
# Dash options that may precede the forge CLI's SUBCOMMAND and consume the
# following token, so that operand is not mistaken for the subcommand. This is
# deliberately wider than the forge CLI's true global flag set — several of
# these are command-level flags — because over-listing here costs only
# non-existent invocations while under-listing would read an operand as the
# subcommand. Flags AFTER the subcommand are handled by that subcommand's rule.
FORGE_VALUE_OPTS = {"-R", "--repo", "--hostname", "-H", "--header"}
FORGE_SHORT_VALUE_CHARS = _short_value_chars(FORGE_VALUE_OPTS)
# A family ACTION's own operand-taking options. This table is the OPPOSITE
# direction from the one above and must be read with the opposite bias: an
# option missing from it has its VALUE counted as a positional, and for the
# sync action the positional IS the condition, so the miss is a FALSE FINDING
# on a command that touches no remote. An option wrongly IN it swallows the
# destination and the finding is LOST, which is the direction that ships a
# document teaching the retired mechanic. So model the REAL arity and nothing
# more: only options observed to take an operand belong here.
#
# OBSERVED from the sync action's own help on forge CLI 2.96.0: `-b/--branch
# <string>` and `-s/--source <string>` each take one; its force flag takes
# none. The create action's own options are deliberately absent — its condition
# is a FLAG rather than a positional, so an option value read as a positional
# changes no verdict there, and listing an option that takes none would be the
# harmful direction for no gain.
FORGE_ACTION_VALUE_OPTS = {
    (REPO, "sync"): {"-b", "--branch", "-s", "--source"},
}
FORGE_ACTION_SHORT_VALUE_CHARS = {
    key: _short_value_chars(opts)
    for key, opts in FORGE_ACTION_VALUE_OPTS.items()
}
# The forge CLI's raw-API subcommand parses with pflag, which clusters short
# options exactly as getopt does. These are ALL of its operand-taking short
# options, not just the mutating ones — the non-mutating letters have to be here
# too, because a letter earlier in the cluster swallows the rest of it and the
# mutation letter behind it is then an OPERAND, not a flag. Observed on forge
# CLI 2.96: `-iX POST`, `-iXPOST`, `-iF a=b` and `-iFa=b` all issue a POST, while
# `-qX POST <path>` makes "X" the jq query and leaves two positionals
# ("accepts 1 arg(s), received 2") — no method flag at all.
#   -F --field  -H --header  -X --method  -f --raw-field
#   -p --preview  -q --jq  -t --template   (-i --include takes none)
API_SHORT_VALUE_CHARS = "FHXfpqt"

# The SHELLS parse their invocation options with their own hand-rolled parsers,
# NOT getopt, and — unlike the carriers — the four do not agree with each other.
# ONE arity model for all of them is therefore not a missing table entry but a
# wrong mechanism, so each shell gets its own letter map. THREE arities occur:
#
#   SHELL_NEXT              the operand is ALWAYS the following argv element; an
#                           attached remainder is NOT the operand, so the
#                           cluster continues THROUGH the letter. bash `-o`/`-O`
#                           and dash `-o`.
#   SHELL_ATTACHED_OR_NEXT  an attached remainder IS the operand and TERMINATES
#                           the cluster; only a letter that ENDS its token takes
#                           the following element. zsh `-o`, ksh93 `-T`/`-R`.
#   SHELL_ATTACHED_OR_NEXT_NONOPT
#                           the same, except the SEPARATE operand is OPTIONAL:
#                           it is taken only when the following token is not
#                           itself an option. ksh93 `-o` alone. Measured:
#                           `ksh -o -c <script>` prints the option list and then
#                           RUNS <script> — the `-o` took nothing and the walk
#                           reached `-c` — and so do `ksh +o -c <script>`,
#                           `ksh -o +x -c <script>` and `ksh -c -o -x <script>`,
#                           while `ksh -o errexit -c <script>` takes "errexit"
#                           normally. Every other shell CONSUMES the `-c` there:
#                           bash "-c: invalid option name", dash "Illegal option
#                           -o -c", zsh "no such option: -c". ksh93's `-T`/`-R`
#                           stay mandatory — they take a numeric mask and a
#                           scriptname, and over-consuming there cannot hide a
#                           script that runs, since the invocation is rejected
#                           either way.
#
# A letter absent from a shell's map is BARE. That is not a default assumption:
# every ASCII letter was swept on each shell as
# `<shell> -c -<L> 'printf OPERAND' 'printf SCRIPT'` — the option operand and
# the script print different words, so which one runs says whether `-L`
# consumed a token — and no other operand-taking letter exists on any of them.
# ksh93 additionally prints its own getopt string when handed an unknown long
# option, `cilrsDER:abefhkmno:prtuvxBCGH`, in which only `o:` and `R:` take an
# operand (its `-T` is outside that string and was measured directly).
#
# Each key here is an IMPLEMENTATION, not a shell name: `ksh93` is the measured
# AT&T ksh and is one of the two models the NAME `ksh` is read under (see
# SHELL_MODELS). Every map is what was MEASURED on this host and claims nothing
# about a shell that is not installed here — the unprobed implementations and
# what the union does about them are stated in the module docstring's scope
# section.
#
# Observed on this host — bash 3.2.57(1) (which is also its /bin/sh), dash,
# zsh 5.9, ksh "sh (AT&T Research) 93u+ 2012-08-01" — with `printf SENTINEL` as
# the script, i.e. the shell really executed it:
#
#   * bash `-O` CONSUMES: `bash -O -c <script>` answers "invalid shell option
#     name -c" (the -c was eaten), while `bash -O extglob -c <script>` and
#     `bash -Oc extglob <script>` both run <script>. zsh `-O` does NOT:
#     `zsh -O -c <script>` runs <script>, and `zsh -O extglob -c <script>`
#     answers "can't open input file: extglob" — nothing was consumed. dash and
#     ksh reject `-O` outright ("Illegal option" / "unknown option").
#   * ATTACHED `-o<name>`: zsh and ksh accept it — `zsh -oerrexit -c <script>`
#     and `ksh -oerrexit -c <script>` run <script> — and it ends the cluster:
#     `zsh -oc errexit <script>` answers "no such option: c", so there is no
#     `-c` at all. bash and dash reject the attached form: `bash -oerrexit -c
#     <script>` answers "-c: invalid option name" and `dash` "Illegal option -o
#     -c", i.e. `-o` took the FOLLOWING token and "errexit" clustered as the
#     bare letters e,r,r,e,x,i,t. `bash -Oextglob` likewise answers "-g:
#     invalid option".
#   * ksh93 `-T` has a MANDATORY operand, attached or separate: `-T` alone
#     answers "numeric mask argument expected", while `ksh -c -T 0 <script>`,
#     `ksh -c -T0 <script>` and `ksh -c -xT 0 <script>` all run <script>.
#     bash's and zsh's `-T` is bare: `bash -c -T 0 <script>` runs the script
#     `0` and leaves <script> as $0.
#   * ksh93 `-R` consumes too (`R:` above; `ksh -c -R <script>` answers "-c
#     requires argument" because -R ate the script). It is mutually exclusive
#     with -c, so consuming it can hide nothing that runs.
#   * SEPARATE `-o <name>`, and the `+` form of every letter, behave identically
#     on all four. `+c` runs the script on all four as well (re-measured:
#     `<shell> +c 'printf SCRIPT' P1` prints SCRIPT on bash, dash, zsh and ksh).
#
# This table answers only "where does an option's operand end". Whether there
# is a script at all when NO `-c` appears anywhere is a separate per-model
# question, and the shells diverge on that too — see SHELL_FIRST_OPERAND. Every
# probe recorded above put a `-c` somewhere in the invocation, which is exactly
# why that divergence went unseen for ten review rounds.
SHELL_NEXT = "next"
SHELL_ATTACHED_OR_NEXT = "attached-or-next"
SHELL_ATTACHED_OR_NEXT_NONOPT = "attached-or-next-nonoption"
SHELL_OPTION_ARITY = {
    "bash": {"o": SHELL_NEXT, "O": SHELL_NEXT},
    "dash": {"o": SHELL_NEXT},
    "zsh":  {"o": SHELL_ATTACHED_OR_NEXT},
    "ksh93": {"o": SHELL_ATTACHED_OR_NEXT_NONOPT,
              "T": SHELL_ATTACHED_OR_NEXT,
              "R": SHELL_ATTACHED_OR_NEXT},
}
SHELL_COMMAND_CHAR = "c"
# Per shell, the LONG invocation options that take a separate operand. An
# unknown long option consumes nothing, which is why bare `--` is handled
# explicitly. Observed: `bash --init-file /dev/null -c <script>` runs <script>
# (and bash 3.2 rejects the `--rcfile=<x>` form); `zsh --emulate sh -c <script>`
# runs <script> (and rejects `--emulate=sh`); dash has no long options at all
# ("Illegal option --"), and no ksh93 long option takes a separate operand
# ("--umask=0" is rejected, "--rc" is bare). DELIBERATE over-detection: bash and
# zsh accept these only BEFORE `-c` ("--: invalid option" / "--emulate: must
# precede other options"), and this walk consumes them in either position —
# reading them as bare after `-c` would take the operand for the script and
# lose the real one, and the invocation it over-reports executes nothing.
SHELL_LONG_VALUE_OPTS = {
    "bash": {"--rcfile", "--init-file"},
    "dash": set(),
    "zsh":  {"--emulate"},
    "ksh93": set(),
}

# A BARE `+` is an option-introducer with no letters behind it, and the four
# shells split on it exactly as they split on the letter arities — so it is a
# per-model entry too, not a global rule. Measured with `printf SCRIPT`:
#
#   * bash and dash SKIP it and keep reading options, so
#     `bash + -c <script>` and `dash + -c <script>` RUN <script>;
#   * zsh and ksh93 treat it as END-OF-OPTIONS, so `zsh + -c <script>` and
#     `ksh + -c <script>` do NOT run <script>. The MECHANISM differs between
#     those two and the difference matters: on zsh the `-c` behind the `+`
#     became the script FILE ("command not found"), while on ksh93 it became
#     the first OPERAND and was run as a COMMAND — `ksh + -c <script>` answers
#     "/bin/ksh: -c: not found", and `ksh + + -c <script>` answers "+: not
#     found", each naming the token it tried to execute. `ksh + <cmd>` runs
#     <cmd>. (SHELL_FIRST_OPERAND carries that rule; an earlier version of this
#     note read both shells as the zsh case because the two error texts look
#     alike.)
#
# Both readings agree once `-c` has been seen: `<shell> -c + <script>` runs
# <script> on all four, because a skipped `+` and an options-terminating `+`
# both leave <script> as the first operand after it.
#
# A bare `-` is END-OF-OPTIONS on all four (`<shell> - -c <script>` runs no
# <script> anywhere, while `<shell> -c - <script>` runs it everywhere), so it
# needs no per-model entry and is handled with `--`. On ksh93 the token behind
# it is a command line for the same reason a bare `+`'s is.
#
# These two plus `--` are the option-introducer tokens that carry no letters
# and have their own per-model rule. `++` and `+-` are NOT "rejected by every
# shell", which this note used to say and which is false in both halves:
# `+-` is end-of-options on zsh and parsed through on ksh93 (SHELL_PLUS_DASH,
# below, exists for exactly that), and `++` is rejected only by bash, dash and
# zsh — `ksh ++ <cmd>` runs <cmd>, and `ksh ++ -c <cmd>` answers "-c: not
# found", i.e. ksh93 carries no letters out of it and runs the token behind it.
# `++` deliberately gets NO per-model rule: it reaches the cluster walk as a
# no-operand token, so the walk keeps reading options past it. That is exact
# for `ksh ++ <cmd>` (the flag then resolves <cmd>, which really runs) and
# INEXACT but safe for `ksh ++ -c <cmd>` — the walk answers <cmd> where ksh93
# actually runs `-c`, i.e. it reports a string the invocation never executes,
# never the reverse. Under the three rejecting models nothing executes at all,
# so their reading of it over-detects for the same harmless reason. Stated
# rather than special-cased: a rule per token shape is what this file already
# learned not to add without a measurement that needs it.
# A `+` token whose body contains a `-` is a THIRD shape of plus token, and the
# shells split on it too — it is neither a bare `+` nor a plain cluster.
# Measured with `printf SCRIPT`:
#
#   * ksh93 PARSES THROUGH the dashes, i.e. they are ignored and the remaining
#     letters are an ordinary cluster: `ksh +- -c <s>`, `ksh +-- -c <s>`,
#     `ksh +--- -c <s>`, `ksh +-c <s>`, `ksh +-x -c <s>`, `ksh -c +-x <s>` and
#     `ksh +-o errexit -c <s>` ALL run <s>. (So does `ksh -x- -c <s>`, which the
#     minus path already handles, an unknown body character being bare.)
#   * zsh accepts EXACTLY `+-` and reads it as end-of-options — `zsh -c +- <s>`
#     runs <s>, `zsh +- -c <s>` does not (the `-c` became the script file) —
#     while every longer form is rejected: `+--` → "no such option: _",
#     `+-c` → "no such option: c", `+-x` → "no such option: x".
#   * bash and dash reject every one of them ("+-: invalid option" / "Illegal
#     option --"), so nothing executes under those models at all.
SHELL_PLUSDASH_REJECT = "reject"
SHELL_PLUSDASH_BARE_ENDS_OPTIONS = "bare-ends-options"
SHELL_PLUSDASH_PARSE_THROUGH = "parse-through"
SHELL_PLUS_DASH = {
    "bash": SHELL_PLUSDASH_REJECT,
    "dash": SHELL_PLUSDASH_REJECT,
    "zsh":  SHELL_PLUSDASH_BARE_ENDS_OPTIONS,
    "ksh93": SHELL_PLUSDASH_PARSE_THROUGH,
}

SHELL_PLUS_SKIP = "skip"
SHELL_PLUS_ENDS_OPTIONS = "end-options"
SHELL_BARE_PLUS = {
    "bash": SHELL_PLUS_SKIP,
    "dash": SHELL_PLUS_SKIP,
    "zsh":  SHELL_PLUS_ENDS_OPTIONS,
    "ksh93": SHELL_PLUS_ENDS_OPTIONS,
}

# What a model does with its FIRST OPERAND when NO `-c` was seen. This is a
# per-model property because the shells diverge on it too, and the divergence
# is the widest one in this file: it needs no option spelling at all.
#
#   SHELL_FIRST_OPERAND_FILE     the operand is a script FILE and there is
#                                nothing to scan. bash, dash, zsh.
#   SHELL_FIRST_OPERAND_COMMAND  the operand is opened as a script file FIRST
#                                and, when that open fails, its TEXT is
#                                executed as a command line. ksh93.
#
# Measured on ksh "Version AJM 93u+ 2012-08-01" (/bin/ksh), each observed to
# EXECUTE — no `-c` anywhere in any of them:
#
#   * `ksh 'printf SCRIPT'` prints SCRIPT, and so do `ksh -x …` (with the
#     xtrace line), `ksh -p …`, `ksh -o errexit …`, `ksh -T 0 …`, `ksh -- …`,
#     `ksh - …`, `ksh + …`, `ksh ++ …` and `ksh +- …`. With the real forbidden
#     form in place of the printf — `ksh '<vcs> <publish> origin main'` — the
#     remote mutation really happens: the error came back FROM the VCS itself
#     ("not a repository", exit 128), not from the shell.
#   * The operand is a full command LINE, not a program name: `ksh 'echo A;
#     echo B'`, `ksh 'true && echo AND-RAN'`, `ksh 'echo HI > /tmp/f'` and
#     `ksh 'VAR=1 echo VARRAN'` all take effect.
#   * It is a FALLBACK, not a blanket rule, and the file wins: in a directory
#     holding a file literally named `echo HI`, `ksh 'echo HI'` runs that FILE.
#     A single-word operand that PATH resolves to a real file is read as that
#     file — `ksh 'echo' HELLO` answers "echo: cannot execute [Exec format
#     error]" (it tried to source /bin/echo) — while `ksh ':'` and `ksh
#     'echo;'` reach the fallback and run.
#   * The operands BEHIND the first are APPENDED to the command line and are
#     also $1…$n. ksh93 does it by running the text with a literal `"$@"`
#     after it, which its own error message proves: `ksh 'if true; then echo
#     T; fi' P1` answers `syntax error at line 1: `"$@"' unexpected`. So they
#     arrive as WORDS on the LAST simple command, never as syntax —
#     `ksh 'echo A' '|' wc -l` prints "A | wc -l" and `ksh 'echo A' ';' 'echo
#     B'` prints "A ; echo B". `_shell_scripts` reproduces the WORDS: the
#     first operand as SOURCE, each appended one re-serialized as one quoted
#     WORD. THIS IS LOAD-BEARING TWICE OVER. `ksh X=1 <vcs> <publish> origin
#     main` publishes, and reading only the first operand resolves it to
#     "X=1" and reports nothing; and an appended operand that is itself
#     multi-word must keep its boundary, because `ksh 'sh -c' '<vcs>
#     <publish>'` and `ksh '<vcs> -C' '/tmp/no such' <publish>` BOTH publish
#     (measured with --version) and BOTH scanned clean while the walk
#     re-joined the operands as raw source — the nested -c script lost its
#     subcommand to $0, and the spaced path split into two tokens.
#   * It survives the `sh` spelling, which is why the `sh` union carries it:
#     ksh93 invoked through a symlink named `sh` still runs `sh 'git
#     --version'` (observed: real git output). `sh` IS ksh93 on shipped
#     systems (Solaris 11), so this is a reachable reading of the NAME, not a
#     hypothetical one.
#
# The other three were measured NOT to do it: `bash|dash|zsh 'printf SCRIPT'`
# answer "No such file or directory" / "cannot open" / "can't open input file"
# and execute nothing.
#
# This flag can only ADD a candidate script, never move one, so it cannot hide
# a form. It DOES over-report three measured shapes, stated rather than
# special-cased — one rule for every instance is what keeps this honest:
# `ksh -s <cmd>` reads the script from stdin and leaves <cmd> a positional
# parameter; `ksh -T -c <cmd>` and `ksh -Tc <cmd>` are rejected outright
# ("numeric mask argument expected"); `ksh -R <file> <cmd>` and `ksh -Rc
# <cmd>` write a cross-reference and execute nothing. Each is an invocation no
# shipped skill would contain, and each errs toward reporting.
SHELL_FIRST_OPERAND_FILE = "script-file"
SHELL_FIRST_OPERAND_COMMAND = "command-line"
SHELL_FIRST_OPERAND = {
    "bash": SHELL_FIRST_OPERAND_FILE,
    "dash": SHELL_FIRST_OPERAND_FILE,
    "zsh":  SHELL_FIRST_OPERAND_FILE,
    "ksh93": SHELL_FIRST_OPERAND_COMMAND,
}

SEPARATOR_CHARS = ";|&`()\n"
LEAD_TRIM = "`*_\"'([{"
TAIL_TRIM = "`*_\"'.,;:!?)]}"


# --------------------------------------------------------------------------
# normalization


def strip_markdown_prefix(text: str) -> str:
    """Drop leading Markdown blockquote / bullet / checklist / numbered-list /
    heading markers, repeatedly, so a marked-up line parses as the command it
    spells. A blockquote marker needs no following space (CommonMark)."""
    s = text
    while True:
        t = s.lstrip(" \t")
        if t[:1] == ">":
            s = t[1:]
            continue
        if t[:1] in ("-", "*", "+") and t[1:2] in (" ", "\t"):
            s = t[2:]
            continue
        k = 0
        while k < len(t) and t[k].isdigit():
            k += 1
        if 0 < k <= 9 and t[k:k + 1] in (".", ")") and t[k + 1:k + 2] in (" ", "\t"):
            s = t[k + 2:]
            continue
        if t[:1] == "[" and t[1:2] in (" ", "x", "X") and t[2:3] == "]" \
                and t[3:4] in ("", " ", "\t"):
            s = t[4:]
            continue
        k = 0
        while k < len(t) and t[k] == "#":
            k += 1
        if 0 < k <= 6 and t[k:k + 1] in (" ", "\t"):
            s = t[k + 1:]
            continue
        return t


def ends_with_open_backslash(text: str) -> bool:
    """True when the line ends in an ODD run of backslashes — the shell joins
    it with the next line. An even run is an escaped backslash: line ends."""
    k = 0
    while k < len(text) and text[len(text) - 1 - k] == "\\":
        k += 1
    return k % 2 == 1


def join_continuations(lines: list[str]) -> list[tuple[int, str]]:
    """[(first physical line number, logical line)] with continuations joined."""
    out: list[tuple[int, str]] = []
    i = 0
    n = len(lines)
    while i < n:
        start = i
        buf = lines[i]
        while ends_with_open_backslash(buf) and i + 1 < n:
            buf = buf[:-1] + lines[i + 1]
            i += 1
        out.append((start + 1, buf))
        i += 1
    return out


def trim_token(tok: str) -> str:
    """Trim Markdown emphasis / quoting / sentence punctuation off a token."""
    s = tok
    while s and s[0] in LEAD_TRIM:
        s = s[1:]
    while s and s[-1] in TAIL_TRIM:
        s = s[:-1]
    return s


MARKUP_CHARS = "`*"


def _scan_destination(text: str, k: int, n: int) -> int:
    """Consume a CommonMark link destination at `k`; return the index just past
    it, or -1 if it does not close. Two shapes: `<…>`, which may hold UNBALANCED
    parentheses, and a bare run that ends at whitespace or at the `)` closing
    the link, with parentheses balanced. A quote is ORDINARY TEXT here — a title
    is only a title after destination-separating whitespace — so an apostrophe
    in a URL cannot swallow the rest of the line."""
    if k < n and text[k] == "<":
        k += 1
        while k < n:
            c = text[k]
            if c == "\\" and k + 1 < n:
                k += 2
                continue
            if c == ">":
                return k + 1
            if c == "\n":
                return -1
            k += 1
        return -1
    depth = 0
    while k < n:
        c = text[k]
        if c == "\\" and k + 1 < n:
            k += 2
            continue
        if c.isspace():
            break
        if c == "(":
            depth += 1
        elif c == ")":
            if not depth:
                break                     # this one closes the link
            depth -= 1
        k += 1
    return k if not depth else -1


def _scan_title(text: str, k: int, n: int) -> int:
    """Consume an optional link title — `"…"`, `'…'` or `(…)`, and ONLY after
    whitespace separating it from the destination. Returns `k` unchanged when
    there is no well-formed title."""
    j = k
    while j < n and text[j].isspace():
        j += 1
    if j == k or j >= n:                  # a title must be separated
        return k
    opener = text[j]
    if opener not in ("\"", "'", "("):
        return k
    closer = ")" if opener == "(" else opener
    j += 1
    while j < n:
        c = text[j]
        if c == "\\" and j + 1 < n:
            j += 2
            continue
        if c == closer:
            return j + 1
        j += 1
    return k                              # unterminated: not a title


def _strip_links(text: str) -> str:
    """Replace each inline link/image with its LABEL: `[lbl](dest)` -> `lbl`.

    The destination is SCANNED, not matched by a regex, because CommonMark
    allows balanced parentheses, backslash escapes, an `<…>` form and an
    optional title — so `[<vcs>](https://x_(y))`, `[<vcs>](<https://x/a(b>)`
    and `[<vcs>](https://x/Guns_N'_Roses)` all render as the bare word and
    none of them may hide the form. A destination that does not close, or a
    `(` that is not followed by one, is left as literal text."""
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\\" and i + 1 < n:      # an escape covers the next char
            out.append(text[i:i + 2])
            i += 2
            continue
        start = i
        if ch == "!" and text[i + 1:i + 2] == "[":   # image: same shape
            i += 1
            ch = "["
        if ch != "[":
            out.append(text[i])
            i += 1
            continue
        close = text.find("]", i + 1)     # a label holds no nested brackets
        if close < 0 or "[" in text[i + 1:close] \
                or text[close + 1:close + 2] != "(":
            out.append(text[start])
            i = start + 1
            continue
        label = text[i + 1:close]
        k = close + 2
        while k < n and text[k].isspace():
            k += 1
        k = _scan_destination(text, k, n)
        if k < 0:                         # never closed: literal text
            out.append(text[start])
            i = start + 1
            continue
        k = _scan_title(text, k, n)
        while k < n and text[k].isspace():
            k += 1
        if k >= n or text[k] != ")":
            out.append(text[start])
            i = start + 1
            continue
        out.append(label)
        i = k + 1
    return "".join(out)


def markup_stripped(text: str) -> str:
    """The line as it RENDERS: inline Markdown markers removed and their
    contents kept — code spans, emphasis, GFM strikethrough, and link labels
    (the destination goes) — so a form split across adjacent markup ("never run
    `<vcs>` `<publish>`", "never run [<vcs>](u) [<publish>](u)") reads as the
    command a human sees."""
    out = text
    for _ in range(4):                    # nested labels are rare; bounded
        replaced = _strip_links(out)
        if replaced == out:
            break
        out = replaced
    out = out.replace("~~", "")
    return "".join(ch for ch in out if ch not in MARKUP_CHARS)


def _literal_lines(raw_lines: list[str]) -> list[bool]:
    """Per physical line: is it inside a fenced code block or a multi-line HTML
    comment? Lines in either are literal, one per line — there is no soft
    wrapping to rejoin there. Both markers are read THROUGH blockquote markers,
    so a QUOTED fence (`> ``` `) opens a region just as a bare one does.
    (This is the ONLY place these regions matter: a form spelled inside one is
    still a finding on its own line.)"""
    inside: list[bool] = []
    fence = None
    in_comment = False
    for raw in raw_lines:
        _, t = _bq_split(raw)
        if in_comment:
            inside.append(True)
            if "-->" in t:
                in_comment = False
            continue
        marker = t[:3] if t[:3] in ("```", "~~~") else None
        if fence is None and marker:
            fence = marker
            inside.append(True)
            continue
        if fence is not None and marker == fence:
            fence = None
            inside.append(True)
            continue
        if fence is None and t[:4] == "<!--" and "-->" not in t:
            in_comment = True
            inside.append(True)
            continue
        inside.append(fence is not None)
    return inside


def _bq_split(raw: str) -> tuple[int, str]:
    """(blockquote depth, the line with its `>` markers removed). Two lines at
    DIFFERENT depths are different blocks, and a block marker must be read
    THROUGH the quoting — `> - <vcs>` opens a list item, not a paragraph."""
    depth = 0
    t = raw
    while True:
        t = t.lstrip(" \t")
        if t[:1] != ">":
            return depth, t
        depth += 1
        t = t[1:]


def _block_kind(raw: str):
    """What Markdown block this PHYSICAL line OPENS, seen through any
    blockquote markers: `"hard"` for a heading / fence / table row / HTML
    comment, `"list"` for a bullet, checklist or numbered item, else `None`
    for an ordinary paragraph line.

    The split matters to the soft-wrap pair pass. A list item's own paragraph
    soft-wraps onto the following indented line — `- Never run <vcs>` /
    `  <publish> from a session` is ONE sentence — so a list item may OPEN a
    joinable pair. Nothing may be joined ONTO a line that opens any new block,
    and a heading / fence / table row / comment never carries a continuation."""
    _, t = _bq_split(raw)
    if t[:3] in ("```", "~~~") or t[:4] == "<!--":
        return "hard"
    if t[:1] == "|":                      # a table row
        return "hard"
    k = 0
    while k < len(t) and t[k] == "#":
        k += 1
    if 0 < k <= 6 and t[k:k + 1] in (" ", "\t"):
        return "hard"
    if t[:1] in ("-", "*", "+") and t[1:2] in (" ", "\t"):
        return "list"                     # `- [ ] x` lands here too
    k = 0
    while k < len(t) and t[k].isdigit():
        k += 1
    if 0 < k <= 9 and t[k:k + 1] in (".", ")") and t[k + 1:k + 2] in (" ", "\t"):
        return "list"
    return None


def code_spans(text: str) -> list[str]:
    """Every backtick-delimited Markdown code span on the line."""
    parts = text.split("`")
    return [p for i, p in enumerate(parts) if i % 2 == 1 and p.strip()]


# --------------------------------------------------------------------------
# the shell's QUOTING model, in ONE place
#
# WIDENING (lockstep fold): the balance check, the splitter, the substitution
# reader, the tokenizer and the quoted-span reader each carried their own quote
# loop that knew exactly two forms, `'` and `"`. Bash has four, and the two that
# were missing are EXECUTABLE — so a line spelling the prohibited form through
# one of them was a real instruction this gate read as unrelated text:
#
#   `$'…'`  ANSI-C quoting, escapes DECODED. OBSERVED on this host (bash
#           3.2.57(1), git 2.54.0): `<vcs> $'<publish>' -h`, `<vcs> $'\x70ush'
#           -h`, `<vcs> $'\160ush' -h` and `<vcs> $'pu'$'sh' -h` all print the
#           publish usage, and `$'\x67it' <publish> -h` does too — the PROGRAM
#           name spelled entirely in hex escapes, with no literal word anywhere
#           on the line for a tokenizer reading a bare `$` to see.
#   `$"…"`  locale translation, which behaves as a double-quoted string.
#           OBSERVED: `<vcs> $"<publish>" -h` prints the publish usage.
#
# Rather than add two more branches to five loops, the forms live HERE and every
# consumer asks this. Adding a fifth form is one edit. This is the same
# structure, the same names and the same values as the floor guard's
# `bin/floor-git-egress-lib.sh`, so the two tables diff line-for-line.
#
# Inside DOUBLE quotes a backslash keeps its special meaning only before these;
# anywhere else it is a literal backslash. OBSERVED: `printf "%s\n" "a\xb"`
# prints `a\xb`, while `"a\$b"` prints `a$b`. Dropping the backslash
# unconditionally — which the tokenizer and the span reader both used to do —
# CORRUPTS a nested ANSI-C string: `<shell> -c "<vcs> $'\x70ush'"` had its outer
# layer rewritten to `$'x70ush'`, so the inner decode produced `x70ush` and a
# form bash really executes was passed.
DQ_ESCAPABLE = "$`\"\\\n"

ANSI_C_SIMPLE = {
    "a": "\a", "b": "\b", "e": "\x1b", "E": "\x1b", "f": "\f", "n": "\n",
    "r": "\r", "t": "\t", "v": "\v", "\\": "\\", "'": "'", '"': '"', "?": "?",
}


def _ansi_c_decode(body: str) -> str:
    """Decode a `$'…'` body the way bash does. An unknown escape keeps its
    backslash, which is also what bash does with it.

    Never EXPANDS: every escape it recognises is at least two characters in and
    exactly one out, and an unrecognised one is copied through unchanged. That
    matters beyond fidelity — `scan_command_text`'s termination pair counts
    token-VALUE length, and a decode that could grow a value would be a new
    producer edge for that argument to answer."""
    out: list[str] = []
    i = 0
    n = len(body)
    while i < n:
        ch = body[i]
        if ch != "\\" or i + 1 >= n:
            out.append(ch)
            i += 1
            continue
        nxt = body[i + 1]
        if nxt in ANSI_C_SIMPLE:
            out.append(ANSI_C_SIMPLE[nxt])
            i += 2
            continue
        if nxt == "c" and i + 2 < n:                  # \cX — a control character
            out.append(chr(ord(body[i + 2].upper()) ^ 0x40))
            i += 3
            continue
        if nxt in ("x", "u", "U"):
            width = {"x": 2, "u": 4, "U": 8}[nxt]
            j = i + 2
            digits = ""
            while j < n and len(digits) < width and body[j] in "0123456789abcdefABCDEF":
                digits += body[j]
                j += 1
            if digits:
                try:
                    out.append(chr(int(digits, 16)))
                except ValueError:
                    out.append(nxt)
                i = j
                continue
        if nxt in "01234567":
            j = i + 1
            digits = ""
            while j < n and len(digits) < 3 and body[j] in "01234567":
                digits += body[j]
                j += 1
            try:
                out.append(chr(int(digits, 8)))
            except ValueError:
                out.append(digits)
            i = j
            continue
        out.append(ch)                                # unknown escape: keep the backslash
        out.append(nxt)
        i += 2
    return "".join(out)


def _quote_at(text: str, i: int) -> tuple:
    """The quote form opening at `i`, or (None, i). Returns (kind, body_start).

    `kind` is one of `'`, `"`, `$'`. `$"…"` is a double-quoted string carrying a
    translation marker, so it is reported as `"` with its body after the quote —
    the `$` is not part of the word, which is exactly the detail that made
    `$"…"` invisible before."""
    ch = text[i]
    if ch in ("'", '"'):
        return ch, i + 1
    if ch == "$" and i + 1 < len(text):
        nxt = text[i + 1]
        if nxt == "'":
            return "$'", i + 2
        if nxt == '"':
            return '"', i + 2
    return None, i


def _quote_end(text: str, start: int, kind: str) -> tuple:
    """(body_end, next_index) for a region whose BODY starts at `start`.

    An UNTERMINATED region ends at EOF and is reported as `next_index ==
    body_end` — the only way the two can be equal, since a terminated region's
    next index is one past its closer. That is what `shell_quoting_is_balanced`
    tests, and reading to the end cannot hide a command."""
    n = len(text)
    i = start
    if kind == "'":
        while i < n and text[i] != "'":
            i += 1
        return i, min(i + 1, n)
    # `"` and `$'` both honour backslash escapes; only the closer differs.
    closer = "'" if kind == "$'" else '"'
    while i < n:
        if text[i] == "\\" and i + 1 < n:
            i += 2
            continue
        if text[i] == closer:
            return i, i + 1
        i += 1
    return n, n


def _quote_value(body: str, kind: str) -> str:
    """The characters a quoted region contributes to its WORD."""
    if kind == "$'":
        return _ansi_c_decode(body)
    if kind == '"':
        out: list[str] = []
        i = 0
        while i < len(body):
            if body[i] == "\\" and i + 1 < len(body) and body[i + 1] in DQ_ESCAPABLE:
                out.append(body[i + 1])
                i += 2
                continue
            out.append(body[i])
            i += 1
        return "".join(out)
    return body


def shell_quoting_is_balanced(text: str) -> bool:
    """True when every shell quote on the line is closed. A line that is NOT
    balanced cannot mean its quotes literally — that is prose."""
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "\\" and i + 1 < n:
            i += 2
            continue
        kind, body_start = _quote_at(text, i)
        if kind is None:
            i += 1
            continue
        end, nxt = _quote_end(text, body_start, kind)
        if nxt <= end:                    # ran to EOF without meeting the closer
            return False
        i = nxt
    return True


# --------------------------------------------------------------------------
# shell-ish splitting and tokenizing


def _substitution_body(text: str, start: int, closer: str) -> tuple[str, int]:
    """The body of a command substitution opened at `start`, and the index just
    past its closer. `)` nests, a backtick does not, and BOTH skip quoted
    regions — a `)` inside quotes does not close the substitution, so
    `$(printf ')'; <cmd>)` yields the whole body and not just its first
    fragment. Quoted regions are skipped through the ONE quoting model, so a
    `$'…'` inside a substitution is not mis-scanned by a second, independent
    two-form state machine — which is what this function used to carry."""
    depth = 1
    i = start
    n = len(text)
    while i < n:
        if text[i] == "\\" and i + 1 < n:
            i += 2
            continue
        kind, body_start = _quote_at(text, i)
        if kind is not None:
            _end, i = _quote_end(text, body_start, kind)
            continue
        ch = text[i]
        if closer == ")" and ch == "(":
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return text[start:i], i + 1
        i += 1
    return text[start:], n            # unterminated: take the rest


def split_commands(text: str, quote_aware: bool) -> list[str]:
    parts: list[str] = []
    cur: list[str] = []
    quote = None
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if quote_aware:
            if quote == "'":
                if ch == "'":
                    quote = None
                cur.append(ch)
                i += 1
                continue
            if quote == '"':
                if ch == "\\" and i + 1 < n:
                    cur.append(ch)
                    cur.append(text[i + 1])
                    i += 2
                    continue
                if text[i:i + 2] == "$(":
                    # Command substitution stays LIVE inside double quotes —
                    # `"$(cmd)"` runs cmd. Lift the BODY out as its own command
                    # line (recursively, so nested substitutions come too) and
                    # carry on with the surrounding command intact: what
                    # follows the substitution is still that command's quoted
                    # argument. A BARE parenthesis is literal here and does
                    # not separate, so `echo "(…)"` stays one command.
                    body, i = _substitution_body(text, i + 2, ")")
                    parts.extend(split_commands(body, quote_aware))
                    continue
                if ch == "`":
                    body, i = _substitution_body(text, i + 1, "`")
                    parts.extend(split_commands(body, quote_aware))
                    continue
                if ch == '"':
                    quote = None
                cur.append(ch)
                i += 1
                continue
            if ch == "\\" and i + 1 < n:
                cur.append(ch)
                cur.append(text[i + 1])
                i += 2
                continue
            kind, body_start = _quote_at(text, i)
            if kind == "$'":
                # ANSI-C: nothing inside is live (no substitution, no
                # separator), so the whole region travels verbatim in the
                # segment text and the tokenizer decodes it.
                _end, nxt = _quote_end(text, body_start, kind)
                cur.append(text[i:nxt])
                i = nxt
                continue
            if kind is not None:
                # `'` and `"` — including the `$"…"` translation form, whose `$`
                # travels with the region so the tokenizer sees the same opener;
                # substitutions inside it are still live and still lifted out.
                quote = kind
                cur.append(text[i:body_start])
                i = body_start
                continue
        if quote_aware and text[i:i + 2] == "$(":
            # Same lift as inside double quotes: the body is its own command
            # line, the SURROUNDING command continues unbroken. A bare `(`
            # stays a separator — that is a subshell, which really does start a
            # new command.
            body, i = _substitution_body(text, i + 2, ")")
            parts.extend(split_commands(body, quote_aware))
            continue
        if quote_aware and ch == "`":
            body, i = _substitution_body(text, i + 1, "`")
            parts.extend(split_commands(body, quote_aware))
            continue
        if text[i:i + 4] == "<!--":
            parts.append("".join(cur))
            cur = []
            i += 4
            continue
        if text[i:i + 3] == "-->":
            parts.append("".join(cur))
            cur = []
            i += 3
            continue
        if text[i:i + 2] in ("&&", "||"):
            parts.append("".join(cur))
            cur = []
            i += 2
            continue
        if ch in SEPARATOR_CHARS:
            parts.append("".join(cur))
            cur = []
            i += 1
            continue
        cur.append(ch)
        i += 1
    parts.append("".join(cur))
    return parts


def tokenize(text: str, quote_aware: bool) -> list[str]:
    """Split one command segment into argv the way the shell would: a quoted
    region contributes its VALUE to the current word (so `$'\\x67it'` is the
    word for the VCS), and a backslash escapes the next character. Every quote
    form is read through `_quote_at`/`_quote_value`, so the tokenizer has no
    quote table of its own to drift from the splitter's.

    A `${…}` body keeps its BACKSLASHES VERBATIM, and does not split on
    whitespace. Outside an expansion a backslash is the shell's word-level
    escape and the character behind it is what survives; INSIDE one it belongs
    to the expansion's own grammar, where it decides whether a `/` is the
    pattern/replacement separator or a literal slash. Dropping it there made
    the candidate reader see `${x/foo\\/bar/<publish>}` as though the escape had
    not been written, which is wrong in BOTH directions.

    The brace rule is applied only in the QUOTE-AWARE reading, deliberately.
    The quote-naive reading's tokens are the first component of that reading's
    termination measure, and its whole argument is that a naive token is
    whitespace-free — so letting one carry a space would break the walk's
    bound, not just its tokenization."""
    toks: list[str] = []
    cur: list[str] = []
    started = False
    i = 0
    n = len(text)
    brace = 0
    while i < n:
        if quote_aware:
            kind, body_start = _quote_at(text, i)
            if kind is not None:
                end, nxt = _quote_end(text, body_start, kind)
                if brace > 0:
                    # VERBATIM inside a `${…}` body, for the same reason a
                    # backslash is. Collapsing `"a}b"` to `a}b` destroys the
                    # quote provenance, and the body walk then reads that `}`
                    # as the expansion's terminator and loses the word behind
                    # it. MEASURED, and on THREE shells rather than one:
                    # `x=a}b; "${x/"a}b"/<publish>}"` yields the publishing word
                    # on bash 3.2.57, zsh 5.9 and ksh93u+, and `${x:-"a}b"}`
                    # yields `a}b` — the expansion really does run past a
                    # quoted brace.
                    cur.append(text[i:nxt])
                else:
                    cur.append(_quote_value(text[body_start:end], kind))
                started = True
                i = nxt
                continue
        ch = text[i]
        if ch.isspace() and brace == 0:
            if started:
                toks.append("".join(cur))
                cur = []
                started = False
            i += 1
            continue
        if quote_aware and ch == "\\" and i + 1 < n:
            if brace > 0:
                cur.append(text[i:i + 2])   # verbatim: the expansion decides
            else:
                cur.append(text[i + 1])
            started = True
            i += 2
            continue
        if quote_aware and text[i:i + 2] == "${":
            brace += 1
            cur.append("${")
            started = True
            i += 2
            continue
        if brace > 0 and ch == "}":
            # ONLY `${` opens a nested expansion, which is why the increment
            # lives in the branch above and there is none here. A bare `{`
            # inside a body is ORDINARY TEXT — MEASURED on bash 3.2.57:
            # `x='{'; <vcs> ${x/{/<publish>} origin main` really runs the
            # publishing subcommand with `origin main` as SEPARATE words
            # (argc=3), and `${x/a/{}` yields `{`, so the first `}` still
            # terminates. zsh 5.9 ("closing brace expected") and dash ("Bad
            # substitution") reject the line, so one shell carries it — which
            # is the bias this gate is written with. Counting that `{` as
            # structure held the token open past its real terminator and fused
            # the trailing operands into it, so the whole command read as ONE
            # word and the publishing subcommand disappeared. Same fact, same
            # fix, in `_expansion_candidates`' body walk.
            brace -= 1
        cur.append(ch)
        started = True
        i += 1
    if started:
        toks.append("".join(cur))
    return toks


# --------------------------------------------------------------------------
# rule table


def _program(tok: str) -> str:
    trimmed = trim_token(tok)
    return os.path.basename(trimmed) or trimmed


def _is_assignment(tok: str) -> bool:
    head = tok.split("=", 1)[0]
    return "=" in tok and head != "" and (head[0].isalpha() or head[0] == "_") \
        and all(c.isalnum() or c == "_" for c in head)


def _expansion_skip(text: str, i: int, hide_quoted: bool = True):
    """The index just past an escape pair — or, with `hide_quoted`, a quoted
    span — at `i` inside a `${…}` body, else None.

    Both hide structure from the expansion's own grammar: `\\}` and `"…}…"` are
    literal text rather than the expansion's terminator, and `\\/` and `"…/…"`
    are not its pattern/replacement separator. The tokenizer keeps both
    VERBATIM inside a body precisely so this can still see them.

    The backslash half is unconditional; the QUOTE half is a parameter because
    the shells genuinely disagree about it, and only about it — see
    `_find_unescaped`."""
    if i >= len(text):
        return None
    if text[i] == "\\" and i + 1 < len(text):
        return i + 2
    if not hide_quoted:
        return None
    kind, body_start = _quote_at(text, i)
    if kind is not None:
        _end, nxt = _quote_end(text, body_start, kind)
        return nxt
    return None


def _find_unescaped(text: str, sub: str, start: int = 0,
                    hide_quoted: bool = True) -> int:
    """`text.find(sub, start)` that skips escaped positions — and, by default,
    quoted spans. -1 when absent.

    A quoted BRACE is settled: all three shells here agree that it closes
    nothing (see the tokenizer). A quoted SEPARATOR is not, and the
    disagreement is load-bearing in both directions, so neither reading may be
    adopted alone. MEASURED on the same two spellings:

      `${x/"a/b"/<publish>}` with x=`a/b`  — ksh93u+ yields the publishing word
        (its separator search IS quote-aware); bash 3.2.57 yields
        `b/<publish>/b`; zsh 5.9 substitutes nothing.
      `${x/"a/<publish>"}` with x=`a`      — bash 3.2.57 yields the publishing
        word ALONE, as one whole argument (`set --` reports argc=1); ksh93u+
        and zsh 5.9 yield `a`.

    So each reading is a real publish on some measured shell and a silent miss
    on the other. `_expansion_candidates` therefore runs the separator search
    BOTH ways and unions the words — over-detection in the safe direction, and
    the only reading with no measured miss behind it."""
    i = start
    n = len(text)
    m = len(sub)
    while i <= n - m:
        nxt = _expansion_skip(text, i, hide_quoted)
        if nxt is not None:
            i = nxt
            continue
        if text[i:i + m] == sub:
            return i
        i += 1
    return -1


def _unescape_expansion_word(word: str) -> str:
    """The literal a `${…}` word really contributes: backslashes dropped and
    quoted spans replaced by their VALUE. Otherwise a single backslash — or a
    single quote — anywhere in the word hides all of it.

    MEASURED on bash 3.2.57, unquoted so the word is the shell's own:
    `unset x; <vcs> ${x:-pu\\sh}` really invokes the publishing subcommand, and
    so does `${x:-"<publish>"}`. Written INSIDE double quotes the backslash
    survives instead (`"${x:-pu\\sh}"` yields `pu\\sh`, which is not a
    subcommand), so unescaping there over-detects — deliberately, and identically
    on both sides of the lockstep, since the tokenizer hands that spelling over
    with the backslash intact too."""
    out: list[str] = []
    i = 0
    n = len(word)
    while i < n:
        if word[i] == "\\" and i + 1 < n:
            out.append(word[i + 1])
            i += 2
            continue
        kind, body_start = _quote_at(word, i)
        if kind is not None:
            end, nxt = _quote_end(word, body_start, kind)
            out.append(_quote_value(word[body_start:end], kind))
            i = nxt
            continue
        out.append(word[i])
        i += 1
    return "".join(out)


def _expansion_candidates(tok: str, depth: int = 0) -> list[str]:
    """The literal words a `${…}` inside `tok` could expand to, nested ones
    included.

    Conservative by construction: only the VISIBLE literal is considered, never
    a guess at the parameter, so a bare `${x}` yields nothing and passes — the
    same variable-indirection boundary this gate documents for a program named
    through a variable."""
    out: list[str] = []
    if depth > EXPANSION_MAX_DEPTH:
        return out
    i = 0
    n = len(tok)
    while i < n:
        if tok[i:i + 2] != "${":
            i += 1
            continue
        braces = 1
        j = i + 2
        body: list[str] = []
        while j < n:
            # An ESCAPED brace is a literal one and closes nothing — the shell
            # reads `${x:+a\}b}` as the word `a\}b`, not as an expansion ending
            # at the first `}`. Counting it made the body stop early and the
            # word behind it disappear. A QUOTED brace is the same fact one
            # spelling further out (`${x/"a}b"/<publish>}`), and both are kept
            # VERBATIM here so the operator and separator searches below re-read
            # them exactly the same way.
            nxt = _expansion_skip(tok, j)
            if nxt is not None:
                body.append(tok[j:nxt])
                j = nxt
                continue
            if tok[j:j + 2] == "${":
                # ONLY `${` nests, for the same measured reason as in
                # `tokenize`: a bare `{` is text, so counting it swallowed the
                # real terminator and the word behind it.
                braces += 1
                body.append("${")
                j += 2
                continue
            if tok[j] == "}":
                braces -= 1
                if braces == 0:
                    break
            body.append(tok[j])
            j += 1
        inner = "".join(body)
        i = j + 1
        # The operator is the FIRST one that appears after the parameter name,
        # longest match winning so `//` is not read as `/`, nor `:-` as `:`.
        # ESCAPE-AWARE: a `\/` is a literal slash in the pattern, not the
        # operator.
        best = None
        for op in sorted(EXPANSION_VALUE_OPS + EXPANSION_REPLACE_OPS
                         + EXPANSION_NON_VALUE_OPS, key=len, reverse=True):
            k = _find_unescaped(inner, op)
            if k > 0 and (best is None or k < best[1]
                          or (k == best[1] and len(op) > len(best[0]))):
                best = (op, k)
        if best is None:
            continue                      # no operator: no literal to take
        op, k = best
        rest = inner[k + len(op):]
        words: list[str] = []
        if op in EXPANSION_REPLACE_OPS:
            # `${p/pattern/replacement}` — the replacement is what survives, and
            # with no second UNESCAPED separator the pattern is DELETED,
            # leaving none. The search must skip an escaped slash or it goes
            # wrong in both directions: a real replacement whose PATTERN
            # contains `\/` is missed, and a pattern-only expansion whose
            # pattern contains `\/<publish>` is reported.
            #
            # A QUOTED slash is the one place the measured shells disagree, so
            # the search is run BOTH ways and the words UNIONED rather than one
            # reading being picked. Committing to either is a measured miss on
            # the other's shell — see `_find_unescaped` for both spellings and
            # both verdicts. This is the same lesson as the candidate LIST one
            # position out: an operand whose meaning is ambiguous has a SET of
            # meanings, and taking one of them decides the others away.
            for hide_quoted in (True, False):
                slash = _find_unescaped(rest, "/", hide_quoted=hide_quoted)
                if slash == -1:
                    continue
                if not hide_quoted \
                        and not _unescape_expansion_word(rest[:slash]):
                    # The naive reading's ONE artefact, and the only place the
                    # two readings need separating rather than unioning. A
                    # naive separator can land inside a quoted span, and when
                    # everything before it is an UNTERMINATED quote the pattern
                    # unescapes to nothing — a shape no shell runs. MEASURED on
                    # `${x/"/<publish>}`: bash 3.2.57 and zsh 5.9 reject the
                    # line outright ("unexpected EOF" / "unmatched") and ksh93u+
                    # parses it but never substitutes, for x unset, x=abc and
                    # x=`"` alike.
                    # The emptiness test goes through the QUOTING MODEL rather
                    # than stripping quote characters, so it covers all FOUR
                    # openers `_quote_at` knows and not only the two raw ones.
                    # Measured on the other two as well, same three shells and
                    # the same answers: bash and zsh reject the ANSI-C and the
                    # locale-translation opener outright, ksh93u+ parses each
                    # and substitutes nothing. All four are pinned as negatives
                    # and a mutant narrowing this to the raw openers is in the
                    # battery — with only the raw two pinned it passed the
                    # whole selftest while reporting the other two.
                    # The restriction is deliberately NOT applied to the
                    # quote-aware reading, where an empty pattern is real:
                    # `${x/""/<publish>}` with x empty yields the publishing
                    # word on zsh 5.9 and on ksh93u+ (bash 3.2.57 declines,
                    # dash rejects the substitution). That spelling is still a
                    # finding, through the quote-aware half.
                    continue
                words.append(_unescape_expansion_word(rest[slash + 1:]))
        elif op in EXPANSION_VALUE_OPS:
            # The SAME unescaping as the replacement side. The shell drops the
            # backslash here too — `unset x; <vcs> ${x:-pu\sh}` really invokes
            # the publishing subcommand (measured) — and reading only the
            # replacement side escape-aware left the default/alternate ops a
            # silent miss on the identical spelling.
            words.append(_unescape_expansion_word(rest))
        else:
            continue                      # removal / error / case / substring
        for word in words:
            word = word.strip()
            if not word:
                continue
            out += _expansion_candidates(word, depth + 1)
            out.append(trim_token(word))
    return out


def _egress_candidates(tok: str, vocabulary) -> list[str]:
    """The token's own trimmed value plus anything a `${…}` in it could expand
    to, filtered to `vocabulary`.

    ONE helper, asked at EVERY operation position. Checking only the first
    position — which is what a per-site membership test amounts to — left the
    two-word families and the forge families reachable through an expansion."""
    hits: list[str] = []
    trimmed = trim_token(tok)
    if trimmed in vocabulary:
        hits.append(trimmed)
    for candidate in _expansion_candidates(tok):
        if candidate in vocabulary:
            hits.append(candidate)
    return hits


def _split_cmdline(value: str) -> list[str]:
    """The VCS's own alias-value splitter (its `split_cmdline`), which is how an
    alias VALUE becomes argv: a backslash escapes the next character, and either
    quote character quotes a run.

    A plain whitespace split is not the same function and misses a real form:
    observed on 2.54.0, an alias value spelling the publish word with a
    backslash inside it prints that subcommand's usage, so the backslash is
    removed and the word IS the publishing subcommand, while a whitespace split
    sees the escaped spelling and finds nothing."""
    words: list[str] = []
    cur: list[str] = []
    started = False
    quote = None
    i = 0
    n = len(value)
    while i < n:
        ch = value[i]
        if quote is not None:
            if ch == "\\" and i + 1 < n and quote == '"':
                cur.append(value[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
                i += 1
                continue
            cur.append(ch)
            i += 1
            continue
        if ch == "\\" and i + 1 < n:
            cur.append(value[i + 1])
            started = True
            i += 2
            continue
        if ch in ("'", '"'):
            quote = ch
            started = True
            i += 1
            continue
        if ch.isspace():
            if started:
                words.append("".join(cur))
                cur = []
                started = False
            i += 1
            continue
        cur.append(ch)
        started = True
        i += 1
    if started:
        words.append("".join(cur))
    return words


def _scan_vcs(args: list[str]) -> tuple[list[str], list[str]]:
    """(findings, nested command lines) for the VCS's own argument list.

    The VCS is the ONE parser here that neither clusters its short global
    options nor accepts an attached operand on them, so it is read by exact
    match and no cluster walk is applied. Observed on 2.54.0: `-C <path>` and
    `-c <k=v>` work, while `-C<path>`, `-cfoo.bar=1` and the cluster `-pc` are
    each rejected with "unknown option" / the usage banner. Any other dash token
    is therefore a lone flag, and skipping it reaches the subcommand behind.

    A subcommand that names a two-word FAMILY is walked one level further, past
    that family's own options and their operands, to the first bare operand —
    its OPERATION. Only that first operand counts: a family operation this
    table does not refuse ends the walk rather than letting a later token be
    read as one.

    An `-c <alias-prefix><name>=<value>` global is COLLECTED as the walk passes
    it, because the tool resolves an alias defined on its own command line
    before dispatching. When the subcommand turns out to be one of them, the
    value is split with the tool's OWN splitter and SPLICED INTO ARGV, and the
    whole walk restarts — an expansion may introduce further globals or name
    another alias, so resolving only its first word would miss both. A value
    beginning with the shell marker is a command line and is handed back as
    nested instead. The alias is POPPED as it resolves, so a self-referential
    definition cannot loop; the hop bound is for a CHAIN, and exhausting it
    reports rather than passing."""
    return _vcs_walk(list(args), {}, 0)


def _vcs_walk(argv: list[str], aliases: dict[str, str],
              hops: int) -> tuple[list[str], list[str]]:
    """One pass of the VCS walk, recursing once per ALIAS CANDIDATE.

    Recursion rather than a loop, because a token can name more than one alias
    (it may carry several expansions) and resolving one CONSUMES it: each
    candidate therefore needs its own copy of the alias map, and committing to
    the first answer let every later candidate decide nothing. The hop bound and
    the finite, popped alias map bound the recursion."""
    while True:
        i = 0
        sub_index = None
        while i < len(argv):
            tok = argv[i]
            if tok.startswith("-"):
                if tok in VCS_TERMINAL_OPTS:
                    return [], []       # it prints and exits; nothing runs
                if tok in VCS_VALUE_OPTS:
                    if tok == "-c" and i + 1 < len(argv):
                        name, sep, value = argv[i + 1].partition("=")
                        if sep and name.lower().startswith(VCS_ALIAS_PREFIX):
                            aliases[name.lower()[len(VCS_ALIAS_PREFIX):]] = value
                    i += 2
                else:
                    i += 1
                continue
            sub_index = i
            break
        if sub_index is None:
            return [], []
        sub = trim_token(argv[sub_index])
        for hit in _egress_candidates(argv[sub_index], VCS_EGRESS):
            return ["%s %s" % (VCS, hit)], []
        # EVERY candidate family, not only the first: one token can carry more
        # than one expansion, so committing to the first answer would let the
        # others decide nothing.
        for family in _egress_candidates(argv[sub_index], VCS_PAIR_FAMILIES):
            op = _vcs_pair_operation(family, argv[sub_index + 1:])
            if op is not None:
                return ["%s %s %s" % (VCS, family, op)], []
        # The alias NAME is an operation position like any other, so a `${…}`
        # that could expand to one resolves through the same walk. Consulting
        # the raw token alone was the one position this helper was not asked
        # at, which is exactly the inconsistency it exists to prevent.
        names = [sub.lower()] if sub.lower() in aliases else []
        names += [n for n in _egress_candidates(argv[sub_index],
                                                {n.lower() for n in aliases})
                  if n not in names]
        if not names:
            return [], []
        if hops >= VCS_ALIAS_MAX_HOPS:
            return [ALIAS_BOUND_FORM], []
        for name in names:
            forms, nested = _vcs_alias_hop(name, dict(aliases), argv,
                                           sub_index, hops)
            if forms or nested:
                return forms, nested
        return [], []


def _vcs_alias_hop(name: str, aliases: dict[str, str], argv: list[str],
                   sub_index: int, hops: int) -> tuple[list[str], list[str]]:
    """Resolve ONE alias candidate on its own copy of the alias map."""
    expansion = aliases.pop(name).strip()
    if expansion.startswith(VCS_ALIAS_SHELL_PREFIX):
        # A shell-valued alias runs its value AND THE INVOCATION'S OWN
        # REMAINING OPERANDS, appended as words. MEASURED on 2.54.0:
        # `<vcs> -c <prefix>p=!echo p one two` prints "one two", and
        # `<vcs> -c <prefix>p=!<vcs> p <publish>` really publishes. Dropping
        # them left that second form a silent miss whenever it was written
        # unquoted — the quoted spelling was already caught by the
        # quoted-operand pass, which is what made the gap look closed.
        # Re-serialized as WORDS (minimal quoting) rather than joined raw,
        # so an operand carrying a space stays one word.
        script = expansion[len(VCS_ALIAS_SHELL_PREFIX):]
        script += "".join(" " + shlex.quote(a)
                          for a in argv[sub_index + 1:])
        return [], [script]
    words = _split_cmdline(expansion)
    if not words:
        return [], []
    return _vcs_walk(words + argv[sub_index + 1:], aliases, hops + 1)


def _vcs_pair_operation(family: str, rest: list[str]):
    """The publishing OPERATION of a two-word family — the first token that is
    neither an option nor an option's operand — or None.

    Returned rather than formatted, because the two callers spell the same
    finding differently: the two-word invocation names the family as a
    SUBCOMMAND, the dashed executable carries it in the PROGRAM."""
    ops = {op for fam, op in VCS_EGRESS_PAIRS if fam == family}
    pair_opts = VCS_PAIR_VALUE_OPTS.get(family, set())
    k = 0
    while k < len(rest):
        tok = rest[k]
        if tok.startswith("-"):
            k += 2 if tok in pair_opts else 1
            continue
        for op in _egress_candidates(tok, ops):
            return op
        break
    return None


def _api_findings(rest: list[str]) -> list[str]:
    """A raw API call is a finding when its EFFECTIVE method is not GET, or when
    it carries a request body.

    The WHOLE option set is read before deciding, because the method and the
    parameters interact. From that CLI's own help on 2.96.0, verbatim: "The
    default HTTP request method is `GET` normally and `POST` if any parameters
    were added", and "adding request parameters will automatically switch the
    request method to `POST`. To send the parameters as a `GET` query string
    instead, use `--method GET`."

    So a field flag ALONE is a mutation — it implies POST — but a field flag
    under an EXPLICIT GET is a query string, which is that CLI's own documented
    search idiom. Returning at the first field flag cannot express the
    difference, and reported the read idiom as a publish.

    Short options cluster here exactly as they do on a carrier: `-XPOST`,
    `-iX POST` and `-iFa=b` are all mutations, while `-qX POST` is a jq query
    whose value happens to be "X" and carries no method flag at all."""
    method = None
    has_field = False
    has_input = False
    k = 0
    while k < len(rest):
        tok = rest[k]
        bare = tok.split("=", 1)[0]
        if bare in API_BODY_FLAGS:
            if bare == "--input":
                has_input = True
            else:
                has_field = True
            k += 1 if "=" in tok else 2
            continue
        if bare in API_METHOD_FLAGS:
            if "=" in tok:
                method = tok.split("=", 1)[1]
                k += 1
            else:
                method = rest[k + 1] if k + 1 < len(rest) else ""
                k += 2
            continue
        if _is_short_option(tok):
            letter, operand, separate = _short_cluster_operand(
                tok, API_SHORT_VALUE_CHARS)
            if letter is not None:
                if separate:
                    operand = rest[k + 1] if k + 1 < len(rest) else ""
                if letter in ("f", "F"):
                    has_field = True
                elif letter == "X":
                    method = operand
                k += 2 if separate else 1
                continue
        k += 1
    explicit_get = method is not None and trim_token(method).upper() == "GET"
    if method is not None and not explicit_get and trim_token(method) != "":
        return ["%s %s (non-GET method)" % (FORGE, API_SUB)]
    if has_input and not explicit_get:
        return ["%s %s (request body)" % (FORGE, API_SUB)]
    if has_field and not explicit_get:
        return ["%s %s (request body)" % (FORGE, API_SUB)]
    return []


def _forge_option_step(tok: str, family=None, actions=()) -> int:
    """How many tokens one dash token ahead of a forge subcommand consumes —
    itself, or itself and the following token. The forge CLI parses with pflag,
    which clusters: `-Rx` carries its own operand while `-R` takes the next
    token, and a cluster ending in an operand-taking letter does the same.

    With a family and the action candidates seen so far, THAT action's own
    value options are consulted too. `actions` is the candidate LIST rather
    than one name for the same reason every other operation position takes a
    list: the action operand may carry a `${…}` and mean several things at
    once. An option is operand-taking if ANY candidate says so — the reading
    that consumes more, which is this table's safe direction for a global and
    the recorded trade for an action (see FORGE_ACTION_VALUE_OPTS)."""
    extra: set = set()
    extra_chars = ""
    for action in actions:
        extra |= FORGE_ACTION_VALUE_OPTS.get((family, action), frozenset())
        extra_chars += FORGE_ACTION_SHORT_VALUE_CHARS.get((family, action), "")
    if _is_short_option(tok):
        letter, _operand, takes_next = _short_cluster_operand(
            tok, FORGE_SHORT_VALUE_CHARS + extra_chars)
        if letter is not None:
            return 2 if takes_next else 1
    return 2 if (tok in FORGE_VALUE_OPTS or tok in extra) else 1


def _scan_forge(args: list[str]) -> list[str]:
    i = 0
    while i < len(args):
        tok = args[i]
        if tok.startswith("-"):
            i += _forge_option_step(tok)
            continue
        rest = args[i + 1:]
        # EVERY subcommand this token could name, in order, not the first one
        # that matches: a token carrying two expansions can name both the
        # pull-request surface and the raw API, and giving one precedence let
        # the other decide nothing.
        for sub in (_egress_candidates(tok, {PR_SUB})
                    + _egress_candidates(tok, {API_SUB})):
            forms = _pr_findings(rest) if sub == PR_SUB \
                else _api_findings(rest)
            if forms:
                return forms
        for family in _egress_candidates(tok, set(FORGE_FAMILY_RULES)):
            forms = _forge_family_findings(family, rest)
            if forms:
                return forms
        return []
    return []


def _pr_findings(rest: list[str]) -> list[str]:
    """The pull-request surface: the first bare operand is the ACTION, and it
    is reported when it publishes code or moves a remote ref."""
    k = 0
    while k < len(rest):
        tok = rest[k]
        if tok.startswith("-"):
            k += _forge_option_step(tok)
            continue
        for action in _egress_candidates(tok, PR_MUTATIONS):
            return ["%s %s %s" % (FORGE, PR_SUB, action)]
        return []
    return []


def _forge_family_findings(family: str, rest: list[str]) -> list[str]:
    """The forge CLI's non-PR families, each with the condition that makes the
    action a publish.

    The whole invocation is read before deciding, because two of the three
    conditions are about something OTHER than the action word: one needs a FLAG
    that may sit anywhere after it, the other needs a positional DESTINATION,
    whose absence means the action touches no remote at all. Returning at the
    action could not express either."""
    rules = FORGE_FAMILY_RULES[family]
    actions: list[str] = []
    positionals: list[str] = []
    flags: set[str] = set()
    k = 0
    while k < len(rest):
        tok = rest[k]
        if tok.startswith("-"):
            name, sep, value = tok.partition("=")
            # pflag booleans: `--<flag>` is true, `--<flag>=<bool>` takes the
            # value, and a REPEATED flag is LAST-WINS. Keeping only the enabled
            # occurrences read `--<flag> --<flag>=false` as a publish, which the
            # tool does not perform — the flag's EFFECTIVE value has to be
            # tracked in encounter order, not accumulated. Anything that is NOT
            # one of pflag's false spellings counts as enabled: an unparsable
            # value makes that CLI exit before publishing.
            if name in REPO_CREATE_PUSH_FLAGS:
                if sep and value in PFLAG_FALSE:
                    flags.discard(name)
                else:
                    flags.add(name)
            else:
                flags.add(name)
            k += _forge_option_step(tok, family, actions)
            continue
        if not actions:
            actions = _egress_candidates(tok, set(rules))
            if not actions:
                return []       # a family action this table does not refuse
        else:
            positionals.append(tok)
        k += 1
    # EVERY candidate action the operand could be, not only the first.
    for action in actions:
        condition = rules[action]
        form = "%s %s %s" % (FORGE, family, action)
        if condition is None:
            return [form]
        if condition == FORGE_COND_PUSH_FLAG:
            if flags & REPO_CREATE_PUSH_FLAGS:
                return ["%s (%s)" % (form, FORGE_COND_PUSH_FLAG)]
        elif condition == FORGE_COND_DESTINATION:
            if positionals:
                return [form]
    return []


def _is_short_option(tok: str) -> bool:
    """A single-dash option token — possibly a CLUSTER of short options. `--`
    and every long option are excluded; so is a bare "-"."""
    return len(tok) > 1 and tok[0] == "-" and tok[1] != "-"


def _is_shell_option(tok: str) -> bool:
    """A shell INVOCATION option token: `-x`, a cluster `-oc`, or the `+` form
    `+o`. Long options and a bare `-`/`+` are excluded."""
    return len(tok) > 1 and tok[0] in ("-", "+") and tok[1] != "-"


def _shell_cluster(tok: str, letters: dict, next_tok=None) -> tuple[int, bool]:
    """Read ONE shell `-`/`+` invocation-option token under one shell's letter
    map: `(following tokens consumed, whether the command flag is reached)`.

    The three arities differ exactly where it matters. A SHELL_NEXT letter takes
    the following argv element and the walk CONTINUES past it, so `-oc <name>`
    is `-o <name>` plus `-c`. A SHELL_ATTACHED_OR_NEXT letter takes the rest of
    the token when there is one and the cluster ENDS there — so on zsh and ksh
    `-oc` is `-o` with the option name "c" and there is no command flag at all —
    and only when it ends the token does it take the following element. Every
    other letter, `-c` included, consumes nothing: `-c` means the SCRIPT is the
    first remaining operand, which the caller finds."""
    extra = 0
    has_c = False
    body = tok[1:]
    i = 0
    while i < len(body):
        ch = body[i]
        kind = letters.get(ch)
        if kind in (SHELL_ATTACHED_OR_NEXT, SHELL_ATTACHED_OR_NEXT_NONOPT):
            if i + 1 < len(body):
                break                     # the remainder IS the operand
            if kind == SHELL_ATTACHED_OR_NEXT_NONOPT and (
                    next_tok is None or next_tok[:1] in ("-", "+")):
                break                     # OPTIONAL: an option is not its operand
            extra += 1                    # the letter ends the token
            break
        if kind == SHELL_NEXT:
            extra += 1                    # never attached: the cluster goes on
            i += 1
            continue
        if ch == SHELL_COMMAND_CHAR:
            has_c = True
        i += 1
    return extra, has_c


def _shell_script_index(args: list[str], model: str):
    """`(index, from_fallback)` for the command string this model executes, or
    None when that model executes none.

    `from_fallback` is False for a real `-c` script — whatever FOLLOWS it is $0
    and the positional parameters, so the command line is that ONE token — and
    True for ksh93's no-`-c` first operand, where the operands AFTER it are
    appended to the command line and `_shell_scripts` has to join them in.

    The `-c` script is the first remaining OPERAND after a `-c`; the invocation
    options ahead of it — including their own operands — a bare `+`, and an
    explicit `--` may sit in between.

    WITHOUT a `-c` the answer is per-model, and this is where the widest
    divergence in the file sits. On bash, dash and zsh the first operand is a
    script FILE and there is nothing to scan. On ksh93 it is opened as a file
    first and, when that open fails, its TEXT is executed as a command line —
    so `ksh <cmd>` needs no option spelling at all, and neither do `ksh -oc
    <cmd>`, `ksh -o c <cmd>`, `ksh +oc <cmd>`, `ksh +-xoc <cmd>` or `ksh --
    <cmd>` (SHELL_FIRST_OPERAND carries the measurements). The flag is read at
    every position a plain operand can be reached from, not at one token
    shape, because the behaviour belongs to the operand and not to whatever
    precedes it.

    The token kinds the walk handles explicitly are an options terminator
    (`--` or a bare `-`), a bare `+` under this model's rule for it, a long
    option, a `-`/`+` cluster, and a plain operand. That enumeration is
    MEASURED-COMPLETE over the probes recorded at the rule tables, not proven
    complete over the grammar — a previous version of this docstring claimed
    the latter and has now been falsified THREE times (see the residual-class
    note in the module docstring)."""
    letters = SHELL_OPTION_ARITY[model]
    long_value = SHELL_LONG_VALUE_OPTS[model]
    # On this model a plain operand is a command line even with no `-c`, so
    # every "is there a script here" test below is `saw_c or first_is_command`.
    first_is_command = SHELL_FIRST_OPERAND[model] == SHELL_FIRST_OPERAND_COMMAND
    i = 0
    saw_c = False
    while i < len(args):
        tok = args[i]
        if tok.startswith("-") and tok.strip("-") == "":
            i += 1                        # `--` (or a bare `-`): options end
            # …and on ksh93 what follows a terminator is still a command line:
            # `ksh -- -c <cmd>` and `ksh - -c <cmd>` both answer "-c: not
            # found", i.e. the `-c` itself was run as the command.
            if i < len(args) and (saw_c or first_is_command):
                return i, not saw_c
            return None
        if tok == "+":
            # bash/dash read a bare `+` as a no-op and keep parsing options;
            # zsh/ksh93 read it as end-of-options. Both leave the script as the
            # first operand after it once `-c` has been seen — and on ksh93 that
            # operand is a command line without one (`ksh + -c <cmd>` answers
            # "-c: not found"; `ksh + + -c <cmd>` answers "+: not found").
            if SHELL_BARE_PLUS[model] == SHELL_PLUS_SKIP:
                i += 1
                continue
            i += 1
            if i < len(args) and (saw_c or first_is_command):
                return i, not saw_c
            return None
        if tok.startswith("--"):
            i += 2 if tok in long_value else 1
            continue
        if tok[:1] == "+" and "-" in tok[1:]:
            # a `+` token with a dash in its body — a third plus shape
            action = SHELL_PLUS_DASH[model]
            if action == SHELL_PLUSDASH_REJECT:
                return None               # the shell rejects it; nothing runs
            if action == SHELL_PLUSDASH_BARE_ENDS_OPTIONS:
                if tok != "+-":
                    return None           # every longer form is rejected
                i += 1
                # `saw_c` alone, deliberately: zsh is the only measured model
                # that ends options at `+-`, and its first operand is a script
                # FILE. Writing `or first_is_command` here would be untestable
                # under every model in the table — add it together with a model
                # that is BOTH, if one is ever measured.
                if i < len(args) and saw_c:
                    return i, False
                return None
            # ksh93 ignores the dashes, so the token is just an ordinary
            # cluster. No stripping is needed and none is done: a `-` is not a
            # letter in any model's map, so the cluster walk already treats it
            # as a no-operand character and walks past it. (Removing an earlier
            # `.replace("-", "")` here was forced by the mutation proof — with
            # the strip in place, deleting it changed no fixture's answer, i.e.
            # it was untestable dead work.) The only reason this branch exists
            # is that `_is_shell_option` rejects a `+` token whose body starts
            # with `-`.
            extra, has_c = _shell_cluster(
                tok, letters, args[i + 1] if i + 1 < len(args) else None)
            saw_c = saw_c or has_c
            i += 1 + extra
            continue
        if _is_shell_option(tok):
            extra, has_c = _shell_cluster(
                tok, letters, args[i + 1] if i + 1 < len(args) else None)
            saw_c = saw_c or has_c
            i += 1 + extra
            continue
        # a plain operand: the `-c` script, or — on a model whose first operand
        # is a command line — that command line
        if saw_c or first_is_command:
            return i, not saw_c
        return None
    return None


def _shell_scripts(args: list[str], shell: str) -> list[str]:
    # RAW docstring: it quotes a shell probe containing `\$0`, and that
    # backslash is load-bearing (see the ksh93 measurement below). Without the
    # `r` prefix python reads `\$` as an invalid escape sequence and warns.
    r"""Every candidate script for a shell of this NAME, in model order and
    deduplicated. One entry for a name that is a single implementation; for the
    ambiguous `sh` and `ksh` this is the UNION over every model that name could
    be, which is what keeps a divergence between them from becoming a silent
    miss. Both unions include ksh93, so both carry its no-`-c` reading — which
    is the whole reason `sh <cmd>` and `ksh <cmd>` are scanned at all.

    A `-c` script is ONE token: what follows it is $0 and the positional
    parameters, and none of it is executed. ksh93's no-`-c` first operand is
    NOT one token — the operands behind it are appended to the command line —
    so this is the single place that difference is applied, by joining them in.
    Getting it wrong is a silent MISS, not a cosmetic error: `ksh X=1 <vcs>
    <publish> origin main` really publishes (measured — `ksh X=1 git
    --version` prints git's own version), and reading only the first operand
    resolves it to "X=1" and reports nothing.

    HOW they are appended, measured rather than assumed: ksh93 executes the
    operand text with the literal `"$@"` appended to it. The proof is its own
    error message — `ksh 'if true; then echo T; fi' P1` answers `syntax error
    at line 1: `"$@"' unexpected`, which is ksh93 quoting the text it built.
    So the trailing operands arrive as WORDS on the LAST simple command, never
    as syntax: `ksh 'echo A' '|' wc -l` prints "A | wc -l" (not a pipeline),
    `ksh 'echo A' ';' 'echo B'` prints "A ; echo B" (not two commands), and
    `ksh 'echo A; echo B' P1` prints "A" then "B P1".

    So the reconstruction is the first operand as SOURCE plus each appended
    operand re-serialized as ONE WORD — which is what `"$@"` expands to.
    Verified as a whole rather than per-symptom: 25 operand vectors (spaces,
    apostrophes, double quotes, `;` `&&` `|` `>`, a substitution, a backtick,
    `--`, `-c`, `{`, `()`, `*`, `~`, `#x`, a backslash, an assignment, a
    reserved word, the empty string) were handed to `/bin/ksh` with an operand
    that prints each received word, and the words it printed were compared with
    the words this reconstruction tokenizes to. 25/25 agree.

    It is NOT exact, and the inexactness is downstream of this function where
    no serialization can reach it. `tokenize` discards quoting, so `A=1` and
    `'A=1'` reduce to the same token VALUE; a later pass that reads values —
    the leading-assignment stripper, the control-word stripper — therefore
    treats an appended operand that merely LOOKS like an assignment or a
    keyword as one, while ksh93 treats it as a command NAME (`ksh "" A=1 <vcs>
    <publish>` answers "A=1: not found" and publishes nothing; this gate
    reports it). That is over-reporting, never a miss: stripping a leading word
    only exposes more of the segment. It is recorded here as a residual rather
    than papered over.

    Quoting every appended operand UNCONDITIONALLY does not fix that, and the
    reason first written here for not doing it was wrong. It said the change
    would be INERT — "the two serializations tokenize identically on all 25
    vectors" — which is true, and is not the whole answer, because `tokenize`
    is not the only consumer of the text this function returns. What comes back
    from here goes to `scan_command_text`, which reads the SAME string twice:
    once through `tokenize`, and once as raw text through `quoted_spans`, whose
    entire job is to notice quotes. Quoting an operand that needed no quoting
    therefore invents a quoted span that was not in the invocation. Measured,
    on `ksh 'sh -c true' <vcs>-<pack>` (the dashed pack-sender executable as
    the appended operand): minimal `shlex.quote` reconstructs
    `sh -c true <vcs>-<pack>`, whose `quoted_spans` is empty and which scans
    CLEAN; always-quote reconstructs `sh -c true '<vcs>-<pack>'`, whose
    `quoted_spans` is `['<vcs>-<pack>']` — read as a command line, and
    REPORTED. Both tokenize to the same four tokens, exactly as the old note
    said. And the report would be FALSE: ksh93 runs the operand text with
    `"$@"` after it, so the appended word becomes the `-c` script's $0 and
    nothing executes it. Measured on ksh93u+ 2012-08-01:
    `ksh 'sh -c "echo RAN:\$0"' MARKER` prints `RAN:MARKER`, and
    `ksh 'sh -c true' /usr/bin/whoami` prints nothing and exits 0. The
    BACKSLASH in that first probe is load-bearing and was missing from an
    earlier draft of this note: without it the outer ksh expands `$0` before
    the inner shell ever sees it, and the same command prints
    `RAN:sh -c echo RAN:MARKER` — a different mechanism proving nothing.
    So minimal quoting is not the
    inert choice, it is the CORRECT one: always-quote would have added a false
    positive. An equivalence argued through one consumer of a value is an
    argument about that consumer, not about the value.

    A plain space-join was tried first and is WRONG, in the direction that
    costs findings. Re-joining an operand as raw source splits it: `ksh 'sh
    -c' '<vcs> <publish>'` became `sh -c <vcs> <publish>`, where the nested
    shell reads `<vcs>` as its whole `-c` script and demotes `<publish>` to
    $0, and `ksh '<vcs> -C' '/tmp/no such' <publish>` became five tokens, so
    `-C` ate `/tmp/no` and "such" became the subcommand. Both invocations
    really run (measured with `--version` in place of the subcommand) and both
    scanned CLEAN. The earlier note here claimed the join "can never
    UNDER-detect" because the words land at the same textual position; the
    position is the same and the TOKENIZATION is not, and every parser
    downstream of this point is token-sensitive. Quoting also removes the
    over-detection the join had in the other direction: a `;` or `&&` handed
    over as an operand is now a literal word, which is what ksh93 does with it
    (`ksh 'echo A' ';' <vcs> --version` prints "A ; <vcs> --version").

    The reconstruction can LENGTHEN a string — an operand carrying
    apostrophes costs more to re-serialize than it spent in the source — which
    made it the first producer in this file to break the walk's old
    "every nested string is strictly shorter" termination bound. A 50-byte line
    reconstructing to 54 was silently DROPPED. `scan_command_text` now
    terminates on a lexicographic pair instead; see its docstring. Note that
    under the quote-NAIVE reading this producer also raises the token-value
    sum — naive tokens keep their quote characters, so re-quoting them adds
    value bytes — which is why that reading's pair counts tokens rather than
    weighing them."""
    out: list[str] = []
    for model in SHELL_MODELS[shell]:
        found = _shell_script_index(args, model)
        if found is None:
            continue
        idx, from_fallback = found
        if from_fallback:
            # the operand text as SOURCE, then each appended operand as ONE
            # shell WORD — which is what `"$@"` expands to
            cand = args[idx] + "".join(
                " " + shlex.quote(a) for a in args[idx + 1:])
        else:
            cand = args[idx]
        if cand not in out:
            out.append(cand)
    return out


def _short_cluster_operand(tok: str, value_chars: str, optional_chars: str = ""):
    """Read ONE short-option token as a cluster: which letter takes an operand,
    where that operand is, and whether the FOLLOWING token is part of it.

    Returns `(letter, attached, takes_next)`. `attached` is the rest of the
    token after that letter, or None when the letter ends the token.
    `takes_next` says the operand is the following token. `(None, None, False)`
    means no letter in the cluster takes an operand at all, so the token is a
    lone flag and consumes nothing.

    This is getopt(3)'s cluster rule, and the only place the gate models it: the
    FIRST letter that takes an operand — of EITHER kind — wins, and the
    remainder of the token is its value, never further flags. Both kinds
    terminate the walk; they differ only in what happens when the letter ENDS
    the token:

      * MANDATORY (`value_chars`): the operand is the following token. This is
        what makes `env -vu <x>`, `xargs -tE <x>`, `time -po <x>`,
        `exec -ca <x>` and `sudo -nu <x>` consume `<x>` and reach the command
        behind it instead of stopping at it.
      * OPTIONAL (`optional_chars`): there is NO operand and nothing more is
        consumed. GNU `xargs -lE` is `-l` with the attached value "E" — the
        real tool answers `invalid number "E" for -l option` and runs nothing —
        so reading it as a mandatory `-E` that eats the next token reports a
        command the invocation never executes.

    A letter that takes NO operand does not terminate the walk, so the command
    behind it is still reached (`env -uSx` unsets a variable named "Sx" and
    splits nothing), and an operand-taking letter EARLIER in the cluster hides
    what follows it (`gh api -qX POST` has no method flag). Every carrier and
    both forge option sets are read through this. A letter in BOTH sets is
    treated as mandatory: under-consuming leaves the tool's own operand as the
    head of the segment, and when that operand is a text-emitter its exemption
    hides the command — the exact silent miss this walk exists to close."""
    body = tok[1:]
    for i, ch in enumerate(body):
        mandatory = ch in value_chars
        if not mandatory and ch not in optional_chars:
            continue                      # a no-operand letter: keep walking
        rest = body[i + 1:]
        if rest:
            return ch, rest, False
        return ch, None, mandatory
    return None, None, False              # a cluster of no-operand letters


def _ssh_option_pair(raw: str) -> tuple[str, str]:
    """(keyword, value) from ONE ssh `-o` operand, in ssh_config's real
    separator grammar.

    A keyword is separated from its value by whitespace, by `=`, or by `=` with
    whitespace on either side — and "whitespace" is `SSH_SEPARATOR_WS`, not
    Python's. All four spellings are the guard's measurements with `ssh -G`;
    reading only `Keyword=value` and reading only a literal SPACE were each a
    miss there, and this gate had NEITHER reading until now.

    The operand may also OPEN with whitespace, which is a configuration LINE's
    ordinary indentation and is accepted on `-o` too. MEASURED here with
    `ssh -G`: a leading space and a leading tab both resolve to the same
    keyword and value as the bare spelling. Not skipping it made the keyword
    the EMPTY string, so the option carried nothing and the form was a miss —
    gate round 8 #1, and a shared one: the runtime guard's copy has the same
    defect and it is routed back.

    Returns the raw remainder, spaces and all: the caller decides whether the
    keyword is one that carries a command."""
    i, n = 0, len(raw)
    while i < n and raw[i] in SSH_SEPARATOR_WS:
        i += 1
    start = i
    while i < n and raw[i] not in SSH_SEPARATOR_WS and raw[i] != "=":
        i += 1
    key = raw[start:i]
    while i < n and raw[i] in SSH_SEPARATOR_WS:
        i += 1
    if i < n and raw[i] == "=":
        i += 1
        while i < n and raw[i] in SSH_SEPARATOR_WS:
            i += 1
    return key, raw[i:]


def _string_carrier_nested(prog: str, args: list[str]) -> list[str]:
    """The command lines a string-executing carrier's OPTIONS carry.

    Only the options — see `STRING_EXEC_SPEC` for what is deliberately not
    mirrored from the runtime guard. The walk is getopt(3)'s, through the same
    `_short_cluster_operand` every other carrier here uses, so an operand-taking
    letter earlier in a cluster hides the command-bearing one exactly as the
    real parser does.

    Termination: every string returned is a SUBSTRING of one argv token, and the
    program token and the option token (or its option prefix) are dropped, so
    both of `scan_command_text`'s measures fall. Quote-aware, the sum of token
    VALUE lengths loses at least the program token. Quote-naive, a naive token
    is whitespace-free, so a substring of one is at most one token, against a
    parent holding at least the program and the option."""
    spec = STRING_EXEC_SPEC[prog]
    out: list[str] = []
    operands = 0
    terminal = False
    i, n = 0, len(args)
    while i < n:
        if spec["destinations"] is not None and operands >= spec["destinations"]:
            break                         # past the destination: not our argv
        tok = args[i]
        if tok == "--":
            # getopt(3)'s option TERMINATOR, and it is exact: the token after it
            # is the destination however it is spelled. MEASURED with `ssh -G`:
            # `ssh -- -o <keyword-form> <host>` configures NOTHING and reports
            # "hostname contains invalid characters", because the option token
            # became the destination. Reading past it manufactured a command
            # line the tool never runs — gate round 8 #3, and a shared defect:
            # the runtime guard skips `--` as an ordinary long option too.
            break
        if tok in spec["terminal"]:
            # Recorded rather than `break`ed on: a command-bearing option may
            # have been read ALREADY, and it still never runs. `su -c <cmd>
            # --help <user>` prints the usage and exits.
            terminal = True
            i += 1
            continue
        if tok in spec["long_value"]:
            value = args[i + 1] if i + 1 < n else ""
            if tok in spec["cmd_opts"]:
                out.append(value)
            i += 2
            continue
        name, sep, attached_value = tok.partition("=")
        if sep and name in spec["long_value"]:
            # The ATTACHED spelling of a long option. Both are the same option
            # to a GNU-style parser, and only the separate one was read — gate
            # round 8 #2. The quoted-operand pass hides how much that mattered:
            # `--command='<cmd>'` is caught by it, and the same option written
            # with an escaped space instead of quotes is not caught by anything.
            if name in spec["cmd_opts"]:
                out.append(attached_value)
            i += 1
            continue
        if tok.startswith("--"):
            i += 1
            continue
        if _is_short_option(tok):
            letter, attached, takes_next = _short_cluster_operand(
                tok, spec["value_chars"])
            if letter is not None:
                operand = attached
                if takes_next:
                    operand = args[i + 1] if i + 1 < n else ""
                    i += 2
                else:
                    i += 1
                if ("-" + letter) in spec["cmd_opts"]:
                    if spec["cmd_keywords"]:
                        key, value = _ssh_option_pair(operand or "")
                        if key.lower() in spec["cmd_keywords"]:
                            out.append(value)
                    else:
                        out.append(operand or "")
                continue
            i += 1
            continue
        operands += 1
        i += 1
    if terminal:
        return []
    return [c for c in out if c.strip()]


def _strip_prefix_tokens(toks: list[str],
                         nested: list[str]) -> list[str]:
    """Drop everything ahead of the real program: assignments, control words,
    prose labels / mapping keys, punctuation, and the execution carriers with
    their own argument shape. A carrier whose operand IS a command line
    (`eval`, `env -S`) appends that command line to `nested` and returns no
    tokens — the carrier consumed the rest of the segment."""
    while toks:
        raw = toks[0]
        prog = _program(raw)
        if _is_assignment(raw):
            toks.pop(0)
            continue
        if prog == "":                      # bare punctuation: { } ( ) ! [
            toks.pop(0)
            continue
        if raw.startswith("-") and raw.strip("-") == "":
            toks.pop(0)                     # the `--` option terminator
            continue
        if prog in CONTROL_WORDS:
            toks.pop(0)
            continue
        if prog not in KNOWN_PROGRAMS and raw.endswith(":"):
            toks.pop(0)                     # a prose label or a mapping key
            continue
        if prog in EVAL_WRAPPERS:
            # eval concatenates its operands and executes the result.
            toks.pop(0)
            if toks:
                nested.append(" ".join(toks))
            return []
        if prog in WRAPPERS:
            spec = WRAPPER_SPEC[prog]
            value_opts = spec["value"]
            short_chars = WRAPPER_SHORT_VALUE_CHARS[prog]
            optional_chars = WRAPPER_OPTIONAL_SHORT_CHARS.get(prog, "")
            positional = spec["positional"]
            is_env = prog == "env"
            split_string = None
            toks.pop(0)
            while toks:
                tok = toks[0]
                if _is_assignment(tok):
                    toks.pop(0)
                    continue
                if not tok.startswith("-"):
                    if positional > 0:
                        positional -= 1     # timeout's duration operand
                        toks.pop(0)
                        continue
                    break
                if is_env and tok in ENV_SPLIT_OPTS:
                    toks.pop(0)
                    if toks:
                        split_string = toks.pop(0)
                    continue
                if is_env and "=" in tok and tok.split("=", 1)[0] in ENV_SPLIT_OPTS:
                    split_string = tok.split("=", 1)[1]
                    toks.pop(0)
                    continue
                if (short_chars or optional_chars) and _is_short_option(tok):
                    # A short-option token, possibly a CLUSTER — `-n5`, `-vu`,
                    # `-tE`, `-po`, `-ca`, `-Sx`, `-vSx`. The first
                    # operand-taking letter takes the rest of the token, or the
                    # NEXT token when it ends this one; a cluster of no-operand
                    # letters consumes nothing and the command behind it is
                    # still reached.
                    letter, operand, takes_next = _short_cluster_operand(
                        tok, short_chars, optional_chars)
                    if letter is not None:
                        toks.pop(0)
                        if takes_next and toks:
                            operand = toks.pop(0)
                        if is_env and letter == ENV_SPLIT_CHAR:
                            split_string = operand
                        continue
                if tok in value_opts:
                    del toks[0:2]
                else:
                    toks.pop(0)
            if split_string is not None:
                # -S's string is spliced into env's OWN argv: it may inject
                # further env options (`env -S "-i cmd"`), and the operands
                # after it are the command's arguments, not a new command. So
                # the expansion is re-parsed as an env argv.
                nested.append(" ".join(["env", split_string] + toks))
                return []
            continue
        break
    return toks


def _scan_tokens_anywhere(toks: list[str], nested: list[str]) -> list[str]:
    """Apply the VCS / forge rule tables at EVERY token position of a prose
    segment, not only at its head. Nested command lines found on the way — an
    alias whose value is a shell command — are appended to `nested` whether or
    not this pass reports a form of its own."""
    for i, tok in enumerate(toks):
        name = _program(tok)
        if name == VCS:
            forms, sub = _scan_vcs(toks[i + 1:])
            nested += sub
            if forms:
                return forms
        elif name == FORGE:
            forms = _scan_forge(toks[i + 1:])
            if forms:
                return forms
        elif name.startswith(VCS + "-") and name[len(VCS) + 1:] in VCS_EGRESS:
            return [name]
        elif name.startswith(VCS + "-") \
                and name[len(VCS) + 1:] in VCS_PAIR_FAMILIES:
            # The dashed FAMILY executable, at a position other than the head.
            # Its one-word sibling was already read here, and leaving this out
            # meant a shipped sentence naming the family executable beside its
            # operation scanned clean while the same command at the head of a
            # line did not — an inconsistency in the pass whose whole job is
            # prose.
            family = name[len(VCS) + 1:]
            op = _vcs_pair_operation(family, toks[i + 1:])
            if op is not None:
                return ["%s-%s %s" % (VCS, family, op)]
    return []


def _dedup(items: list[str]) -> list[str]:
    """Order-preserving de-duplication of a segment's nested command lines.

    A segment whose head is the VCS is read TWICE — once by its own rule, and
    once more at position 0 of the prose pass, which is the same call — so a
    nested command line it yields (an alias whose value is a shell command) is
    produced twice. The walk's visited set already collapses that, so this
    changes no verdict; it keeps `analyze`'s contract equal to what it means,
    which is what the parser fixtures assert against."""
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def analyze(tokens: list[str]) -> tuple[list[str], list[str], str]:
    """(findings, nested command strings to scan, program basename) for ONE
    command segment."""
    forms, nested, prog = _analyze(tokens)
    return forms, _dedup(nested), prog


def _analyze(tokens: list[str]) -> tuple[list[str], list[str], str]:
    nested: list[str] = []
    toks = _strip_prefix_tokens(list(tokens), nested)
    if not toks:
        return [], nested, ""
    prog = _program(toks[0])
    args = toks[1:]
    forms: list[str] = []
    if prog in SHELLS:
        # Finding the script is a PARSE, under this shell's own option arity —
        # and under every model it could be when the name is ambiguous.
        nested += _shell_scripts(args, prog)
        return [], nested, prog
    elif prog == VCS:
        forms, vcs_nested = _scan_vcs(args)
        nested += vcs_nested
    elif prog.startswith(VCS + "-") and prog[len(VCS) + 1:] in VCS_EGRESS:
        forms = [prog]                      # the dashed plumbing executable
    elif prog.startswith(VCS + "-") and prog[len(VCS) + 1:] in VCS_PAIR_FAMILIES:
        # A dashed FAMILY executable: the family name is in the PROGRAM, so its
        # operation is the first argument that is neither an option nor an
        # option's operand. The same walk as the two-word form, entered one
        # level further along.
        family = prog[len(VCS) + 1:]
        op = _vcs_pair_operation(family, args)
        if op is not None:
            forms = ["%s-%s %s" % (VCS, family, op)]
    elif prog == FORGE:
        forms = _scan_forge(args)
    if prog in STRING_EXEC_SPEC:
        # ADDITIVE, and deliberately not an `elif`: the carrier's own option
        # grammar contributes nested command lines, and the prose pass below
        # still runs on the segment (these names are NOT in PROSE_EXEMPT).
        nested += _string_carrier_nested(prog, args)
    if forms:
        return forms, nested, prog
    # Prose (or an unknown program, or a known one whose own rule found
    # nothing): a forbidden form spelled LATER in the segment — "never run
    # <vcs> <publish> from a session" — still teaches the retired mechanic and
    # is reported. Text-emitters are exempt by contract: `echo <vcs> <publish>`
    # prints a string and must stay clean.
    if prog not in PROSE_EXEMPT:
        return _scan_tokens_anywhere(toks, nested), nested, prog
    return [], nested, prog


def quoted_spans(text: str) -> list[str]:
    """The contents of every quoted span, in BOTH shell quote styles. A quoted
    operand of anything but a NON_EXECUTING program is read as a command line:
    that is what catches an execution carrier this scanner does not know by
    name (`ssh host "<cmd>"` and `ssh host '<cmd>'` alike) and prose that
    spells a command inside quotes. It reads EVERY quote form through the one
    quoting model, so an ANSI-C span hands back its DECODED value."""
    spans: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "\\" and i + 1 < n:
            i += 2
            continue
        kind, body_start = _quote_at(text, i)
        if kind is None:
            i += 1
            continue
        end, nxt = _quote_end(text, body_start, kind)
        value = _quote_value(text[body_start:end], kind)
        if value.strip():
            spans.append(value)
        i = nxt
    return spans


def scan_command_text(text: str, quote_aware: bool) -> list[str]:
    """Scan one command-bearing string, following nested command lines — shell
    -c scripts, `eval` / `env -S` operands, and the quoted operands of any
    program that is not purely text-emitting — to ANY depth. There is no fixed
    depth cap.

    Termination is LEXICOGRAPHIC, on a PAIR, and the pair's first component is
    not the same quantity in the two readings this walk runs under. Two wrong
    answers preceded it, and both are worth keeping because the second was made
    while correcting the first.

    It was once by LENGTH — "every nested string is strictly shorter than the
    string it came from" — which was a true invariant of every producer this
    walk had, until the ksh93 operand reconstruction became the first one that
    can GROW a string: it re-serializes appended operands as quoted words, and
    quoting an operand that already spent its source budget on escapes costs
    more than it saves. A 50-byte line reconstructing to 54 bytes was then
    DROPPED, unscanned — `<vcs> -c "foo.bar=a'b"` twice over, which really
    reaches the VCS. The invariant was stated right here in this docstring and
    a producer that violates it was added without re-reading it; the length
    test is gone rather than widened, because a bound that silently discards
    work is a miss generator whatever its constant.

    Its replacement was stated here as one measure — "every producer builds its
    nested string from token VALUES and DROPS the program token, so the sum of
    token-value lengths strictly decreases" — and THAT WAS FALSE TOO, about a
    producer this same function calls a dozen lines below the docstring.
    `quoted_spans` does not drop the program token: it reads the segment's RAW
    TEXT, so a program token that is itself quoted comes back whole. Feed the
    walk `'abc'` and the parent tokenizes to ['abc'], the nested string is
    'abc', and the measure goes 3 -> 3 — no decrease at all. The claim was
    checked against the producers that hand back an OPERAND and not against the
    one that can hand back a program.

    What does bound the walk is a pair of non-negative integers that falls
    lexicographically at every producer step:

      * QUOTE-AWARE (`quote_aware=True`) — the reading that has a
        `quoted_spans` pass — **(sum of token-value lengths, serialized
        length)**. Every `analyze` producer builds its string out of token
        VALUES of the segment and sheds a strictly positive amount of that
        value, so the first component strictly falls. WHAT it sheds varies, and
        a loose summary of that is what made both earlier versions of this
        argument wrong, so enumerate rather than generalise: the `eval` join
        and both `_shell_scripts` forms (a `-c` script, the ksh93
        reconstruction) drop the program token whole, plus whatever
        `_strip_prefix_tokens` and the shell option walk consumed ahead of the
        operand. The VCS alias's shell-valued producer sheds more than a token:
        its string is the INTERIOR of one parent token past the alias marker
        (so at least the `<prefix><name>=!` characters are gone) plus the
        invocation's remaining operands re-serialized, whose token VALUES are
        unchanged by the quoting — and the program token and the config option
        are dropped whole on top of that. The `env -S` expansion does NOT drop a whole token in general
        — it re-emits `env`, and with an ATTACHED operand it strips an option
        PREFIX off a token rather than removing one: `env -Sx` (tokens
        `['env', '-Sx']`, mass 6) becomes `env x` (`['env', 'x']`, mass 4).
        With a separate operand (`env -S x`, mass 6) the `-S` token does go
        whole, to the same `env x`. Either way at least the two characters of
        `-S` are gone. The quote
        characters `shlex.quote` adds are stripped again the moment the child
        is tokenized, which is exactly why a LONGER string can still be a
        lighter one. `quoted_spans` is the producer that discards no token at
        all — it can hand back a quoted PROGRAM token whole — so it can leave
        the first component untouched; but what it returns is the INTERIOR of a
        quoted run of the segment, shorter by at least its two delimiters, so
        on a tie the second component falls.
      * QUOTE-NAIVE (`quote_aware=False`) — **(token count, serialized
        length)**. `quoted_spans` is not consulted here at all (it sits behind
        the `quote_aware` guard), and the token-value measure is not merely
        unnecessary in this reading, it is FALSE: naive tokenization keeps the
        quote characters INSIDE the token, so re-serializing an operand that
        already carries quotes really does add value bytes. Not hypothetical:
        it happens on this repository's own tracked files during an ordinary
        run — for example a 26-byte segment reached from the ksh93 prose in
        `_shell_scripts`, which reconstructs to 44 bytes with its token-value
        sum rising 24 -> 43. (HOW MANY such edges a run has is deliberately not
        stated: that number is counted over a corpus containing this very
        paragraph, and would decay exactly as the totals below do.) What falls
        instead is the token COUNT: naive
        tokenization breaks on whitespace and nothing else, so every naive
        token is whitespace-free, and `shlex.quote` of a whitespace-free token
        is whitespace-free too. Each producer therefore emits at most one token
        per argument it keeps. The `eval` join and both `_shell_scripts` forms
        drop the program token, so the count strictly falls; so does a
        SEPARATE-operand `env -S x`, which drops the `-S` token. The VCS
        alias's shell-valued producer emits at most one token for the alias
        value (its text is a substring of ONE naive token, so it carries no
        whitespace) plus one per remaining operand, against a parent that
        additionally holds the program token, the config option and the alias
        NAME — three tokens fewer at minimum. The count TIES
        on every ATTACHED `env -S` form, because there the option prefix comes
        off a token instead of the token coming off the list — `env -Sx` and
        `env -vSx` and `env --split-string=x` all become `env x`, two tokens
        for two. On those the serialized length carries it, and by more than a
        byte: 7 -> 5, 8 -> 5, 20 -> 5.

    Checked, not just argued. Every producer edge of this walk was measured
    against both pairs, over three corpora together: the selftest fixtures,
    every tracked file in this repository, and 1800 adversarial nestings built
    from shell heads crossed with quote-carrying operands. ZERO violations of a
    strict lexicographic decrease for the pair each reading uses. The wrong
    pairing fails loudly in both directions — (token count, length) applied
    quote-aware and (token-value sum, length) applied quote-naive each violate
    on hundreds of edges of that same corpus — so the two first components are
    NOT interchangeable and neither covers both readings, which is why this
    argument is written per reading instead of as one sentence.

    The edge TOTALS are deliberately not quoted here, and that omission is the
    point rather than laziness. This corpus includes this repository's own
    tracked files, this file among them, so any total is a function of the
    prose you are reading and goes stale the moment anyone edits it: the first
    draft of this paragraph quoted 8306 quote-aware edges, and adding the
    paragraphs above moved it to 8380 in the same commit. A self-referential
    count is a claim that falsifies itself on the next edit — exactly the class
    the MODULE docstring calls (e). What is stable, and load-bearing, is the
    ZERO. Re-run it rather than trusting a figure: walk the producers
    `scan_command_text` walks (`analyze`'s nested list, plus `quoted_spans`
    when `quote_aware`) and assert that the pair for that reading strictly
    decreases from parent to child.

    The visited set is a de-duplicator, and that is all it is. It stops a
    string that RECURS from being re-scanned; it does not stop a string that
    GROWS. A future producer that broke the measure above by emitting a longer
    string every round would never repeat one, so the set would never fire —
    it would only make the runaway consume memory as fast as it consumes time.
    Do not read it as a safety net for the termination argument; if you add a
    producer, check it against the pair for its reading. Removing `seen.add`
    changes no answer today — the pair terminates the walk on its own and the
    findings are deduplicated anyway — so that mutation is recorded as
    expected-insensitive in the mutation harness rather than left to look like
    an untested branch."""
    out: list[str] = []
    work = [text]
    seen = {text}
    while work:
        cur = work.pop()
        for segment in split_commands(cur, quote_aware):
            toks = tokenize(strip_markdown_prefix(segment), quote_aware)
            forms, nested, prog = analyze(toks)
            out += forms
            if quote_aware and prog and prog not in NON_EXECUTING:
                nested += quoted_spans(segment)
            for script in nested:
                if script not in seen:
                    seen.add(script)
                    work.append(script)
    return out


def scan_text(text: str) -> list[tuple[int, str]]:
    """[(line number, form)] for one file's content, deduplicated + sorted."""
    found: set[tuple[int, str]] = set()
    raw_lines = text.split("\n")
    fenced = _literal_lines(raw_lines)
    normalized = [strip_markdown_prefix(line) for line in raw_lines]
    lines = join_continuations(normalized)
    for lineno, logical in lines:
        for form in scan_command_text(logical, True):
            found.add((lineno, form))
        for span in code_spans(logical):
            for form in scan_command_text(span, True):
                found.add((lineno, form))
        if not shell_quoting_is_balanced(logical):
            for form in scan_command_text(logical, False):
                found.add((lineno, form))
        rendered = markup_stripped(logical)
        if rendered != logical:
            for form in scan_command_text(rendered, True):
                found.add((lineno, form))
    # A soft-wrapped Markdown paragraph renders as one sentence, so a form can
    # straddle two physical lines with no continuation backslash. Scan each
    # adjacent non-blank pair as one rendered line and keep only what neither
    # line yields alone, reported at the first of the two.
    for idx in range(len(lines) - 1):
        lineno, first = lines[idx]
        next_lineno, second = lines[idx + 1]
        if not first.strip() or not second.strip():
            continue
        # Only a real soft wrap. `## <vcs>` followed by `<publish> mechanics
        # are daemon-owned` is two blocks, not a sentence; `- <vcs>` followed
        # by `- <publish> notifications` is two list items. But a list item's
        # OWN paragraph does soft-wrap onto the next line, so a list item may
        # open a joinable pair.
        if fenced[next_lineno - 1] or fenced[lineno - 1]:
            continue                      # literal command lines, not prose
        first_raw = raw_lines[lineno - 1]
        second_raw = raw_lines[next_lineno - 1]
        if _bq_split(first_raw)[0] != _bq_split(second_raw)[0]:
            continue                      # different blockquote depth
        if _block_kind(second_raw) is not None:
            continue                      # the second line opens a new block
        if _block_kind(first_raw) == "hard":
            continue                      # a heading/fence/row carries nothing
        pair = markup_stripped(first) + " " + markup_stripped(second)
        own = {form for (ln, form) in found if ln in (lineno, next_lineno)}
        forms = set(scan_command_text(pair, True))
        # Same fallback the physical lines get: a pair whose shell quoting is
        # UNBALANCED cannot mean its quotes literally — that is an apostrophe
        # in prose ("The worker's rule is never to run <vcs>" / "<publish>
        # from a session"), which must not hide the form.
        if not shell_quoting_is_balanced(pair):
            forms |= set(scan_command_text(pair, False))
        for form in forms:
            if form not in own:
                found.add((lineno, form))
    return sorted(found)


# --------------------------------------------------------------------------
# drivers


GITLINK_MODE = "160000"


def tracked_files() -> list[str]:
    return [path for path, _is_gitlink in tracked_entries()]


def tracked_entries() -> list[tuple[str, bool]]:
    """Every tracked path, with whether the INDEX says it is a gitlink.

    The mode is read here rather than inferred from the working tree, because a
    directory in the working tree is not evidence of a submodule. Measured after
    the first version of this guard shipped: a tracked REGULAR file replaced by a
    directory was classified as a submodule pointer and skipped, and the gate
    exited 0 saying `0 files scanned, 1 submodule pointer(s) skipped`. That is
    the same reassuring-direction failure the guard was written to close, one
    layer in — the classification was asserted, never established. `git ls-files
    -s` is where the answer actually lives.
    """
    out = subprocess.run(["git", "ls-files", "-s", "-z"],
                         capture_output=True, check=True).stdout
    entries: list[tuple[str, bool]] = []
    for record in out.split(b"\0"):
        if not record:
            continue
        meta, _, raw_path = record.partition(b"\t")
        mode = meta.split(b" ", 1)[0].decode("ascii", "replace")
        entries.append((raw_path.decode("utf-8", "surrogateescape"),
                        mode == GITLINK_MODE))
    return entries


def scan_paths(paths: list[str], gitlinks=()) -> int:
    """Scan every path and report what was ACTUALLY read, not what was asked for.

    A file this scan could not open used to be indistinguishable from a clean
    one: the loop skipped it, the summary printed `len(paths)` as if it had been
    scanned, and the exit status was 0. Measured at the final integration gate —
    a path that does not exist produced `push-form check OK (1 files, 0
    findings)` and exit 0, and the identical file made readable produced a
    finding. That is this delivery's standing defect class landing inside the
    gate itself: the instrument could not see what it was certifying, and it
    failed in the reassuring direction.

    A gitlink is the one legitimate skip — a submodule pointer is a directory in
    the working tree, there is nothing to read, and it is not this repository's
    content. It is counted and reported separately, never as scanned. **That
    classification comes from the INDEX (`gitlinks`), never from the fact that
    the path is a directory**: a tracked regular file replaced by a directory
    would otherwise be waved through as a submodule, which is the same
    reassuring-direction failure one layer in, and was measured on the first
    version of this guard.
    Anything else — a missing file, a permission failure, a checkout race, a
    directory the index does not call a gitlink — is a SETUP error (exit 2), the
    same status this program already uses when it cannot list the tree at all. A
    scan that could not run is not a pass.
    """
    known_gitlinks = frozenset(gitlinks or ())
    hits = 0
    scanned = 0
    skipped_gitlinks: list[str] = []
    unreadable: list[str] = []
    for path in paths:
        try:
            with open(path, "rb") as fh:
                data = fh.read()
        except IsADirectoryError as exc:
            if path in known_gitlinks:
                skipped_gitlinks.append(path)  # submodule: nothing to read
                continue
            unreadable.append(
                "%s: is a directory, and the index does not record it as a "
                "submodule (%s)" % (path, exc))
            continue
        except (FileNotFoundError, PermissionError, OSError) as exc:
            unreadable.append("%s: %s" % (path, exc))
            continue
        scanned += 1
        text = data.decode("utf-8", "surrogateescape")
        for lineno, form in scan_text(text):
            hits += 1
            print("PUSH-FORM FAIL %s:%d: agent-side remote mutation '%s' — "
                  "use the daemon branch-publication tool (worker or lead) or "
                  "the lead-only landing-request tool"
                  % (path, lineno, form), file=sys.stderr)
    if unreadable:
        for line in unreadable:
            print("PUSH-FORM-CHECK: cannot read %s" % line, file=sys.stderr)
        print("PUSH-FORM-CHECK: %d path(s) could not be read — the scan did NOT "
              "cover them, so this run proves nothing about them."
              % len(unreadable), file=sys.stderr)
        return 2
    if hits:
        print("PUSH-FORM-CHECK: %d finding(s)." % hits, file=sys.stderr)
        return 1
    note = ("" if not skipped_gitlinks
            else ", %d submodule pointer(s) skipped" % len(skipped_gitlinks))
    print("push-form check OK (%d files scanned%s, 0 findings)"
          % (scanned, note))
    return 0


# --------------------------------------------------------------------------
# selftest — every form the floor guard denies, plus the benign negatives.
# Fixture command text is assembled from the fragments above, so no case
# appears verbatim in this file and the gate still covers it.

_V = VCS
_G = FORGE
_P = PUBLISH
_K = PACK
_R = PR_SUB
_A = API_SUB
_SUB = SUBTREE
_SVN = SVN
_DC = DCOMMIT
_P4 = P4
_SM = SUBMIT
_LFS = LFS
_PP = PRE_PUBLISH
_REPO = REPO
_REL = RELEASE
_AP = VCS_ALIAS_PREFIX


def _identities_are_right() -> list[str]:
    """Pin the assembled names against INDEPENDENT fragments. Without this the
    fixtures would be circular: a typo in a rule-table constant would be echoed
    by every case built from it, and scanner and selftest would agree on the
    wrong word."""
    expected = [
        ("VCS", _V, j("g", "i", "t")),
        ("FORGE", _G, j("g", "h")),
        ("PUBLISH", _P, j("p", "u", "s", "h")),
        ("PACK", _K, j("s", "end", "-", "pack")),
        ("PR_SUB", _R, j("p", "r")),
        ("API_SUB", _A, j("a", "p", "i")),
        ("SUBTREE", _SUB, j("s", "u", "b", "t", "r", "e", "e")),
        ("SVN_BRANCH", SVN_BRANCH, j("b", "r", "a", "n", "c", "h")),
        ("SVN_TAG", SVN_TAG, j("t", "a", "g")),
        ("SVN_SET_TREE", SVN_SET_TREE, j("s", "e", "t", "-", "t", "r", "e", "e")),
        ("SVN_COMMIT_DIFF", SVN_COMMIT_DIFF,
         j("c", "o", "m", "m", "i", "t", "-", "d", "i", "f", "f")),
        ("SVN", _SVN, j("s", "v", "n")),
        ("DCOMMIT", _DC, j("d", "c", "o", "m", "m", "i", "t")),
        ("P4", _P4, j("p", "4")),
        ("SUBMIT", _SM, j("s", "u", "b", "m", "i", "t")),
        ("LFS", _LFS, j("l", "f", "s")),
        ("PRE_PUBLISH", _PP, j("p", "r", "e", "-", "p", "u", "s", "h")),
        ("REPO", _REPO, j("r", "e", "p", "o")),
        ("RELEASE", _REL, j("r", "e", "l", "e", "a", "s", "e")),
        ("VCS_ALIAS_PREFIX", _AP, j("a", "l", "i", "a", "s", ".")),
    ]
    return ["%s is %r, expected %r" % (name, got, want)
            for name, got, want in expected if got != want]


# --------------------------------------------------------------------------
# The carrier and global-option tables, enumerated INDEPENDENTLY.
#
# Written out by hand from the carriers' own manuals. They are deliberately NOT
# derived from WRAPPER_SPEC / VCS_VALUE_OPTS / FORGE_VALUE_OPTS: a fixture
# generated from the production table cannot fail when that table loses an
# entry, and that drift is exactly what these cases exist to catch. Measured
# before they existed: deleting "--work-tree" from VCS_VALUE_OPTS, or the
# "builtin" row from WRAPPER_SPEC, left the whole selftest exiting 0 while the
# corresponding form became a silent miss (the VCS option) or fell back to the
# prose pass under the wrong program (the carrier).
#
# _tables_are_pinned() compares the two directions, so an entry REMOVED from a
# rule table, an entry ADDED to one without a fixture, and an ARITY change are
# all failures; _table_parser_cases() then exercises every entry through the
# real parse.

# carrier -> the options whose MANDATORY operand is the following token. This
# is a COMPLETE enumeration per carrier of the PLATFORM UNION — every such
# option of every implementation a reader may be running, taken from each tool's
# own option table (GNU coreutils / findutils, util-linux, bash, sudo, OpenBSD
# doas, and the BSD/Darwin manuals for `env` and `xargs`), not from
# WRAPPER_SPEC. It is a union rather than one platform's table on purpose: it
# can only OVER-detect an option, never under-detect one, because on a platform
# lacking the option the invocation is a usage error that executes nothing.
# Copying the production set instead of reading the manuals is how `xargs
# --process-slot-var`, `ionice -P/--pgid`, `ionice -u/--uid`, `doas -a` and the
# BSD-only `xargs -J/-R/-S` and `env -P` stayed missing, each a silent miss
# behind a text-emitter operand.
_CARRIER_VALUE_OPTS = {
    "command":  [],
    "builtin":  [],
    "nohup":    [],
    "setsid":   [],
    "nice":     ["-n", "--adjustment"],
    "ionice":   ["-c", "--class", "-n", "--classdata", "-p", "--pid",
                 "-P", "--pgid", "-u", "--uid"],
    "stdbuf":   ["-i", "--input", "-o", "--output", "-e", "--error"],
    "exec":     ["-a"],
    "time":     ["-f", "--format", "-o", "--output"],
    "timeout":  ["-s", "--signal", "-k", "--kill-after"],
    # -J replstr / -R replacements / -S replsize are BSD/Darwin only.
    "xargs":    ["-a", "--arg-file", "-d", "--delimiter", "-E", "-I", "-J",
                 "-L", "-n", "--max-args", "-P", "--max-procs", "-R", "-S",
                 "-s", "--max-chars", "--process-slot-var"],
    "sudo":     ["-u", "--user", "-g", "--group", "-C", "--close-from",
                 "-D", "--chdir", "-h", "--host", "-p", "--prompt", "-R",
                 "--chroot", "-r", "--role", "-t", "--type",
                 "-T", "--command-timeout", "-U", "--other-user",
                 "-a", "--auth-type", "-c", "--login-class"],
    "doas":     ["-a", "-u", "-C"],
    # -P utilpath is BSD/Darwin only; -L/-U user[/class] are FreeBSD only
    # (documented, not observable here — Darwin's env rejects them); --argv0 is
    # GNU only.
    "env":      ["-u", "--unset", "-C", "--chdir", "-a", "--argv0", "-P",
                 "-L", "-U"],
}

# carrier -> the SHORT letters whose operand is OPTIONAL: they take an attached
# remainder and NEVER the following token. Hand-written like the rest. Getting
# this set WRONG in either direction is a real defect, in opposite ways — a
# letter missing from it is read as mandatory and consumes a token the tool
# leaves alone (a form reported that never runs), while a letter wrongly IN it
# stops consuming a token the tool does take, and if that token is a
# text-emitter its exemption hides the command. Both are pinned; the sets must
# stay disjoint, and a letter that is mandatory on ANY platform belongs in the
# mandatory set.
_CARRIER_OPTIONAL_SHORT_CHARS = {
    # GNU findutils only: -e[eof], -i[replace], -l[max-lines]. BSD xargs
    # answers "invalid option" for all three.
    "xargs":    "eil",
}

# carrier -> the SHORT letters among those options, as one sorted string. Also
# hand-written, and deliberately NOT read from WRAPPER_SHORT_VALUE_CHARS: that
# map is DERIVED from the rule table, so a fixture generated the same way could
# not fail when the derivation itself is wrong. This table is what pins the
# cluster walk — the letter set is the whole of its input, so a letter missing
# here is a cluster the gate reads as a lone flag, which is exactly how
# `env -vu <emitter>` and `xargs -tE <emitter>` hid the command behind them.
# env's -S is included because it clusters like an operand-taking letter even
# though its operand is a command line rather than a value.
_CARRIER_SHORT_VALUE_CHARS = {
    "command":  "",
    "builtin":  "",
    "nohup":    "",
    "setsid":   "",
    "nice":     "n",
    "ionice":   "Pcnpu",
    "stdbuf":   "eio",
    "exec":     "a",
    "time":     "fo",
    "timeout":  "ks",
    "xargs":    "EIJLPRSadns",
    "sudo":     "CDRTUacghprtu",
    "doas":     "Cau",
    "env":      "CLPSUau",
}

# The shells' invocation-option rule, hand-written PER SHELL from the probes
# recorded at the rule table: which letters take an operand and HOW ("next" =
# the following argv element only, the cluster continuing through the letter;
# "attached-or-next" = the rest of the token when there is one, ending the
# cluster, otherwise the following element), and the long options that take a
# separate operand. Enumerated per shell on purpose — ONE arity for all four is
# the exact defect this pins, and it made `zsh -O -c <script>`,
# `zsh|ksh -o<name> -c <script>` and `ksh -c -T <mask> <script>` silent misses.
# The arity WORDS are written out literally rather than as the production
# constants, so renaming a constant cannot make the two sides agree by
# construction.
_SHELL_LETTER_ARITY = {
    "bash": {"o": "next", "O": "next"},
    "dash": {"o": "next"},
    "zsh":  {"o": "attached-or-next"},
    "ksh93": {"o": "attached-or-next-nonoption", "T": "attached-or-next",
              "R": "attached-or-next"},
}
_SHELL_LONG_VALUE_OPTS = {
    "bash": ["--rcfile", "--init-file"],
    "dash": [],
    "zsh":  ["--emulate"],
    "ksh93": [],
}
# What each model does with a BARE `+`: "skip" (a no-op, keep reading options)
# or "end-options" (like `-` and `--`). Hand-written from the probes, and the
# words are literals rather than the production constants so renaming one
# cannot make the two sides agree by construction. A bare `-` is END-OF-OPTIONS
# on all four and needs no per-model entry, which the parser cases pin directly.
_SHELL_BARE_PLUS = {
    "bash": "skip",
    "dash": "skip",
    "zsh":  "end-options",
    "ksh93": "end-options",
}
# What each model does with a `+` token whose BODY contains a `-` (`+-`, `+--`,
# `+-c`, `+-x`, `+-o`). Hand-written from the probes recorded at the rule table.
_SHELL_PLUS_DASH = {
    "bash": "reject",
    "dash": "reject",
    "zsh":  "bare-ends-options",
    "ksh93": "parse-through",
}
# What each model does with its FIRST OPERAND when no `-c` was seen:
# "script-file" (bash/dash/zsh — nothing to scan) or "command-line" (ksh93,
# which opens it as a file first and runs its TEXT when that open fails).
# Hand-written from the probes recorded at the rule table, words as literals so
# renaming a production constant cannot make the two sides agree by
# construction. This is the one shell divergence that needs no option spelling
# at all, so a model dropped from here silently reopens `<name> <cmd>`.
_SHELL_FIRST_OPERAND = {
    "bash": "script-file",
    "dash": "script-file",
    "zsh":  "script-file",
    "ksh93": "command-line",
}
# Which models each shell NAME is read under. `sh` and `ksh` are the ambiguous
# ones and must stay unions, or a divergence between their models is a silent
# miss.
_SHELL_NAME_MODELS = {
    "bash": ["bash"],
    "dash": ["dash"],
    "zsh":  ["zsh"],
    "ksh":  ["ksh93", "dash"],
    "sh":   ["bash", "dash", "zsh", "ksh93"],
}

# The forge CLI's operand-taking SHORT options, hand-written the same way: the
# ones the gate lets consume a token ahead of a subcommand, and ALL of the raw
# API subcommand's — the non-mutating letters included, because an
# operand-taking letter earlier in a cluster turns the mutation letter behind it
# into part of its own operand.
_FORGE_GLOBAL_SHORT_CHARS = "HR"
_FORGE_API_SHORT_CHARS = "FHXfpqt"

# carrier -> one of its flags that takes NO operand AT ALL, used below to build
# the CLUSTER form of each short operand-taking option. It must not be an
# OPTIONAL-operand flag: `xargs -e` would take the following letter as its own
# value, so `-eE` is not a cluster and would test nothing. Empty where the
# carrier has no such flag (`nice` has only -n; every short `stdbuf` option
# takes an operand — note stdbuf is NOT GNU-only, FreeBSD ships it with the same
# mandatory -e/-i/-o), and unused where the carrier has no operand-taking
# option.
_CARRIER_CLUSTER_PREFIX = {
    "command":  "p",
    "builtin":  "",
    "nohup":    "",
    "setsid":   "f",
    "nice":     "",
    "ionice":   "t",
    "stdbuf":   "",
    "exec":     "c",
    "time":     "p",
    "timeout":  "v",
    "xargs":    "t",
    "sudo":     "n",
    "doas":     "n",
    "env":      "v",
}

# carrier -> how many BARE operands precede the command (timeout's duration).
_CARRIER_POSITIONALS = {"timeout": 1}

# carrier -> flags that really take no operand. Every OPTIONAL-operand option
# each carrier has is listed here in full, because that is the direction that
# opens a REAL miss: listing one of them as operand-taking SWALLOWS the program
# behind it. The plain no-operand flags are a selection — they cannot cause
# that drift — so this table is exhaustive where it has to be and representative
# elsewhere. `_tables_are_pinned()` requires none of these in the value set.
#
# There is no companion "policy" table: every entry here is a statement of the
# tool's real arity. The one entry that used to be a policy call, sudo's -h, was
# simply WRONG — sudo documents `-h host` and its parser takes the following
# non-option token — and it is now an operand-taking option instead.
_CARRIER_BARE_FLAGS = {
    "command":  ["-p"],
    "exec":     ["-c", "-l"],
    "setsid":   ["-f", "-w"],
    "ionice":   ["-t"],
    "time":     ["-p", "-v"],
    "timeout":  ["--foreground", "--preserve-status", "-v"],
    # optional-operand: -e/--eof, -i/--replace, -l/--max-lines
    "xargs":    ["-e", "--eof", "-i", "--replace", "-l", "--max-lines",
                 "-r", "-t", "-x", "-0", "-p"],
    # optional-operand: -E/--preserve-env
    "sudo":     ["-E", "--preserve-env", "-b", "-H", "-n", "-k", "-S", "-s",
                 "-i"],
    "doas":     ["-n", "-s", "-L"],
    # optional-operand: --block-signal / --default-signal / --ignore-signal
    "env":      ["-i", "-v", "-0", "--block-signal", "--default-signal",
                 "--ignore-signal", "--list-signal-handling"],
}

# VCS global options that accept an ATTACHED operand ONLY, so the bare token
# must be skipped as a lone flag and must NOT swallow the subcommand behind it.
# Bare `--exec-path` prints the path and exits; `--super-prefix` exists only in
# the `=` form (and is gone from current releases). Both were listed as
# separate-operand options and are now pinned the other way.
_VCS_ATTACHED_ONLY_OPTS = ["--exec-path", "--super-prefix"]

# The `${…}` operators, enumerated by hand into the three classes that decide
# whether the expansion's WORD can be the value. Both directions are real
# defects: an operator wrongly in the value class is a false finding on a valid
# command (a prefix REMOVAL yields a substring of the parameter, never of the
# pattern), and one missing from it is a silent miss at every operation
# position. The replacement class is separate because only the text after the
# SECOND separator survives.
_EXPANSION_VALUE_OPS = [":-", ":=", ":+", "-", "=", "+"]
_EXPANSION_REPLACE_OPS = ["//", "/#", "/%", "/"]
_EXPANSION_NON_VALUE_OPS = ["##", "#", "%%", "%", ":?", "?", "^^", "^",
                            ",,", ",", ":"]

# The inline-alias rule's own constants, hand-written. The marker that makes an
# alias value a SHELL command line rather than a subcommand, and the hop bound —
# both are load-bearing: the marker decides which of two entirely different
# readings a value gets, and the bound decides where an adversarial chain stops
# being resolved and starts being reported.
_VCS_ALIAS_SHELL_PREFIX = "!"
_VCS_ALIAS_MAX_HOPS = 8

# The false spellings the forge CLI's boolean flag parser accepts, hand-written
# from that parser's own accepted set. A spelling MISSING here is a false
# finding on a flag that publishes nothing; one wrongly here reads an enabled
# flag as disabled, which is a MISS.
_PFLAG_FALSE = {"0", "f", "F", "false", "FALSE", "False"}

# The forge CLI's pull-request actions, split by whether they publish code or
# move a remote ref. Both halves are enumerated by hand from that CLI's own
# help, and BOTH matter: an action missing from the first list is a silent miss,
# and one wrongly in it is a false finding on an ordinary read.
_FORGE_PR_MUTATIONS = ["create", "merge", "close", "ready", "edit",
                       "update-branch", "revert", "reopen"]
# Discussion-state and read-only actions, which must NOT be refused.
_FORGE_PR_NON_MUTATIONS = ["comment", "review", "lock", "unlock",
                           "checkout", "checks", "diff", "list", "status",
                           "view"]

# The forge CLI's non-PR families, hand-written. The CONDITION is spelled as a
# word here rather than as the production sentinel, so renaming a sentinel
# cannot make the two sides agree by construction:
#   "always"                 — the action publishes on its own;
#   "push-flag"              — only when the publishing flag is present;
#   "positional-destination" — only when a destination operand is given.
_FORGE_FAMILIES = {
    REPO: {"create": "push-flag", "sync": "positional-destination"},
    RELEASE: {"create": "always", "upload": "always"},
}
# Actions of those same families that this table deliberately does NOT refuse,
# each because it mutates settings, metadata or a remote repository that holds
# none of this checkout's code — destructive is not the same question as
# publishing. Pinned as absent from the rules so a widening cannot happen by
# accident.
_FORGE_FAMILY_EXCLUDED = {
    REPO: ["fork", "delete", "archive", "unarchive", "rename", "edit",
           "view", "clone", "list"],
    RELEASE: ["view", "list", "download", "delete", "edit", "delete-asset"],
}

# The VCS's TWO-WORD publishing forms, enumerated by hand. The words themselves
# are pinned against independent fragments by _identities_are_right(); what THIS
# table pins is the SET — a pair dropped from the rule table, or one added to it
# without a fixture, is a failure in one direction or the other.
_VCS_PAIRS = [(SUBTREE, PUBLISH), (SVN, DCOMMIT), (SVN, SVN_BRANCH),
              (SVN, SVN_TAG), (SVN, SVN_SET_TREE), (SVN, SVN_COMMIT_DIFF),
              (P4, SUBMIT), (LFS, PUBLISH), (LFS, PRE_PUBLISH)]
# Operations of those same families that are read-only or local-only and must
# NOT be refused, so a widening of the writer list cannot happen by accident.
# Representative, not exhaustive — see the note on the forge exclusions.
_VCS_PAIR_EXCLUDED = {
    SVN: ["clone", "init", "fetch", "rebase", "log", "blame", "info",
          "find-rev", "show-ignore", "propget", "migrate", "reset"],
    SUBTREE: ["add", "merge", "split", "pull"],
    P4: ["sync", "rebase", "clone", "branches", "unshelve"],
    LFS: ["status", "track", "pull", "fetch", "install"],
}

# Each family's own options that consume a SEPARATE operand, from that family's
# own usage. Hand-written and deliberately not read from VCS_PAIR_VALUE_OPTS:
# an option MISSING here is read as bare and the operation behind its operand is
# reported when nothing runs, while an option wrongly listed swallows the
# operation itself — a silent miss. The three families this host cannot run are
# empty on purpose; see the rule table.
_VCS_PAIR_OPTS = {
    SUBTREE: ["-P", "--prefix", "--annotate", "-b", "--branch", "--onto",
              "-m", "--message"],
    SVN: [],
    P4: [],
    LFS: [],
}
# …and the family options that take an ATTACHED operand ONLY, which must NOT be
# in the value set: the signing option's key id is optional and attached
# (`-S[=<key-id>]`), so a bare one consumes nothing and the operation behind it
# is still reached.
_VCS_PAIR_ATTACHED_ONLY_OPTS = {SUBTREE: ["-S", "--gpg-sign"]}

# VCS globals whose BARE form makes the tool print and exit, so no subcommand
# runs behind them. Hand-written from that tool's own option list. Both
# directions are real: an option missing here reports a form the tool never
# runs, and one wrongly here hides a subcommand that does.
_VCS_TERMINAL_OPTS = ["--exec-path", "--super-prefix", "--version", "-v",
                      "--help", "-h", "--man-path", "--html-path",
                      "--info-path"]

# The VCS global options that consume the FOLLOWING TOKEN as their value.
_VCS_GLOBAL_VALUE_OPTS = ["-C", "-c", "--git-dir", "--work-tree", "--namespace",
                          "--config-env", "--shallow-file", "--attr-source"]
# The dash options the gate lets consume a token ahead of the forge CLI's
# subcommand. Deliberately wider than that CLI's true global flag set — see
# FORGE_VALUE_OPTS — so this pins the gate's modelled set, not the tool's.
_FORGE_GLOBAL_VALUE_OPTS = ["-R", "--repo", "--hostname", "-H", "--header"]

# …and the per-ACTION ones, which are pinned with the opposite bias and
# therefore separately: this table must be the tool's REAL arity, because an
# option wrongly listed here swallows the destination positional that IS the
# sync action's publish condition, and the finding is then lost. Written out by
# hand, including its short letters, so a derivation error cannot make the
# fixture and the rule table agree on the wrong set. An action with no entry
# belongs to no key here at all — that is what pins "create has none".
_FORGE_ACTION_VALUE_OPTS = {
    (REPO, "sync"): ["-b", "--branch", "-s", "--source"],
}
_FORGE_ACTION_SHORT_CHARS = {(REPO, "sync"): "bs"}
# The string-exec carriers, enumerated INDEPENDENTLY of the rule table — and
# the generated carrier cases below iterate THIS list rather than the rule
# table's set, deliberately. A generator fed from the table it is testing
# cannot see that table SHRINK: it just emits fewer cases and still passes.
# (Measured, not assumed: with the generator reading `SSH_CMD_KEYWORDS`,
# dropping a keyword from it was an insensitive mutation.) Iterating the
# hand-written list turns that shrink into a failing positive, and the pin
# below turns the opposite drift into a failing pin.
#
# Provenance: the four command-bearing keywords are ssh_config(5)'s; the option
# letters are ssh(1)'s usage line; `su`'s are its manual. Same sources as the
# runtime egress guard's copy of this table, which is what it is in lockstep
# with.
_SSH_CMD_KEYWORDS = ["proxycommand", "remotecommand", "localcommand",
                     "knownhostscommand"]
# The separator whitespace, enumerated independently for the same reason. The
# generated cases below cover one spelling per member, but a member the LIST
# does not name generates no case at all, so the pin is what makes the set
# itself falsifiable: with `\n` absent from the generated axis, removing it
# from the rule table passed the whole selftest (gate round 8 #4).
_SSH_SEPARATOR_WS = [" ", "\t", "\r", "\n"]
# The ssh/slogin OPERAND-TAKING option letters, from ssh(1)'s usage line, written
# out here rather than derived — the same discipline as every fixture above, and
# for a measured reason. Found at the final integration gate (slice C round 1c):
# `_SSH_VALUE_CHARS` was read at two sites and pinned at neither, and the parser
# corpus sampled exactly one letter of the twenty-two. Removing `B` left the
# WHOLE selftest at exit 0 while a form carrying a command-bearing option behind
# `-B <operand>` flipped from a finding to clean — the operand was mistaken for
# the destination and the walk stopped before ever reaching the option. Twenty of
# the twenty-two letters survived removal independently. This is the FOURTH
# appearance of one class here: a set consumed at one site and pinned at none.
_SSH_VALUE_CHARS_FIXTURE = "BbcDEeFIiJLlmOoPpQRSWw"
_STRING_EXEC_CARRIERS = ["ssh", "slogin", "rsh", "su"]
_STRING_EXEC_CMD_OPTS = {
    "ssh": ["-o"], "slogin": ["-o"], "rsh": [],
    "su": ["-c", "--command", "--session-command"],
}
_STRING_EXEC_TERMINAL = {
    "ssh": ["-V", "-Q"], "slogin": ["-V", "-Q"], "rsh": [],
    "su": ["-h", "--help", "-V", "--version"],
}
_STRING_EXEC_DESTINATIONS = {"ssh": 1, "slogin": 1, "rsh": 1, "su": None}

# ── four more sets that were READ at one site and PINNED nowhere ──────────────
#
# The merge gate found these by narrowing, which is the only way this class is
# ever found: drop a member from the production set, re-run the selftest, and
# watch it stay green while a real line changes verdict. All four did, and the
# printed totals did not move by one case. MEASURED, at the tip that opened
# this: dropping `--field` from the API body flags turned a request-body
# finding clean; dropping `&` from the separators turned the operation after it
# clean (the neighbouring fixture used `&&`, which takes a different branch and
# proves nothing about `&`); dropping `true` from the emitters turned a quoted
# mention into a false finding.
#
# So each set gets BOTH halves, the way the ssh whitespace set already has
# them: an enumeration written here, compared to production in both directions
# by `_tables_are_pinned` — and a generated case per member AT THE SITE THAT
# CONSUMES IT, so the pin cannot be satisfied by a set nothing exercises. This
# is the fourth appearance of one class (a set covered at one consumption site
# and not the other); the standing note about it is in the docstring.
_API_BODY_FLAGS = ["-f", "-F", "--field", "--raw-field", "--input"]
_API_METHOD_FLAGS = ["-X", "--method"]
_SEPARATOR_CHARS = [";", "|", "&", "`", "(", ")", "\n"]
_NON_EXECUTING = ["echo", "printf", "true", "false"]
# The TEXT-MODEL alphabets: what `trim_token` strips from each end of a token, and
# the ANSI-C simple escapes. Enumerated independently, same reason, same measured
# class as `_SSH_VALUE_CHARS_FIXTURE` above — all three were found together at the
# final integration gate, all three in the UNDER-report direction:
#   · removing `_` from LEAD_TRIM left the selftest green and made an
#     emphasis-wrapped mention of the operation clean (both named emphasis cases
#     use `*`, so nothing exercised the underscore spelling);
#   · removing `,` from TAIL_TRIM left it green and made a comma-terminated
#     mention clean;
#   · removing the backslash entry from ANSI_C_SIMPLE left it green and made a
#     doubled-backslash form inside a nested shell string clean — the decode
#     reduces the pair to one backslash, which the inner shell then removes to
#     rebuild the operation word.
# These are the LINT's own text model, not command grammar, which is why the
# command-grammar pins above could not see them: the blind spot was upstream of
# every table they cover.
_LEAD_TRIM_FIXTURE = "`*_\"'([{"
_TAIL_TRIM_FIXTURE = "`*_\"'.,;:!?)]}"
# The two the SECOND sweep of this class found (gate round 2c), same shape as the
# three above and both in the under-report direction:
#   · MARKUP_CHARS is the inline-markup alphabet `markup_stripped` removes so a
#     rendered line reads as the command a human sees. Dropping `*` left the
#     whole selftest green — every published count unchanged — while an
#     emphasis-split mention of the operation went clean.
#   · DQ_ESCAPABLE is what a backslash may escape inside a double-quoted region.
#     Dropping the backtick left the selftest green while an escaped-backtick
#     command substitution inside a nested shell string went clean: the outer
#     shell hands the literal backticks to the inner one, which runs them.
_MARKUP_CHARS_FIXTURE = "`*"
_DQ_ESCAPABLE_FIXTURE = "$`\"\\\n"
# The gitlink mode, written out independently of the production constant. Gate
# round 3c: the index probe fabricated its submodule entry with `GITLINK_MODE`
# itself, so the parser's oracle and the parser's input were the same value —
# mutating it to `100755` or `120000` left all cases green, and a tracked SYMLINK
# to a directory was then skipped as a submodule and the gate exited 0. A test
# that fabricates its input from the constant it is checking asserts only that
# the constant equals itself.
_GITLINK_MODE_FIXTURE = "160000"
# The shell control words `_strip_prefix_tokens` steps over. Same class, found in
# the same round: dropping `then` left every case green while a perfectly ordinary
# `if …; then <benign> …; fi` line flipped from clean to a FALSE finding. That is
# the over-report direction, which this lint is deliberately biased toward — but a
# member nothing exercises is unpinned either way, and the next one dropped may
# not be the safe direction.
_CONTROL_WORDS_FIXTURE = {"if", "then", "else", "elif", "fi", "while", "until",
                          "do", "done", "case", "esac", "in", "for", "select",
                          "function", "coproc"}
# The programs whose NAME the walk recognises, so a `<name>:` head is read as a
# command and not as a prose label. Gate round 4c: unpinned, and dropping the VCS
# from it left every case green while `<vcs>: <publish>` flipped finding -> clean
# — the UNDER-report direction, which for this lint means a stale instruction
# ships. Enumerated independently of the union that builds it.
_KNOWN_PROGRAMS_FIXTURE = {"git", "gh", "sh", "bash", "zsh", "ksh", "dash"}
# The publishing operations themselves, and the full prose-exemption union.
# Gate round 5c: BOTH were listed as pinned and neither actually was — adding a
# member to either left every case green while a real form flipped. A ledger that
# says "pinned" about a table nothing pins is worse than one that says "residual",
# because it retires the suspicion that would have found the defect. Assembled
# from fragments like their production counterparts, so this file still contains
# no scanned term verbatim, and derived from NOTHING: an added or removed member
# on either side is a failure.
_VCS_EGRESS_FIXTURE = {j("pu", "sh"), j("send", "-pack")}
_PROSE_EXEMPT_FIXTURE = {
    "", "bash", "builtin", "case", "command", "coproc", "dash", "do", "doas",
    "done", "echo", "elif", "else", "env", "esac", "eval", "exec", "false",
    "fi", "for", "function", "if", "in", "ionice", "ksh", "nice", "nohup",
    "printf", "select", "setsid", "sh", "stdbuf", "sudo", "then", "time",
    "timeout", "true", "until", "while", "xargs", "zsh",
}
_ANSI_C_SIMPLE_FIXTURE = {
    "a": "\a", "b": "\b", "e": "\x1b", "E": "\x1b", "f": "\f", "n": "\n",
    "r": "\r", "t": "\t", "v": "\v", "\\": "\\", "'": "'", '"': '"', "?": "?",
}
# A member with no NAME here generates no case, so the name map is pinned to be
# total over the separator set — otherwise adding a separator would silently add
# a member the corpus never reaches, which is the same defect one step later.
_SEPARATOR_NAMES = {";": "semi", "|": "pipe", "&": "amp", "`": "backtick",
                    "(": "oparen", ")": "cparen", "\n": "newline"}


def _without_member(name: str, member, probe):
    """Run `probe()` with one member removed from the production set `name`.

    The set is restored unconditionally. This is the only oracle that answers
    "does this case actually test THAT member" — textual presence does not.
    """
    g = globals()
    old = g[name]
    g[name] = (old.replace(member, "") if isinstance(old, str)
               else {x for x in old if x != member})
    try:
        return probe()
    finally:
        g[name] = old


def _members_are_load_bearing() -> list[str]:
    """Each explicit case row must change answer when its member is removed.

    A member that does not is reported by a SECOND path, which is legitimate but
    must be declared in `_REDUNDANT_MEMBERS` with the measured reason. Checked in
    both directions, so an exemption that stops being true is itself a failure.
    """
    problems: list[str] = []
    moved: list[tuple[str, str, bool]] = []
    for flag, line in _API_BODY_FLAG_CASES:
        moved.append(("forge API flag", flag, not _without_member(
            "API_BODY_FLAGS", flag, lambda: bool(scan_text(line)))))
    for flag, line in _API_METHOD_FLAG_CASES:
        moved.append(("forge API flag", flag, not _without_member(
            "API_METHOD_FLAGS", flag, lambda: bool(scan_text(line)))))
    for name, line in _EMITTER_CASES:
        # the emitter cases are NEGATIVE: removing the exemption must make the
        # protected mention start reporting.
        moved.append(("text emitter", name, _without_member(
            "NON_EXECUTING", name, lambda: bool(scan_text(line)))))
    for ch, name, line, _want in _SEPARATOR_CASES:
        # END-TO-END only, deliberately: an earlier version also accepted "the
        # quote-naive split loses a part", and gate round 3 #1's second
        # construction walked straight through it — a row declaring `;` while a
        # `|` carried the verdict still lost a naive part, so the row looked
        # load-bearing and was not. The level a row is checked at must be the
        # level its expectation is asserted at.
        moved.append(("command separator", name, _without_member(
            "SEPARATOR_CHARS", ch, lambda: not bool(scan_text(line)))))
    # THREE directions, not two. The loop below only ever visits keys that a row
    # produced, so an exemption naming a member with no row was never looked at
    # — gate round 4 added a ghost key and the whole selftest still passed. An
    # exemption that outlives its row is exactly the drift this table exists to
    # prevent, so the key set must be a subset of the rows.
    ghosts = sorted(set(_REDUNDANT_MEMBERS) - {(f, m) for f, m, _ in moved})
    for family, member in ghosts:
        problems.append("%s %r is exempted as %r but has no case row, so the "
                        "exemption is never checked — drop it"
                        % (family, member, _REDUNDANT_MEMBERS[(family, member)]))
    for family, member, did in moved:
        listed = (family, member) in _REDUNDANT_MEMBERS
        if not did and not listed:
            problems.append("%s %r: removing it from the rule table changes "
                            "nothing about its own case, so the case does not "
                            "test it" % (family, member))
        if did and listed:
            problems.append("%s %r is exempted as %r, but removing it DOES "
                            "change its case — drop the exemption"
                            % (family, member, _REDUNDANT_MEMBERS[(family,
                                                                   member)]))
    return problems


def _tables_are_pinned() -> list[str]:
    """Compare the hand-written enumeration above against the rule tables the
    scanner actually uses, in BOTH directions."""
    problems: list[str] = []
    covered = set(_CARRIER_VALUE_OPTS)
    for name in sorted(covered - WRAPPERS):
        problems.append("carrier %r has fixtures but is not in the rule table"
                        % name)
    for name in sorted(WRAPPERS - covered):
        problems.append("carrier %r is in the rule table but has no fixtures"
                        % name)
    for name in sorted(covered & WRAPPERS):
        want = set(_CARRIER_VALUE_OPTS[name])
        got = set(WRAPPER_SPEC[name]["value"])
        if want != got:
            problems.append(
                "carrier %r takes an operand for %r, fixtures enumerate %r"
                % (name, sorted(got), sorted(want)))
        want_pos = _CARRIER_POSITIONALS.get(name, 0)
        got_pos = WRAPPER_SPEC[name]["positional"]
        if want_pos != got_pos:
            problems.append("carrier %r takes %d positional(s), fixtures "
                            "assume %d" % (name, got_pos, want_pos))
        overlap = sorted(set(_CARRIER_BARE_FLAGS.get(name, ())) & got)
        if overlap:
            problems.append("carrier %r lists %r as operand-taking, but the "
                            "fixtures pin them as bare flags" % (name, overlap))
        want_opt = _CARRIER_OPTIONAL_SHORT_CHARS.get(name, "")
        got_opt = WRAPPER_OPTIONAL_SHORT_CHARS.get(name, "")
        if want_opt != got_opt:
            problems.append("carrier %r takes an OPTIONAL operand for short "
                            "%r, fixtures enumerate %r"
                            % (name, got_opt, want_opt))
        want_chars = _CARRIER_SHORT_VALUE_CHARS.get(name)
        got_chars = WRAPPER_SHORT_VALUE_CHARS.get(name)
        both = sorted(set(got_opt) & set(got_chars or ""))
        if both:
            problems.append("carrier %r reads %r as taking an operand that is "
                            "both mandatory and optional; a letter that is "
                            "mandatory on any platform belongs in the "
                            "mandatory set alone" % (name, both))
        if want_chars is None:
            problems.append("carrier %r has no hand-written short-option "
                            "letter set" % name)
        elif want_chars != got_chars:
            problems.append("carrier %r clusters short operand-taking letters "
                            "%r, fixtures enumerate %r"
                            % (name, got_chars, want_chars))
        bare_chars = {f[1] for f in _CARRIER_BARE_FLAGS.get(name, ())
                      if len(f) == 2 and f[0] == "-" and f[1] != "-"}
        clash = sorted(bare_chars & set(got_chars or ""))
        if clash:
            problems.append("carrier %r reads %r as operand-taking inside a "
                            "cluster, but the fixtures pin them as bare flags"
                            % (name, clash))
        # The cluster fixtures are only worth anything if their prefix letter
        # really takes no operand — otherwise it swallows the letter under test
        # and the case passes without exercising the cluster at all.
        if name not in _CARRIER_CLUSTER_PREFIX:
            problems.append("carrier %r has no cluster-prefix entry, so its "
                            "short options are never tested in cluster form"
                            % name)
            continue
        prefix = _CARRIER_CLUSTER_PREFIX[name]
        shorts = [o for o in _CARRIER_VALUE_OPTS[name]
                  if len(o) == 2 and o[0] == "-" and o[1] != "-"]
        if prefix and prefix in (got_chars or ""):
            problems.append("carrier %r uses %r as a cluster prefix but reads "
                            "it as operand-taking" % (name, prefix))
        elif not prefix and shorts and name not in ("nice", "stdbuf"):
            # nice has only -n and every short stdbuf option takes an operand,
            # so neither tool HAS a no-operand short flag to cluster behind.
            problems.append("carrier %r has short operand-taking options %r "
                            "but no cluster prefix to test them with"
                            % (name, shorts))
    if set(_VCS_TERMINAL_OPTS) != VCS_TERMINAL_OPTS:
        problems.append("the VCS terminal globals are %r, fixtures enumerate %r"
                        % (sorted(VCS_TERMINAL_OPTS),
                           sorted(_VCS_TERMINAL_OPTS)))
    overlap = sorted(set(_VCS_TERMINAL_OPTS) & VCS_VALUE_OPTS)
    if overlap:
        problems.append("the VCS globals %r both consume an operand and "
                        "terminate; a terminal option consumes nothing because "
                        "nothing runs after it" % overlap)
    for opt in _VCS_ATTACHED_ONLY_OPTS:
        if opt in VCS_VALUE_OPTS:
            problems.append("VCS option %r takes an ATTACHED operand only, but "
                            "the rule table consumes the following token — a "
                            "bare one would swallow the subcommand" % opt)
    for label, want, got in (
            ("value", _EXPANSION_VALUE_OPS, EXPANSION_VALUE_OPS),
            ("replacement", _EXPANSION_REPLACE_OPS, EXPANSION_REPLACE_OPS),
            ("non-value", _EXPANSION_NON_VALUE_OPS, EXPANSION_NON_VALUE_OPS)):
        if list(got) != want:
            problems.append("the %s expansion operators are %r, fixtures "
                            "enumerate %r" % (label, list(got), want))
    classes = [set(_EXPANSION_VALUE_OPS), set(_EXPANSION_REPLACE_OPS),
               set(_EXPANSION_NON_VALUE_OPS)]
    for a in range(len(classes)):
        for b in range(a + 1, len(classes)):
            shared = sorted(classes[a] & classes[b])
            if shared:
                problems.append("the expansion operators %r are in two classes "
                                "at once" % shared)
    if _VCS_ALIAS_SHELL_PREFIX != VCS_ALIAS_SHELL_PREFIX:
        problems.append("the alias shell marker is %r, fixtures enumerate %r"
                        % (VCS_ALIAS_SHELL_PREFIX, _VCS_ALIAS_SHELL_PREFIX))
    if _VCS_ALIAS_MAX_HOPS != VCS_ALIAS_MAX_HOPS:
        problems.append("the alias hop bound is %d, fixtures enumerate %d"
                        % (VCS_ALIAS_MAX_HOPS, _VCS_ALIAS_MAX_HOPS))
    if set(_FORGE_PR_MUTATIONS) != PR_MUTATIONS:
        problems.append("the forge PR mutating actions are %r, fixtures "
                        "enumerate %r" % (sorted(PR_MUTATIONS),
                                          sorted(_FORGE_PR_MUTATIONS)))
    overlap = sorted(set(_FORGE_PR_NON_MUTATIONS) & PR_MUTATIONS)
    if overlap:
        problems.append("the forge PR actions %r are refused, but the fixtures "
                        "pin them as non-publishing" % overlap)
    if set(_FORGE_FAMILIES) != set(FORGE_FAMILY_RULES):
        problems.append("the forge non-PR families are %r, fixtures enumerate "
                        "%r" % (sorted(FORGE_FAMILY_RULES),
                                sorted(_FORGE_FAMILIES)))
    _cond_word = {None: "always",
                  FORGE_COND_PUSH_FLAG: "push-flag",
                  FORGE_COND_DESTINATION: "positional-destination"}
    for family in sorted(set(_FORGE_FAMILIES) & set(FORGE_FAMILY_RULES)):
        if set(_FORGE_FAMILIES[family]) != set(FORGE_FAMILY_RULES[family]):
            problems.append("forge family %r refuses the actions %r, fixtures "
                            "enumerate %r"
                            % (family, sorted(FORGE_FAMILY_RULES[family]),
                               sorted(_FORGE_FAMILIES[family])))
        for action, cond in sorted(FORGE_FAMILY_RULES[family].items(),
                                   key=lambda kv: kv[0]):
            if cond not in _cond_word:
                problems.append("forge family %r reads action %r with the "
                                "unknown condition %r" % (family, action, cond))
                continue
            want = _FORGE_FAMILIES[family].get(action)
            if want != _cond_word[cond]:
                problems.append("forge family %r publishes on %r when %r, "
                                "fixtures enumerate %r"
                                % (family, action, _cond_word[cond], want))
        banned = sorted(set(_FORGE_FAMILY_EXCLUDED.get(family, ()))
                        & set(FORGE_FAMILY_RULES[family]))
        if banned:
            problems.append("forge family %r refuses %r, but the fixtures pin "
                            "them as non-publishing" % (family, banned))
    if REPO_CREATE_PUSH_FLAGS != {FORGE_COND_PUSH_FLAG}:
        problems.append("the publishing flag of the repository family's create "
                        "action is %r, the condition names %r"
                        % (sorted(REPO_CREATE_PUSH_FLAGS),
                           FORGE_COND_PUSH_FLAG))
    if set(_VCS_PAIRS) != VCS_EGRESS_PAIRS:
        problems.append("the VCS two-word publishing pairs are %r, fixtures "
                        "enumerate %r" % (sorted(VCS_EGRESS_PAIRS),
                                          sorted(set(_VCS_PAIRS))))
    for family, ops in sorted(_VCS_PAIR_EXCLUDED.items()):
        refused = {op for f, op in VCS_EGRESS_PAIRS if f == family}
        banned = sorted(set(ops) & refused)
        if banned:
            problems.append("VCS family %r refuses %r, but the fixtures pin "
                            "them as non-publishing" % (family, banned))
    if _PFLAG_FALSE != PFLAG_FALSE:
        problems.append("the boolean flag's false spellings are %r, fixtures "
                        "enumerate %r" % (sorted(PFLAG_FALSE),
                                          sorted(_PFLAG_FALSE)))
    if {f for f, _op in _VCS_PAIRS} != VCS_PAIR_FAMILIES:
        problems.append("the VCS two-word families are %r, fixtures enumerate "
                        "%r" % (sorted(VCS_PAIR_FAMILIES),
                                sorted({f for f, _op in _VCS_PAIRS})))
    if set(_VCS_PAIR_OPTS) != set(VCS_PAIR_VALUE_OPTS):
        problems.append("the VCS families with an option table are %r, fixtures "
                        "enumerate %r" % (sorted(VCS_PAIR_VALUE_OPTS),
                                          sorted(_VCS_PAIR_OPTS)))
    for family in sorted(set(_VCS_PAIR_OPTS) & set(VCS_PAIR_VALUE_OPTS)):
        if set(_VCS_PAIR_OPTS[family]) != VCS_PAIR_VALUE_OPTS[family]:
            problems.append("VCS family %r takes a separate operand for %r, "
                            "fixtures enumerate %r"
                            % (family, sorted(VCS_PAIR_VALUE_OPTS[family]),
                               sorted(_VCS_PAIR_OPTS[family])))
        attached = _VCS_PAIR_ATTACHED_ONLY_OPTS.get(family, ())
        overlap = sorted(set(attached) & VCS_PAIR_VALUE_OPTS[family])
        if overlap:
            problems.append("VCS family %r reads %r as taking a separate "
                            "operand, but the fixtures pin them as attached-only"
                            % (family, overlap))
    if set(_VCS_GLOBAL_VALUE_OPTS) != VCS_VALUE_OPTS:
        problems.append("VCS global operand-taking options are %r, fixtures "
                        "enumerate %r" % (sorted(VCS_VALUE_OPTS),
                                          sorted(_VCS_GLOBAL_VALUE_OPTS)))
    if set(_FORGE_GLOBAL_VALUE_OPTS) != FORGE_VALUE_OPTS:
        problems.append("forge global operand-taking options are %r, fixtures "
                        "enumerate %r" % (sorted(FORGE_VALUE_OPTS),
                                          sorted(_FORGE_GLOBAL_VALUE_OPTS)))
    if set(_FORGE_ACTION_VALUE_OPTS) != set(FORGE_ACTION_VALUE_OPTS):
        problems.append("forge actions with their own operand-taking options "
                        "are %r, fixtures enumerate %r"
                        % (sorted(FORGE_ACTION_VALUE_OPTS),
                           sorted(_FORGE_ACTION_VALUE_OPTS)))
    for key in sorted(set(_FORGE_ACTION_VALUE_OPTS)
                      & set(FORGE_ACTION_VALUE_OPTS)):
        if set(_FORGE_ACTION_VALUE_OPTS[key]) != FORGE_ACTION_VALUE_OPTS[key]:
            problems.append(
                "forge action %r takes an operand for %r, fixtures enumerate %r"
                % (key, sorted(FORGE_ACTION_VALUE_OPTS[key]),
                   sorted(_FORGE_ACTION_VALUE_OPTS[key])))
        if _FORGE_ACTION_SHORT_CHARS.get(key) \
                != FORGE_ACTION_SHORT_VALUE_CHARS.get(key):
            problems.append(
                "forge action %r short operand-taking letters are %r, fixtures "
                "enumerate %r" % (key, FORGE_ACTION_SHORT_VALUE_CHARS.get(key),
                                  _FORGE_ACTION_SHORT_CHARS.get(key)))
    # every action named here must be one the family rules actually refuse —
    # an entry for an action outside the table would model nothing
    for family, action in sorted(_FORGE_ACTION_VALUE_OPTS):
        if action not in FORGE_FAMILY_RULES.get(family, {}):
            problems.append("forge action %r has option fixtures but the "
                            "family rules do not refuse it" % ((family,
                                                                action),))
    if _FORGE_GLOBAL_SHORT_CHARS != FORGE_SHORT_VALUE_CHARS:
        problems.append("forge global short operand-taking letters are %r, "
                        "fixtures enumerate %r" % (FORGE_SHORT_VALUE_CHARS,
                                                   _FORGE_GLOBAL_SHORT_CHARS))
    if _FORGE_API_SHORT_CHARS != API_SHORT_VALUE_CHARS:
        problems.append("forge API short operand-taking letters are %r, "
                        "fixtures enumerate %r" % (API_SHORT_VALUE_CHARS,
                                                   _FORGE_API_SHORT_CHARS))
    if set(_SHELL_NAME_MODELS) != SHELLS:
        problems.append("the shell names are %r, fixtures enumerate %r"
                        % (sorted(SHELLS), sorted(_SHELL_NAME_MODELS)))
    for name in sorted(set(_SHELL_NAME_MODELS) & SHELLS):
        if list(SHELL_MODELS[name]) != _SHELL_NAME_MODELS[name]:
            problems.append("shell %r is read under models %r, fixtures "
                            "enumerate %r" % (name, list(SHELL_MODELS[name]),
                                              _SHELL_NAME_MODELS[name]))
    if set(_SHELL_LETTER_ARITY) != set(SHELL_OPTION_ARITY):
        problems.append("the shell arity models are %r, fixtures enumerate %r"
                        % (sorted(SHELL_OPTION_ARITY),
                           sorted(_SHELL_LETTER_ARITY)))
    if set(_SHELL_LONG_VALUE_OPTS) != set(SHELL_LONG_VALUE_OPTS):
        problems.append("the shell long-option models are %r, fixtures "
                        "enumerate %r" % (sorted(SHELL_LONG_VALUE_OPTS),
                                          sorted(_SHELL_LONG_VALUE_OPTS)))
    if set(_SHELL_PLUS_DASH) != set(SHELL_PLUS_DASH):
        problems.append("the shell plus-dash models are %r, fixtures enumerate "
                        "%r" % (sorted(SHELL_PLUS_DASH),
                                sorted(_SHELL_PLUS_DASH)))
    for model in sorted(set(_SHELL_PLUS_DASH) & set(SHELL_PLUS_DASH)):
        if _SHELL_PLUS_DASH[model] != SHELL_PLUS_DASH[model]:
            problems.append("shell %r reads a `+` token containing a dash as "
                            "%r, fixtures enumerate %r"
                            % (model, SHELL_PLUS_DASH[model],
                               _SHELL_PLUS_DASH[model]))
        if SHELL_PLUS_DASH[model] not in (SHELL_PLUSDASH_REJECT,
                                          SHELL_PLUSDASH_BARE_ENDS_OPTIONS,
                                          SHELL_PLUSDASH_PARSE_THROUGH):
            problems.append("shell %r reads a dashed `+` token with the unknown "
                            "action %r" % (model, SHELL_PLUS_DASH[model]))
    if set(_SHELL_BARE_PLUS) != set(SHELL_BARE_PLUS):
        problems.append("the shell bare-`+` models are %r, fixtures enumerate "
                        "%r" % (sorted(SHELL_BARE_PLUS),
                                sorted(_SHELL_BARE_PLUS)))
    for model in sorted(set(_SHELL_BARE_PLUS) & set(SHELL_BARE_PLUS)):
        if _SHELL_BARE_PLUS[model] != SHELL_BARE_PLUS[model]:
            problems.append("shell %r reads a bare `+` as %r, fixtures "
                            "enumerate %r" % (model, SHELL_BARE_PLUS[model],
                                              _SHELL_BARE_PLUS[model]))
        if SHELL_BARE_PLUS[model] not in (SHELL_PLUS_SKIP,
                                          SHELL_PLUS_ENDS_OPTIONS):
            problems.append("shell %r reads a bare `+` with the unknown action "
                            "%r" % (model, SHELL_BARE_PLUS[model]))
    if set(_SHELL_FIRST_OPERAND) != set(SHELL_FIRST_OPERAND):
        problems.append("the shell first-operand models are %r, fixtures "
                        "enumerate %r" % (sorted(SHELL_FIRST_OPERAND),
                                          sorted(_SHELL_FIRST_OPERAND)))
    for model in sorted(set(_SHELL_FIRST_OPERAND) & set(SHELL_FIRST_OPERAND)):
        if _SHELL_FIRST_OPERAND[model] != SHELL_FIRST_OPERAND[model]:
            problems.append("shell %r reads its first operand with no `-c` as "
                            "%r, fixtures enumerate %r"
                            % (model, SHELL_FIRST_OPERAND[model],
                               _SHELL_FIRST_OPERAND[model]))
        if SHELL_FIRST_OPERAND[model] not in (SHELL_FIRST_OPERAND_FILE,
                                              SHELL_FIRST_OPERAND_COMMAND):
            problems.append("shell %r reads its first operand with the unknown "
                            "action %r" % (model, SHELL_FIRST_OPERAND[model]))
    for model in sorted(set(_SHELL_LETTER_ARITY) & set(SHELL_OPTION_ARITY)):
        if _SHELL_LETTER_ARITY[model] != SHELL_OPTION_ARITY[model]:
            problems.append("shell %r reads its option letters as %r, fixtures "
                            "enumerate %r" % (model, SHELL_OPTION_ARITY[model],
                                              _SHELL_LETTER_ARITY[model]))
        if SHELL_COMMAND_CHAR in SHELL_OPTION_ARITY[model]:
            problems.append("shell %r models the command flag %r as taking an "
                            "operand; it does not — the script is the first "
                            "remaining OPERAND" % (model, SHELL_COMMAND_CHAR))
        for ch, kind in sorted(SHELL_OPTION_ARITY[model].items()):
            if kind not in (SHELL_NEXT, SHELL_ATTACHED_OR_NEXT,
                            SHELL_ATTACHED_OR_NEXT_NONOPT):
                problems.append("shell %r reads %r with the unknown arity %r"
                                % (model, ch, kind))
    for model in sorted(set(_SHELL_LONG_VALUE_OPTS)
                        & set(SHELL_LONG_VALUE_OPTS)):
        if set(_SHELL_LONG_VALUE_OPTS[model]) != SHELL_LONG_VALUE_OPTS[model]:
            problems.append("shell %r takes a separate operand for the long "
                            "options %r, fixtures enumerate %r"
                            % (model, sorted(SHELL_LONG_VALUE_OPTS[model]),
                               sorted(_SHELL_LONG_VALUE_OPTS[model])))
    # Every model a NAME is read under has to exist in both tables, or the walk
    # would raise (or silently skip a shell) instead of parsing it.
    for name, models in sorted(SHELL_MODELS.items()):
        for model in models:
            if model not in SHELL_OPTION_ARITY:
                problems.append("shell %r is read under model %r, which has no "
                                "letter map" % (name, model))
            if model not in SHELL_LONG_VALUE_OPTS:
                problems.append("shell %r is read under model %r, which has no "
                                "long-option map" % (name, model))
            if model not in SHELL_BARE_PLUS:
                problems.append("shell %r is read under model %r, which has no "
                                "bare-`+` rule" % (name, model))
            if model not in SHELL_PLUS_DASH:
                problems.append("shell %r is read under model %r, which has no "
                                "dashed-`+` rule" % (name, model))
            if model not in SHELL_FIRST_OPERAND:
                problems.append("shell %r is read under model %r, which has no "
                                "first-operand rule" % (name, model))
    # Every mutation flag the API rule reports must be reachable through the
    # cluster walk too, or a clustered spelling of it is a silent miss.
    for flag in sorted(API_BODY_FLAGS | API_METHOD_FLAGS):
        if len(flag) == 2 and flag[0] == "-" and flag[1] not in API_SHORT_VALUE_CHARS:
            problems.append("forge API mutation flag %r is short but is not in "
                            "the clustered-letter set, so %r hides it"
                            % (flag, "-i" + flag[1]))
    # The string-exec carriers, both directions.
    if set(_STRING_EXEC_CARRIERS) != STRING_EXEC_CARRIERS:
        problems.append("string-exec carriers are %r, fixtures enumerate %r"
                        % (sorted(STRING_EXEC_CARRIERS),
                           sorted(_STRING_EXEC_CARRIERS)))
    if set(_SSH_CMD_KEYWORDS) != SSH_CMD_KEYWORDS:
        problems.append("command-bearing ssh keywords are %r, fixtures "
                        "enumerate %r" % (sorted(SSH_CMD_KEYWORDS),
                                          sorted(_SSH_CMD_KEYWORDS)))
    if set(_SSH_SEPARATOR_WS) != set(SSH_SEPARATOR_WS):
        problems.append("ssh separator whitespace is %r, fixtures enumerate %r"
                        % (sorted(SSH_SEPARATOR_WS), sorted(_SSH_SEPARATOR_WS)))
    # The three sets the FINAL integration gate caught unpinned, all consumed at a
    # site no case reached. Both directions, as above.
    if set(_SSH_VALUE_CHARS_FIXTURE) != set(_SSH_VALUE_CHARS):
        problems.append("ssh operand-taking option letters are %r, fixtures "
                        "enumerate %r" % (sorted(set(_SSH_VALUE_CHARS)),
                                          sorted(set(_SSH_VALUE_CHARS_FIXTURE))))
    for label, fixture, table in (("lead trim", _LEAD_TRIM_FIXTURE, LEAD_TRIM),
                                  ("tail trim", _TAIL_TRIM_FIXTURE, TAIL_TRIM)):
        if set(fixture) != set(table):
            problems.append("%s characters are %r, fixtures enumerate %r"
                            % (label, sorted(set(table)), sorted(set(fixture))))
    if _ANSI_C_SIMPLE_FIXTURE != ANSI_C_SIMPLE:
        problems.append("the ANSI-C simple escapes are %r, fixtures enumerate %r"
                        % (sorted(ANSI_C_SIMPLE.items()),
                           sorted(_ANSI_C_SIMPLE_FIXTURE.items())))
    # A pin proves the member is DECLARED; these prove it is CONSUMED. Textual
    # presence is not consumption — the whole reason the three above went unseen
    # is that they were declared, read, and never exercised at the reading site.
    for ch in sorted(set(_LEAD_TRIM_FIXTURE)):
        if trim_token(ch + VCS) != VCS:
            problems.append("lead-trim member %r is declared but trim_token does "
                            "not strip it (%r stayed %r)"
                            % (ch, ch + VCS, trim_token(ch + VCS)))
    for ch in sorted(set(_TAIL_TRIM_FIXTURE)):
        if trim_token(VCS + ch) != VCS:
            problems.append("tail-trim member %r is declared but trim_token does "
                            "not strip it (%r stayed %r)"
                            % (ch, VCS + ch, trim_token(VCS + ch)))
    for key, value in sorted(_ANSI_C_SIMPLE_FIXTURE.items()):
        if _ansi_c_decode("\\" + key) != value:
            problems.append("ANSI-C escape %r is declared as %r but decodes to %r"
                            % ("\\" + key, value, _ansi_c_decode("\\" + key)))
    for label, fixture, table in (
            ("inline markup", _MARKUP_CHARS_FIXTURE, MARKUP_CHARS),
            ("double-quote escapable", _DQ_ESCAPABLE_FIXTURE, DQ_ESCAPABLE)):
        if set(fixture) != set(table):
            problems.append("%s characters are %r, fixtures enumerate %r"
                            % (label, sorted(set(table)), sorted(set(fixture))))
    if _GITLINK_MODE_FIXTURE != GITLINK_MODE:
        problems.append("the gitlink mode is %r, the fixture enumerates %r"
                        % (GITLINK_MODE, _GITLINK_MODE_FIXTURE))
    if _CONTROL_WORDS_FIXTURE != CONTROL_WORDS:
        problems.append("the shell control words are %r, fixtures enumerate %r"
                        % (sorted(CONTROL_WORDS), sorted(_CONTROL_WORDS_FIXTURE)))
    for word in sorted(_CONTROL_WORDS_FIXTURE):
        # The word must be STEPPED OVER, so the token AFTER it is what gets read
        # as the command. If it is not, the control word itself becomes the head,
        # the segment is treated as prose, and an ordinary shell line built on it
        # is reported. `_NON_EXECUTING[0]` is a benign program that is itself in a
        # pinned set, so this case cannot pass by naming something arbitrary.
        stripped = _strip_prefix_tokens([word, _NON_EXECUTING[0], "hello"], [])
        if stripped[:1] != [_NON_EXECUTING[0]]:
            problems.append("control word %r is declared but _strip_prefix_tokens "
                            "does not step over it (%r stayed %r), so the token "
                            "after it is never read as the command"
                            % (word, [word, _NON_EXECUTING[0], "hello"], stripped))
    if _VCS_EGRESS_FIXTURE != VCS_EGRESS:
        problems.append("the publishing operations are %r, fixtures enumerate %r"
                        % (sorted(VCS_EGRESS), sorted(_VCS_EGRESS_FIXTURE)))
    if _PROSE_EXEMPT_FIXTURE != PROSE_EXEMPT:
        problems.append("the prose-exemption set is %r, fixtures enumerate %r"
                        % (sorted(PROSE_EXEMPT), sorted(_PROSE_EXEMPT_FIXTURE)))
    if _KNOWN_PROGRAMS_FIXTURE != KNOWN_PROGRAMS:
        problems.append("the known programs are %r, fixtures enumerate %r"
                        % (sorted(KNOWN_PROGRAMS), sorted(_KNOWN_PROGRAMS_FIXTURE)))
    for prog in sorted(_KNOWN_PROGRAMS_FIXTURE):
        # A KNOWN program's name followed by a colon is a command, not a prose
        # label. Drop it from the set and the whole segment is skipped as a label.
        if not scan_text("%s: %s" % (prog, PUBLISH)) and prog == VCS:
            problems.append("known program %r is declared but %r reports nothing "
                            "— its colon-head form is being read as a prose label"
                            % (prog, "%s: %s" % (prog, PUBLISH)))
    # PROSE_EXEMPT is a UNION, so its components are pinned individually above;
    # what was NOT checked is that each component actually reaches THIS union.
    # Gate round 4c: removing one text emitter from the union alone left every
    # case green while `<emitter> <vcs> <publish>` flipped clean -> finding.
    for word in sorted(set(_NON_EXECUTING) | set(_CONTROL_WORDS_FIXTURE)):
        if word not in PROSE_EXEMPT:
            problems.append("%r is a pinned non-executing/control word but is not "
                            "in PROSE_EXEMPT, so a line headed by it is reported "
                            "as a finding" % word)
    for ch in sorted(set(_MARKUP_CHARS_FIXTURE)):
        # Split the operation word with the marker, the way rendered emphasis or
        # a code span does; stripping it must put the word back together.
        split = VCS[:1] + ch + VCS[1:] + " " + PUBLISH[:2] + ch + PUBLISH[2:]
        if markup_stripped(split) != VCS + " " + PUBLISH:
            problems.append("inline-markup member %r is declared but "
                            "markup_stripped does not remove it (%r became %r)"
                            % (ch, split, markup_stripped(split)))
    for ch in sorted(set(_DQ_ESCAPABLE_FIXTURE)):
        # Inside a double-quoted region a backslash before this character must
        # contribute the CHARACTER, not the backslash-pair.
        if _quote_value("\\" + ch, '"') != ch:
            problems.append("double-quote escapable member %r is declared but "
                            "_quote_value keeps the backslash (%r became %r)"
                            % (ch, "\\" + ch, _quote_value("\\" + ch, '"')))
    # Every operand-taking ssh letter must actually consume its separate operand:
    # if it does not, the operand is read as the destination and the option walk
    # stops before any command-bearing option that follows it.
    # Both directions, because the exception is as load-bearing as the rule: an
    # operand-taking letter that is ALSO terminal (ssh's query option) ends the
    # invocation, so nothing after it ever runs and reporting it would be a false
    # finding. Asserting only the first half would let the terminal model be
    # deleted unnoticed; asserting only the second would let the operand walk be.
    _ssh_terminal = {opt[1:] for opt in _STRING_EXEC_TERMINAL["ssh"]
                     if len(opt) == 2 and opt.startswith("-")}
    for ch in sorted(set(_SSH_VALUE_CHARS_FIXTURE)):
        line = ("ssh -%s operand -o '%s=%s %s' host"
                % (ch, _SSH_CMD_KEYWORDS[0], VCS, PUBLISH))
        reported = bool(scan_text(line))
        if ch in _ssh_terminal:
            if reported:
                problems.append("ssh option letter %r is terminal — the "
                                "invocation exits before the command-bearing "
                                "option is reached — yet %r reports a finding"
                                % (ch, line))
        elif not reported:
            problems.append("ssh option letter %r is in the operand-taking set "
                            "but its separate operand is not consumed — the "
                            "command-bearing option after it is never reached "
                            "(%r reports nothing)" % (ch, line))
    # The four sets the merge gate caught unpinned. Both directions, so neither
    # a widened production set nor a widened fixture list passes unnoticed.
    for label, fixture, table in (
            ("forge API body flags", _API_BODY_FLAGS, API_BODY_FLAGS),
            ("forge API method flags", _API_METHOD_FLAGS, API_METHOD_FLAGS),
            ("command separators", _SEPARATOR_CHARS, set(SEPARATOR_CHARS)),
            ("non-executing text emitters", _NON_EXECUTING, NON_EXECUTING)):
        if set(fixture) != set(table):
            problems.append("%s are %r, fixtures enumerate %r"
                            % (label, sorted(table), sorted(fixture)))
    unnamed = [ch for ch in SEPARATOR_CHARS if ch not in _SEPARATOR_NAMES]
    if unnamed:
        problems.append("separator(s) %r have no fixture NAME, so no case is "
                        "generated for them" % unnamed)
    # THIRD place, and the one that survives the other two being narrowed
    # together: the explicit case rows. A member with no row is a member no case
    # reaches, whatever the two lists above agree on.
    for label, covered, table in (
            ("forge API body flag",
             {f for f, _ in _API_BODY_FLAG_CASES}, API_BODY_FLAGS),
            ("forge API method flag",
             {f for f, _ in _API_METHOD_FLAG_CASES}, API_METHOD_FLAGS),
            ("command separator",
             {c for c, _, _, _ in _SEPARATOR_CASES}, set(SEPARATOR_CHARS)),
            ("non-executing text emitter",
             {n for n, _ in _EMITTER_CASES}, NON_EXECUTING)):
        if covered != set(table):
            problems.append("%s cases cover %r, the rule table holds %r"
                            % (label, sorted(covered), sorted(table)))
    # And every separator at the SPLIT SITE ITSELF, quote-naive — the pass that
    # actually reads the set. A whole-line case discriminates five of the seven
    # members; the backtick is lifted by the quote-AWARE substitution branch
    # before the separator test ever sees it, so the aware pass reports the line
    # either way. MEASURED: with the backtick removed from the split test, every
    # end-to-end case stayed green and only this assertion objects.
    for ch, name, _line, _want in _SEPARATOR_CASES:
        naive = split_commands("echo x %s %s %s" % (ch, _V, _P), False)
        if len(naive) < 2:
            problems.append("separator %s (%r) does not split the quote-naive "
                            "pass — it produced %r" % (name, ch, naive))
    # Each explicit row DECLARES a member; nothing so far made the row's command
    # actually contain it. Without this, a row could be labelled with one member
    # and exercise another, and every check above — coverage, cardinality,
    # uniqueness, the behavioural expectation — would still pass while the
    # declared member went unexercised. Gate round 2 #1.
    for flag, line in _API_BODY_FLAG_CASES + _API_METHOD_FLAG_CASES:
        if flag not in line.split():
            problems.append("the case row declaring forge API flag %r does not "
                            "contain it as a token: %r" % (flag, line))
    for name, line in _EMITTER_CASES:
        if line.split()[:1] != [name]:
            problems.append("the case row declaring text emitter %r does not "
                            "invoke it: %r" % (name, line))
    # …and the binding that textual presence CANNOT give: take the declared
    # member away and the case's answer must move. Gate round 3 #1 built three
    # rows that named one member and exercised another — a declared flag sitting
    # as another option's operand, a declared separator quoted while a different
    # one did the splitting, a protected mention under a later emitter — and
    # every textual check above passed on all three. Only removal answers it.
    problems += _members_are_load_bearing()
    # Every member, at EVERY position the code consumes one: before the
    # keyword, and between the keyword and its value. A set proved present at
    # one site and absent at the other is gate round 9 #3.
    if set(_WS_NAMES) != set(_SSH_SEPARATOR_WS):
        problems.append("whitespace NAMES cover %r, the fixture oracle is %r"
                        % (sorted(_WS_NAMES), sorted(_SSH_SEPARATOR_WS)))
    for label, generated in (
            ("separator", {sep for _n, sep, _a in _SSH_SEPARATORS}),
            ("leading", {pre for _n, pre in _SSH_KEYWORD_PREFIXES})):
        for ws in sorted(_SSH_SEPARATOR_WS):
            if not any(ws in spelling for spelling in generated):
                problems.append("ssh whitespace %r is in the rule table but no "
                                "generated %s case spells it" % (ws, label))
    for name in sorted(set(_STRING_EXEC_CARRIERS) & STRING_EXEC_CARRIERS):
        spec = STRING_EXEC_SPEC[name]
        if set(_STRING_EXEC_CMD_OPTS[name]) != set(spec["cmd_opts"]):
            problems.append("carrier %r carries a command on %r, fixtures "
                            "enumerate %r"
                            % (name, sorted(spec["cmd_opts"]),
                               sorted(_STRING_EXEC_CMD_OPTS[name])))
        if set(_STRING_EXEC_TERMINAL[name]) != set(spec["terminal"]):
            problems.append("carrier %r exits on %r, fixtures enumerate %r"
                            % (name, sorted(spec["terminal"]),
                               sorted(_STRING_EXEC_TERMINAL[name])))
        both = sorted(set(spec["terminal"]) & set(spec["cmd_opts"]))
        if both:
            problems.append("carrier %r reads %r as both terminal and "
                            "command-bearing" % (name, both))
        if _STRING_EXEC_DESTINATIONS[name] != spec["destinations"]:
            problems.append("carrier %r ends its options after %r operand(s), "
                            "fixtures assume %r"
                            % (name, spec["destinations"],
                               _STRING_EXEC_DESTINATIONS[name]))
        # A command-bearing SHORT option that is not in the carrier's own
        # operand-taking letters can never be reached through the cluster walk,
        # so the whole row would be dead.
        for opt in sorted(spec["cmd_opts"]):
            if len(opt) == 2 and opt[0] == "-" \
                    and opt[1] not in spec["value_chars"]:
                problems.append("carrier %r carries a command on %r, which is "
                                "not one of its operand-taking letters %r"
                                % (name, opt, spec["value_chars"]))
    return problems


def _ansi_c(word: str, escape: str = "x") -> str:
    """`word` spelled as an ANSI-C quoted region with its FIRST character
    written as an escape.

    Computed, never written out: this file must contain no scannable form
    verbatim (the check-denylist.py idiom), and now that the scanner DECODES
    `$'…'` a literal `$'\\x67it'` beside a literal publish spelling is a
    scannable form — the gate found exactly that in its own fixture list on the
    first run after the decode landed. Building the escape from `ord()` keeps
    the fixtures honest without exempting this file from its own scan."""
    code = ord(word[0])
    body = {"x": "\\x%02x", "o": "\\%o", "u": "\\u%04x", "U": "\\U%08x"}[escape] % code
    return j("$'", body, word[1:], "'")


def _alias_chain(n: int, tail: str) -> list[str]:
    """`n` chained inline alias definitions, the last expanding to `tail`,
    followed by the first alias NAME as the subcommand."""
    argv: list[str] = []
    for k in range(1, n + 1):
        value = tail if k == n else "a%d" % (k + 1)
        argv += ["-c", "%sa%d=%s" % (_AP, k, value)]
    return argv + ["a1"]


def _nest(depth: int) -> str:
    """`sh -c` nested `depth` levels around the bare publishing command."""
    inner = "%s %s" % (_V, _P)
    for _ in range(depth):
        escaped = inner.replace("\\", "\\\\").replace('"', '\\"')
        inner = 'sh -c "%s"' % escaped
    return inner


def _positive_cases() -> list[tuple[str, list[str], int]]:
    """(name, fixture lines, expected first-report line number)."""
    return [
        ("bare", ["%s %s" % (_V, _P)], 1),
        ("dash-C", ["%s -C /x %s" % (_V, _P)], 1),
        ("dash-c-config", ["%s -c a=b %s" % (_V, _P)], 1),
        ("git-dir", ["%s --%s-dir=/x/.%s %s origin main" % (_V, _V, _V, _P)], 1),
        ("absolute-path", ["/usr/bin/%s %s" % (_V, _P)], 1),
        ("command-wrapper", ["command %s %s" % (_V, _P)], 1),
        ("env-assignment", ["env A=1 %s %s" % (_V, _P)], 1),
        ("pack-plumbing", ["%s %s host:repo" % (_V, _K)], 1),
        ("forge-merge", ["%s %s merge 1" % (_G, _R)], 1),
        ("forge-create", ["%s %s create" % (_G, _R)], 1),
        ("forge-ready", ["%s %s ready 1" % (_G, _R)], 1),
        ("forge-close", ["%s %s close 1" % (_G, _R)], 1),
        ("forge-edit", ["%s %s edit 1 --base main" % (_G, _R)], 1),
        ("api-method", ["%s %s -X PUT repos/o/r/pulls/1/merge" % (_G, _A)], 1),
        ("api-body", ["%s %s -f state=closed repos/o/r/pulls/1" % (_G, _A)], 1),
        # attached short-option operands
        ("api-method-attached", ["%s %s -XPOST repos/o/r/pulls" % (_G, _A)], 1),
        ("api-body-attached-f", ["%s %s -fstate=closed repos/o/r/x" % (_G, _A)], 1),
        ("api-body-attached-F", ["%s %s -Ffile=@x repos/o/r/x" % (_G, _A)], 1),
        ("api-method-equals", ["%s %s --method=DELETE repos/o/r/x" % (_G, _A)], 1),
        ("api-input", ["%s %s --input body.json repos/o/r/x" % (_G, _A)], 1),
        # …and the mutation flag may sit behind a no-operand letter in a
        # CLUSTER. Observed on forge CLI 2.96: each of these issues a POST.
        ("api-method-clustered",
         ["%s %s -iX POST repos/o/r/pulls" % (_G, _A)], 1),
        ("api-method-clustered-attached",
         ["%s %s -iXPOST repos/o/r/pulls" % (_G, _A)], 1),
        ("api-body-clustered-F",
         ["%s %s -iF state=closed repos/o/r/x" % (_G, _A)], 1),
        ("api-body-clustered-attached-f",
         ["%s %s -ifstate=closed repos/o/r/x" % (_G, _A)], 1),
        ("shell-c", ["sh -c '%s %s'" % (_V, _P)], 1),
        ("shell-lc", ['bash -lc "cd x && %s %s origin main"' % (_V, _P)], 1),
        ("shell-nested", ["bash -c \"sh -c '%s %s'\"" % (_V, _P)], 1),
        ("shell-nested-deep", [_nest(12)], 1),
        # command substitution stays live inside double quotes
        ("substitution-in-dquotes", ['echo "$(%s %s)"' % (_V, _P)], 1),
        # a `)` inside the substitution's own quotes does not close it
        ("substitution-with-quoted-paren",
         ["""echo "$(printf ')'; %s %s)\"""" % (_V, _P)], 1),
        ("substitution-unquoted", ["$(%s %s)" % (_V, _P)], 1),
        ("substitution-unquoted-in-arg", ["echo $(%s %s) x" % (_V, _P)], 1),
        ("backtick-unquoted", ["echo `%s %s`" % (_V, _P)], 1),
        ("subshell-group", ["(cd x && %s %s)" % (_V, _P)], 1),
        ("xargs-optional-operand-flag", ["xargs -i %s %s" % (_V, _P)], 1),
        ("backtick-subst-in-dquotes", ['echo "`%s %s`"' % (_V, _P)], 1),
        # a quoted operand of anything that is not purely text-emitting
        ("quoted-prose-command",
         ['Run the command "%s %s" now.' % (_V, _P)], 1),
        ("remote-carrier-quoted", ['ssh host "%s %s"' % (_V, _P)], 1),
        ("remote-carrier-single-quoted", ["ssh host '%s %s'" % (_V, _P)], 1),
        ("eval-quoted", ['eval "%s %s"' % (_V, _P)], 1),
        ("eval-bare", ["eval %s %s" % (_V, _P)], 1),
        ("eval-option-terminator", ["eval -- '%s %s'" % (_V, _P)], 1),
        ("env-split-injects-option", ["env -S '-i %s %s'" % (_V, _P)], 1),
        ("shell-c-option-terminator", ["bash -c -- '%s %s'" % (_V, _P)], 1),
        ("shell-c-extra-option", ["bash -c -e '%s %s'" % (_V, _P)], 1),
        # a forbidden form spelled later in ordinary prose
        ("prose-instruction", ["Never run %s %s from a session." % (_V, _P)], 1),
        ("prose-instruction-apostrophe",
         ["the lead's rule: never %s %s yourself" % (_V, _P)], 1),
        ("prose-instruction-forge",
         ["Do not %s %s merge the branch yourself." % (_G, _R)], 1),
        ("prose-instruction-dashed",
         ["Never invoke %s-%s by hand." % (_V, _K)], 1),
        # a soft-wrapped paragraph renders as one sentence
        ("prose-soft-wrapped",
         ["Under rhythm A the worker must never run %s" % _V,
          "%s until the lead says so." % _P], 1),
        # inline markup renders away
        ("prose-adjacent-code-spans",
         ["Never run `%s` `%s` yourself." % (_V, _P)], 1),
        ("prose-adjacent-emphasis",
         ["Never run **%s** *%s* yourself." % (_V, _P)], 1),
        ("prose-adjacent-links",
         ["Never run [%s](https://x) [%s](https://y) yourself." % (_V, _P)], 1),
        # a destination may hold BALANCED parens and escapes (round-18 finding 1)
        ("prose-links-balanced-parens",
         ["Never run [%s](https://example/x_(y)) [%s](u) yourself." % (_V, _P)],
         1),
        ("prose-links-title-and-escape",
         ['Never run [%s](https://x_(a(b)) "t") [%s](u\\)) yourself.' % (_V, _P)],
         1),
        ("prose-image-link",
         ["Never run ![%s](https://x) [%s](https://y) yourself." % (_V, _P)], 1),
        # a quote inside a destination is TEXT, not a title (round-19 finding 1)
        ("prose-links-apostrophe-dest",
         ["Never run [%s](https://en.wikipedia.org/wiki/Guns_N'_Roses) "
          "[%s](u) yourself." % (_V, _P)], 1),
        ("prose-links-angle-dest",
         ["Never run [%s](<https://x/a(b>) [%s](u) yourself." % (_V, _P)], 1),
        ("prose-links-real-title",
         ['Never run [%s](https://x "a title") [%s](u) yourself.' % (_V, _P)],
         1),
        ("prose-adjacent-strikethrough",
         ["Never run ~~%s~~ ~~%s~~ yourself." % (_V, _P)], 1),
        # a LIST ITEM's own paragraph soft-wraps onto the next line
        # (round-18 finding 2)
        ("list-item-continuation",
         ["- Never run %s" % _V, "  %s from a session." % _P], 1),
        ("numbered-item-continuation",
         ["1. Never run %s" % _V, "   %s from a session." % _P], 1),
        ("checklist-item-continuation",
         ["- [ ] Never run %s" % _V, "      %s from a session." % _P], 1),
        ("quoted-list-item-continuation",
         ["> - Never run %s" % _V, ">   %s from a session." % _P], 1),
        # an apostrophe in the prose must not hide a soft-wrapped form: the
        # pair gets the same unbalanced-quote fallback a physical line gets
        # (round-19 finding 2)
        ("apostrophe-soft-wrapped-pair",
         ["The worker's rule is never to run %s" % _V,
          "%s from a session." % _P], 1),
        ("apostrophe-list-continuation",
         ["- The worker's rule is never to run %s" % _V,
          "  %s from a session." % _P], 1),
        ("apostrophe-quoted-pair",
         ["> The lead's rule is never to run %s" % _V,
          "> %s from a session." % _P], 1),
        # the head is a known program whose own rule finds nothing
        ("prose-after-known-program-head",
         ["%s users must never run %s %s." % (_V, _V, _P)], 1),
        # wrappers with their own option arity
        ("nice-adjustment", ["nice -n 5 %s %s" % (_V, _P)], 1),
        ("nice-attached", ["nice -n5 %s %s" % (_V, _P)], 1),
        ("sudo-long-user", ["sudo --user root %s %s" % (_V, _P)], 1),
        ("sudo-short-user", ["sudo -u root %s %s" % (_V, _P)], 1),
        ("env-chdir", ["env --chdir /tmp %s %s" % (_V, _P)], 1),
        ("env-split-string", ['env -S "%s %s"' % (_V, _P)], 1),
        ("env-split-string-eq", ['env --split-string="%s %s"' % (_V, _P)], 1),
        # -S's operand may be ATTACHED, and short options cluster ahead of it
        ("env-split-attached", ["env -S%s %s" % (_V, _P)], 1),
        ("env-split-clustered", ["env -vS%s %s" % (_V, _P)], 1),
        ("env-split-clustered-null", ["env -0S%s %s" % (_V, _P)], 1),
        # -u eats the rest of the cluster, so this unsets a variable and the
        # command behind it is reached normally
        ("env-unset-cluster-is-not-a-split",
         ["env -uS%s %s %s" % (_V, _V, _P)], 1),
        ("env-argv0", ["env -a alias %s %s" % (_V, _P)], 1),
        ("env-optional-operand-flag",
         ["env --block-signal %s %s" % (_V, _P)], 1),
        ("nohup", ["nohup %s %s" % (_V, _P)], 1),
        ("setsid", ["setsid %s %s" % (_V, _P)], 1),
        ("stdbuf", ["stdbuf -o0 %s %s" % (_V, _P)], 1),
        ("timeout-duration", ["timeout 5 %s %s" % (_V, _P)], 1),
        ("timeout-kill-after", ["timeout -k 10 5 %s %s" % (_V, _P)], 1),
        ("xargs", ["xargs %s %s" % (_V, _P)], 1),
        ("xargs-max-args", ["xargs -n 1 %s %s" % (_V, _P)], 1),
        # the carriers the whole-line fixtures used to skip (round-20 finding 1)
        ("builtin", ["builtin %s %s" % (_V, _P)], 1),
        ("ionice", ["ionice %s %s" % (_V, _P)], 1),
        ("ionice-class-and-classdata",
         ["ionice -c 2 -n 7 %s %s" % (_V, _P)], 1),
        ("exec", ["exec %s %s" % (_V, _P)], 1),
        ("exec-argv0", ["exec -a alias %s %s" % (_V, _P)], 1),
        ("time", ["time %s %s" % (_V, _P)], 1),
        ("time-output", ["time -o out %s %s" % (_V, _P)], 1),
        ("doas", ["doas %s %s" % (_V, _P)], 1),
        ("doas-user", ["doas -u root %s %s" % (_V, _P)], 1),
        # the VCS global options that consume their operand: -C, -c and the
        # attached --<vcs>-dir form are above; these complete the set
        ("work-tree", ["%s --work-tree /tmp %s origin main" % (_V, _P)], 1),
        ("namespace", ["%s --namespace ns %s" % (_V, _P)], 1),
        ("config-env", ["%s --config-env=k=E %s" % (_V, _P)], 1),
        ("config-env-separate", ["%s --config-env k=E %s" % (_V, _P)], 1),
        # attached-operand-only options: the ATTACHED form sets the value and
        # the subcommand behind it really runs, so it must not be swallowed
        # (round-20 round-1 finding 2). The BARE form of these two is a
        # different thing entirely — see the terminal-global negatives.
        ("exec-path-attached", ["%s --exec-path=/x %s" % (_V, _P)], 1),
        ("super-prefix-attached", ["%s --super-prefix=x/ %s" % (_V, _P)], 1),
        # carrier options that were missing outright, each a silent miss behind
        # a text-emitter operand (round-20 round-1 finding 1)
        ("xargs-process-slot-var",
         ["xargs --process-slot-var echo %s %s" % (_V, _P)], 1),
        ("doas-auth-style", ["doas -a echo %s %s" % (_V, _P)], 1),
        ("ionice-pgid", ["ionice -P echo %s %s" % (_V, _P)], 1),
        ("ionice-uid", ["ionice --uid echo %s %s" % (_V, _P)], 1),
        # …and the optional-operand option that was listed as consuming one,
        # which swallowed the program behind it
        ("xargs-max-lines-bare", ["xargs --max-lines %s %s" % (_V, _P)], 1),
        # round-2 findings: more of the same class, each verified against the
        # real tool (git 2.54 consumes a separate operand for both of these;
        # sudo documents `-h host` and takes the next non-option token)
        ("shallow-file",
         ["%s --shallow-file echo %s origin main" % (_V, _P)], 1),
        ("attr-source", ["%s --attr-source echo %s origin main" % (_V, _P)], 1),
        ("sudo-host-short", ["sudo -h echo %s %s origin main" % (_V, _P)], 1),
        ("sudo-auth-type", ["sudo -a echo %s %s" % (_V, _P)], 1),
        ("sudo-auth-type-long", ["sudo --auth-type echo %s %s" % (_V, _P)], 1),
        ("sudo-login-class", ["sudo -c echo %s %s" % (_V, _P)], 1),
        ("sudo-login-class-long",
         ["sudo --login-class echo %s %s" % (_V, _P)], 1),
        # …and the forge CLI's, which had none
        ("forge-repo-short", ["%s -R o/r %s merge 1" % (_G, _R)], 1),
        ("forge-repo-long", ["%s --repo o/r %s create" % (_G, _R)], 1),
        ("forge-hostname", ["%s --hostname h %s ready 1" % (_G, _R)], 1),
        ("forge-header-short",
         ["%s -H 'a: b' %s -X POST repos/o/r/pulls" % (_G, _A)], 1),
        ("forge-header-long",
         ["%s --header 'a: b' %s close 1" % (_G, _R)], 1),
        # round-4 findings: the SAME class one token narrower — the
        # operand-taking option ENDS a short-option CLUSTER, so the cluster is
        # not an exact table match. Every operand below is the text-emitter, so
        # a walk that drops the cluster reads the emitter as the program and its
        # exemption hides the command. Each shape was run with printf/echo
        # standing in for the program and observed to execute it.
        ("carrier-cluster-env-unset", ["env -vu echo %s %s" % (_V, _P)], 1),
        ("carrier-cluster-env-chdir", ["env -vC echo %s %s" % (_V, _P)], 1),
        ("carrier-cluster-xargs-eof", ["xargs -tE echo %s %s" % (_V, _P)], 1),
        ("carrier-cluster-time-output", ["time -po echo %s %s" % (_V, _P)], 1),
        ("carrier-cluster-exec-argv0", ["exec -ca echo %s %s" % (_V, _P)], 1),
        ("carrier-cluster-sudo-user", ["sudo -nu echo %s %s" % (_V, _P)], 1),
        ("carrier-cluster-doas-user", ["doas -nu echo %s %s" % (_V, _P)], 1),
        ("carrier-cluster-timeout-signal",
         ["timeout -vs echo 5 %s %s" % (_V, _P)], 1),
        # nice and stdbuf have no no-operand short flag to cluster behind, so
        # these two are the SEPARATE shape with an emitter operand, not
        # clusters — named for what they are.
        ("carrier-nice-adjustment-operand-is-an-emitter",
         ["nice -n echo %s %s" % (_V, _P)], 1),
        ("carrier-stdbuf-output-operand-is-an-emitter",
         ["stdbuf -eL -o echo %s %s" % (_V, _P)], 1),
        ("carrier-cluster-ionice-classdata",
         ["ionice -tn echo %s %s" % (_V, _P)], 1),
        # …and the BSD-only carrier options the enumeration was missing, both
        # bare and clustered
        ("carrier-bsd-xargs-replstr", ["xargs -J echo %s %s" % (_V, _P)], 1),
        ("carrier-bsd-xargs-replstr-cluster",
         ["xargs -tJ echo %s %s" % (_V, _P)], 1),
        ("carrier-bsd-xargs-replacements",
         ["xargs -I{} -R echo %s %s" % (_V, _P)], 1),
        ("carrier-bsd-xargs-replsize",
         ["xargs -I{} -S echo %s %s" % (_V, _P)], 1),
        ("carrier-bsd-env-utilpath", ["env -P echo %s %s" % (_V, _P)], 1),
        ("carrier-bsd-env-utilpath-cluster",
         ["env -vP echo %s %s" % (_V, _P)], 1),
        # round-5 finding 1: FreeBSD env -L/-U user[/class] (documented, not
        # observable on this machine)
        ("carrier-bsd-env-login", ["env -L echo %s %s" % (_V, _P)], 1),
        ("carrier-bsd-env-login-cluster",
         ["env -vL echo %s %s" % (_V, _P)], 1),
        ("carrier-bsd-env-login-uppercase",
         ["env -U echo %s %s" % (_V, _P)], 1),
        # round-5 finding 2: the shell's own invocation options consume
        # operands, and the SCRIPT is the first operand after them. Observed on
        # bash/dash/zsh/ksh: each of these executes the quoted script.
        ("shell-c-then-option-with-operand",
         ["bash -c -o xtrace '%s %s'" % (_V, _P)], 1),
        ("shell-c-clustered-with-operand-option",
         ["bash -oc xtrace '%s %s'" % (_V, _P)], 1),
        ("shell-c-clustered-shopt-option",
         ["bash -Oc extglob '%s %s'" % (_V, _P)], 1),
        ("shell-plus-option-before-c",
         ["bash +o xtrace -c '%s %s'" % (_V, _P)], 1),
        ("shell-c-then-plus-option",
         ["bash -c +o xtrace '%s %s'" % (_V, _P)], 1),
        ("shell-shopt-option-before-c",
         ["bash -O extglob -c '%s %s'" % (_V, _P)], 1),
        ("shell-long-value-option-before-c",
         ["bash --rcfile /dev/null -c '%s %s'" % (_V, _P)], 1),
        ("shell-dash-option-with-operand",
         ["dash -c -o nolog '%s %s'" % (_V, _P)], 1),
        ("shell-zsh-option-with-operand",
         ["zsh -c -o xtrace '%s %s'" % (_V, _P)], 1),
        # round-6 finding 1: the four shells do not share one option arity, and
        # three forms were silent misses under a single model. Spelled with an
        # ESCAPED space rather than quotes ON PURPOSE — a QUOTED script is
        # carried by the quoted-operand pass whatever the shell parse does, so
        # only the escaped spelling actually tests the parse; each was measured
        # to be a silent miss before the per-shell map and each was observed to
        # EXECUTE on the shell it names.
        ("shell-zsh-bare-shopt-letter-reaches-the-script",
         ["zsh -O -c %s\\ %s" % (_V, _P)], 1),
        ("shell-zsh-attached-option-name-reaches-the-script",
         ["zsh -oerrexit -c %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh-attached-option-name-reaches-the-script",
         ["ksh -oerrexit -c %s\\ %s" % (_V, _P)], 1),
        ("shell-zsh-attached-name-inside-a-cluster",
         ["zsh -xoerrexit -c %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh-mask-operand-separate",
         ["ksh -c -T 0 %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh-mask-operand-attached",
         ["ksh -c -T0 %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh-mask-operand-in-a-cluster",
         ["ksh -c -xT 0 %s\\ %s" % (_V, _P)], 1),
        # …and the ambiguous name is read as ALL FOUR models, so a divergence
        # between them is still reported: under bash `-O` eats the `-c` and
        # under bash/dash/zsh `-T` is bare, but some plausible `sh` runs each.
        ("shell-ambiguous-sh-unions-the-shopt-letter",
         ["sh -O -c %s\\ %s" % (_V, _P)], 1),
        ("shell-ambiguous-sh-unions-the-attached-name",
         ["sh -oerrexit -c %s\\ %s" % (_V, _P)], 1),
        ("shell-ambiguous-sh-unions-the-mask-operand",
         ["sh -c -T 0 %s\\ %s" % (_V, _P)], 1),
        # `ksh` is ambiguous too — ksh93 here, pdksh/mksh elsewhere — so it is
        # unioned with the minimal POSIX reading. This is the DELIBERATE
        # over-detection that buys the coverage: no measured ksh executes
        # `-c -R <cmd>` (ksh93 answers "-c requires argument" because -R ate the
        # command; a ksh without -R rejects the option), but a ksh whose -R is
        # bare would run it, and the union reports it rather than assuming one.
        ("shell-ksh-union-reports-a-bare-xref-reading",
         ["ksh -c -R %s\\ %s" % (_V, _P)], 1),
        # round-8 finding 1: a BARE `+`. Both of these were measured to EXECUTE
        # the escaped command and both returned no finding before — the walk
        # read `+` as a plain operand, which lost the script after `-c` on all
        # four shells and lost the whole parse before it.
        ("shell-bash-bare-plus-reaches-the-command-flag",
         ["bash + -c %s\\ %s" % (_V, _P)], 1),
        ("shell-dash-bare-plus-reaches-the-command-flag",
         ["dash + -c %s\\ %s" % (_V, _P)], 1),
        ("shell-bare-plus-after-c-is-not-the-script",
         ["zsh -c + %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh-bare-plus-after-c-is-not-the-script",
         ["ksh -c + %s\\ %s" % (_V, _P)], 1),
        ("shell-bare-dash-after-c-is-not-the-script",
         ["bash -c - %s\\ %s" % (_V, _P)], 1),
        ("shell-ambiguous-sh-unions-the-bare-plus",
         ["sh + -c %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh-union-covers-the-bare-plus",
         ["ksh + -c %s\\ %s" % (_V, _P)], 1),
        # round-9 finding 1: ksh93's `-o` declines a separate operand when the
        # next token is an option, so the `-c` behind it is still reached.
        ("shell-ksh93-optional-operand-declined",
         ["ksh -o -c %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-optional-operand-declined-plus",
         ["ksh +o -c %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-optional-operand-mid-walk",
         ["ksh -c -o -x %s\\ %s" % (_V, _P)], 1),
        ("shell-ambiguous-sh-unions-the-optional-operand",
         ["sh -o -c %s\\ %s" % (_V, _P)], 1),
        # round-9 finding 2: a `+` token whose body contains a dash — ksh93
        # parses through it, zsh reads exactly `+-` as end-of-options.
        ("shell-ksh93-plusdash-parses-through",
         ["ksh +- -c %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-plusdash-long-parses-through",
         ["ksh +-- -c %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-plusdash-carries-the-command-flag",
         ["ksh +-c %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-plusdash-with-an-operand-letter",
         ["ksh +-o errexit -c %s\\ %s" % (_V, _P)], 1),
        ("shell-zsh-plusdash-after-c-is-not-the-script",
         ["zsh -c +- %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-plusdash-after-c-is-not-the-script",
         ["ksh -c +-x %s\\ %s" % (_V, _P)], 1),
        # round-11 finding: ksh93 needs NO `-c` and no option spelling at all.
        # It opens its first operand as a script FILE and, when that open
        # fails, executes the operand TEXT as a command line — so every line
        # below really runs the form on ksh93u+ 2012-08-01. Spelled with an
        # ESCAPED space, not quotes, on purpose: a QUOTED operand is carried by
        # the quoted-operand pass whatever the shell parse does, so only the
        # escaped spelling tests the parse. Each was a silent miss (the walk
        # answered "no script") until the first-operand flag; the previously
        # stated conjunction — that a miss also needed "an option spelling no
        # shipped skill would plausibly contain" — was false, and the first
        # case here is why.
        ("shell-ksh93-first-operand-is-a-command",
         ["ksh %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-first-operand-behind-a-bare-flag",
         ["ksh -x %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-first-operand-behind-an-option-operand",
         ["ksh -o errexit %s\\ %s" % (_V, _P)], 1),
        # the four option spellings that reach it with an `-o` in the token:
        # `-o` takes the attached/next name and there is no command flag left,
        # which is exactly what the walk used to read as "no script"
        ("shell-ksh93-attached-option-name-then-first-operand",
         ["ksh -oc %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-separate-option-name-then-first-operand",
         ["ksh -o c %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-plus-attached-option-name-then-first-operand",
         ["ksh +oc %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-dashed-plus-cluster-then-first-operand",
         ["ksh +-xoc %s\\ %s" % (_V, _P)], 1),
        # …and every option-introducer that ENDS options still leaves a command
        # line behind it on this model
        ("shell-ksh93-first-operand-after-terminator",
         ["ksh -- %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-first-operand-after-bare-dash",
         ["ksh - %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-first-operand-after-bare-plus",
         ["ksh + %s\\ %s" % (_V, _P)], 1),
        # The `sh` NAME unions ksh93 and ksh93 keeps the behaviour when it IS
        # /bin/sh (observed through a symlink named `sh`), so the bare `sh`
        # spelling carries it too.
        ("shell-sh-union-first-operand-is-a-command",
         ["sh %s\\ %s" % (_V, _P)], 1),
        ("shell-sh-union-first-operand-behind-a-flag",
         ["sh -x %s\\ %s" % (_V, _P)], 1),
        # round-12 finding: the operands BEHIND that first one are appended to
        # the command line — ksh93 runs the operand text with a literal `"$@"`
        # after it — so the form does not have to sit inside ONE token, and
        # this spelling needs no escaping and no quoting at all, which makes it
        # the most plausible of the lot. Measured: `ksh X=1 git --version`
        # prints git's own version string. Reading only the first operand
        # resolved these to "X=1" and reported nothing.
        ("shell-ksh93-form-in-the-appended-operands",
         ["ksh X=1 %s %s origin main" % (_V, _P)], 1),
        ("shell-ksh93-form-split-across-operands",
         ["ksh X=1 %s %s" % (_V, _P)], 1),
        ("shell-sh-union-form-split-across-operands",
         ["sh X=1 %s %s" % (_V, _P)], 1),
        ("shell-ksh93-split-operands-behind-a-flag",
         ["ksh -x X=1 %s %s" % (_V, _P)], 1),
        ("shell-ksh93-split-operands-after-terminator",
         ["ksh -- X=1 %s %s" % (_V, _P)], 1),
        # …and behind an option-NAME spelling, where the walk has to land on
        # the right operand before the join can reach anything
        ("shell-ksh93-split-operands-after-attached-option-name",
         ["ksh -oc X=1 %s %s" % (_V, _P)], 1),
        # round-12 finding: an appended operand is ONE WORD, so re-joining it
        # as raw source splits it and LOSES the form. Both of these execute —
        # measured with `--version` in place of the subcommand:
        # `ksh 'sh -c' 'git --version'` and `ksh 'git -C' /tmp --version` both
        # print git's version. Under a plain space-join the nested `-c` script
        # became the bare VCS token (its subcommand demoted to $0) and the
        # spaced path operand became two tokens (making "such" the
        # subcommand), so BOTH scanned clean.
        ("shell-ksh93-appended-operand-is-a-nested-shell-script",
         ["ksh sh\\ -c %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-appended-operand-holds-a-spaced-option-value",
         ["ksh %s\\ -C /tmp/no\\ such %s" % (_V, _P)], 1),
        ("shell-sh-union-appended-operand-is-a-nested-shell-script",
         ["sh sh\\ -c %s\\ %s" % (_V, _P)], 1),
        ("shell-ksh93-nested-script-after-terminator",
         ["ksh -- sh\\ -c %s\\ %s" % (_V, _P)], 1),
        # round-13 finding: an appended operand carrying APOSTROPHES costs more
        # to re-serialize than it spent in the source, so the reconstruction is
        # LONGER than the line it came from. The walk used to drop a nested
        # string that was not strictly shorter, so this scanned clean while the
        # invocation really reaches the VCS with both global config operands
        # (measured with `--version` in place of the subcommand). The length
        # test is gone; the walk terminates on a lexicographic pair — NOT on
        # the visited set, which only stops a string that recurs. See
        # `scan_command_text`.
        ("shell-ksh93-reconstruction-longer-than-its-source",
         ["""ksh X=1 %s -c "foo.bar=a'b" -c "baz.qux=c'd" %s"""
          % (_V, _P)], 1),
        ("shell-ksh93-reconstruction-longer-single-operand",
         ["""ksh X=1 %s -c "a.b=c'd'e'f'g'h" %s""" % (_V, _P)], 1),
        # shell grammar words ahead of the command
        ("control-if", ["if %s %s" % (_V, _P)], 1),
        ("control-while-do", ["while true" , "do %s %s" % (_V, _P)], 2),
        ("control-bang", ["! %s %s" % (_V, _P)], 1),
        ("control-brace", ["{ %s %s; }" % (_V, _P)], 1),
        # the dashed plumbing executables
        ("dashed-pack", ["%s-%s host:repo" % (_V, _K)], 1),
        ("dashed-pack-abs", ["/usr/lib/%s-core/%s-%s host:repo" % (_V, _V, _K)], 1),
        ("dashed-publish-abs",
         ["/usr/lib/%s-core/%s-%s origin main" % (_V, _V, _P)], 1),
        # backslash-newline continuations — reported at the FIRST physical line
        ("multiline-bare", ["%s \\" % _V, "%s origin main" % _P], 1),
        ("multiline-dash-C", ["%s -C /x \\" % _V, "  %s" % _P], 1),
        ("multiline-pack", ["%s \\" % _V, "%s host:repo" % _K], 1),
        ("multiline-forge", ["%s %s \\" % (_G, _R), "merge 1"], 1),
        # Markdown prefixes (round-16 finding 7)
        ("markdown-bullet", ["- %s %s origin main" % (_V, _P)], 1),
        ("markdown-numbered", ["1. %s -C /x %s" % (_V, _P)], 1),
        ("markdown-blockquote", ["> %s %s merge 1" % (_G, _R)], 1),
        ("markdown-blockquote-nospace", [">%s %s" % (_V, _P)], 1),
        ("markdown-checklist", ["- [ ] %s %s" % (_V, _P)], 1),
        ("markdown-star-bullet", ["  * %s %s" % (_V, _P)], 1),
        ("markdown-quoted-bullet", ["> - %s %s" % (_V, _P)], 1),
        ("markdown-heading", ["### %s %s" % (_V, _P)], 1),
        ("markdown-emphasis", ["**%s %s** is what the daemon does" % (_V, _P)], 1),
        ("markdown-code-span", ["run `%s %s` yourself" % (_V, _P)], 1),
        ("markdown-link", ["[%s %s](https://example/x)" % (_V, _P)], 1),
        ("html-comment", ["<!-- %s %s -->" % (_V, _P)], 1),
        ("shell-comment", ["# %s %s   (the retired way)" % (_V, _P)], 1),
        ("prose-label", ["Run: %s %s" % (_V, _P)], 1),
        ("yaml-run-key", ["        run: %s %s origin main" % (_V, _P)], 1),
        ("markdown-bullet-multiline", ["- %s \\" % _V, "  %s origin main" % _P], 1),
        ("markdown-blockquote-multiline", ["> %s \\" % _V, "> %s" % _P], 1),
        # only the quote-NAIVE reading sees this: the apostrophe in prose opens
        # a shell single-quote that would otherwise swallow the rest
        ("apostrophe-prose",
         ["under A/C it's deferred; %s %s origin main follows the green-light"
          % (_V, _P)], 1),
        # …and here the code span is what saves it, on a balanced line
        ("apostrophe-code-span",
         ["the lead's `%s %s` and the worker's job" % (_V, _P)], 1),
        # a finding anywhere on the line, not only at its start
        ("after-separator", ["%s commit -m x && %s %s" % (_V, _V, _P)], 1),
        ("second-line", ["intro prose", "    %s %s" % (_V, _P)], 2),
        # ── the two EXECUTABLE quote forms the two-form model could not see ──
        # Each was run against the real tool before it was encoded: with `-h`
        # appended, every line below prints the publish usage on this host
        # (bash 3.2.57(1), git 2.54.0) — the shell handed the decoded word to
        # the VCS. ONE exception, marked at its case: `\u`/`\U` were added in
        # bash 4.2 and this host's bash prints them literally, so those two are
        # a VERSION union exactly like the carrier tables' platform union — the
        # floor guard decodes them too, and a union can only over-detect.
        ("ansi-c-subcommand", ["%s $'%s'" % (_V, _P)], 1),
        ("ansi-c-hex-subcommand", ["%s %s" % (_V, _ansi_c(_P))], 1),
        ("ansi-c-octal-subcommand", ["%s %s" % (_V, _ansi_c(_P, "o"))], 1),
        # DOCUMENTED (bash >= 4.2), not observed on this host — see above.
        ("ansi-c-unicode-subcommand", ["%s %s" % (_V, _ansi_c(_P, "u"))], 1),
        ("ansi-c-unicode-long-subcommand",
         ["%s %s" % (_V, _ansi_c(_P, "U"))], 1),
        # a word ASSEMBLED from two adjacent ANSI-C regions — neither half is
        # the word, so a scanner matching whole tokens sees nothing
        ("ansi-c-split-subcommand",
         ["%s $'%s'$'%s'" % (_V, _P[:2], _P[2:])], 1),
        # …and the PROGRAM name spelled the same way: no literal <vcs> appears
        # anywhere on the line
        ("ansi-c-program", ["%s %s" % (_ansi_c(_V), _P)], 1),
        ("ansi-c-program-and-subcommand",
         ["%s %s" % (_ansi_c(_V), _ansi_c(_P))], 1),
        # an ANSI-C region concatenated onto a bare prefix
        ("ansi-c-partial-word", ["%s %s$'%s'" % (_V, _P[:2], _P[2:])], 1),
        # locale-translation quoting behaves as a double-quoted string
        ("locale-quote-subcommand", ['%s $"%s"' % (_V, _P)], 1),
        ("locale-quote-program", ['$"%s" %s' % (_V, _P)], 1),
        # a shell `-c` script that is itself ANSI-C quoted
        ("ansi-c-shell-script", ["bash -c $'%s %s'" % (_V, _P)], 1),
        # the DOUBLE-QUOTE layer must not corrupt a nested ANSI-C word: an
        # unconditional backslash drop rewrote the hex spelling to `$'x70ush'`
        # and the inner decode then produced `x70ush`
        ("ansi-c-inside-double-quotes",
         ['bash -c "%s %s"' % (_V, _ansi_c(_P))], 1),
        # ANSI-C inside a command substitution — the substitution reader used to
        # carry its own two-form quote loop
        ("ansi-c-in-substitution", ["echo $(%s $'%s')" % (_V, _P)], 1),
        ("ansi-c-in-backticks", ["echo `%s $'%s'`" % (_V, _P)], 1),
        # ---- the TWO-WORD publishing families ------------------------------
        # A family subcommand whose own operation reaches a remote. None of
        # these contains the one-word form anywhere on the line.
        ("vcs-pair-subtree",
         ["%s %s %s --prefix=x origin main" % (_V, _SUB, _P)], 1),
        ("vcs-pair-svn", ["%s %s %s" % (_V, _SVN, _DC)], 1),
        ("vcs-pair-p4", ["%s %s %s" % (_V, _P4, _SM)], 1),
        ("vcs-pair-lfs", ["%s %s %s origin main" % (_V, _LFS, _P)], 1),
        ("vcs-pair-lfs-hook-plumbing",
         ["%s %s %s origin main" % (_V, _LFS, _PP)], 1),
        # the family's option walk must reach PAST an option and its operand…
        ("vcs-pair-behind-a-long-option-operand",
         ["%s %s --prefix x %s origin main" % (_V, _SUB, _P)], 1),
        ("vcs-pair-behind-a-short-option-operand",
         ["%s %s -P x %s origin main" % (_V, _SUB, _P)], 1),
        # …and past a BARE family flag, which consumes nothing
        ("vcs-pair-behind-a-bare-family-flag",
         ["%s %s -q %s --prefix=x o m" % (_V, _SUB, _P)], 1),
        # …and the family itself must be reached past a VCS global
        ("vcs-pair-behind-a-vcs-global",
         ["%s -C /x %s %s --prefix=y o m" % (_V, _SUB, _P)], 1),
        # the prose pass reaches it at any token position, like the one-word
        # form
        ("vcs-pair-in-prose",
         ["Never run %s %s %s from a session" % (_V, _SUB, _P)], 1),
        # and so do the carrier / nesting passes
        ("vcs-pair-through-a-carrier",
         ["sudo -u root %s %s %s --prefix=x o m" % (_V, _SUB, _P)], 1),
        ("vcs-pair-in-a-shell-script",
         ['bash -c "%s %s %s"' % (_V, _P4, _SM)], 1),
        # ---- the widened forge PR vocabulary and the other families --------
        ("forge-update-branch", ["%s %s update-branch 123" % (_G, _R)], 1),
        ("forge-revert", ["%s %s revert 1" % (_G, _R)], 1),
        ("forge-reopen", ["%s %s reopen 1" % (_G, _R)], 1),
        ("forge-repo-create-with-the-publishing-flag",
         ["%s %s create x --%s" % (_G, _REPO, _P)], 1),
        ("forge-repo-create-flag-before-the-name",
         ["%s %s create --%s x" % (_G, _REPO, _P)], 1),
        ("forge-repo-sync-with-a-destination",
         ["%s %s sync owner/x" % (_G, _REPO)], 1),
        ("forge-release-create", ["%s %s create v1.0" % (_G, _REL)], 1),
        ("forge-family-behind-a-global",
         ["%s -R o/r %s create v1.0" % (_G, _REL)], 1),
        ("forge-family-in-prose",
         ["Never run %s %s create yourself" % (_G, _REL)], 1),
        ("forge-family-in-a-shell-script",
         ['bash -c "%s %s create v1.0"' % (_G, _REL)], 1),
        # …and a boolean flag carrying a TRUE value still publishes
        ("forge-repo-create-publishing-flag-set-true",
         ["%s %s create o/r --%s=true" % (_G, _REPO, _P)], 1),
        # A body flag consumes its own operand, so a method flag sitting in that
        # position is the field's VALUE and sets no method at all — the call is
        # still a POST. Reading the flag as bare turns this into an explicit
        # GET and loses the finding.
        ("api-field-operand-is-not-a-method-flag",
         ["%s %s x -f -X GET" % (_G, _A)], 1),
        # ---- the INLINE ALIAS ----------------------------------------------
        # The publishing word need not appear in subcommand position at all.
        ("vcs-alias-defined-on-the-line",
         ["%s -c %sp=%s p" % (_V, _AP, _P)], 1),
        ("vcs-alias-quoted-definition",
         ["%s -c '%sp=%s' p" % (_V, _AP, _P)], 1),
        # the value is split with the tool's own splitter, so an escaped
        # spelling still IS the subcommand
        ("vcs-alias-backslash-escaped-value",
         ["%s -c '%sp=%s\\%s' p" % (_V, _AP, _P[0], _P[1:])], 1),
        # an expansion may introduce further globals…
        ("vcs-alias-expansion-introduces-a-global",
         ["%s -c '%sp=-c color.ui=never %s' p" % (_V, _AP, _P)], 1),
        # …or name another alias, hop after hop
        ("vcs-alias-chain", ["%s -c %sa=b -c %sb=%s a" % (_V, _AP, _AP, _P)], 1),
        # a value behind the shell marker is a COMMAND LINE, recursed into
        ("vcs-alias-shell-value",
         ["%s -c '%sp=!%s %s' p" % (_V, _AP, _V, _P)], 1),
        # the config key's section is case-insensitive
        ("vcs-alias-prefix-is-case-insensitive",
         ["%s -c %sp=%s p" % (_V, _AP.upper(), _P)], 1),
        # …and so is the alias NAME, in both directions
        ("vcs-alias-name-defined-upper-invoked-lower",
         ["%s -c %sPP=%s pp" % (_V, _AP, _P)], 1),
        ("vcs-alias-name-defined-lower-invoked-upper",
         ["%s -c %spp=%s PP" % (_V, _AP, _P)], 1),
        # an alias may expand to a TWO-WORD family form
        ("vcs-alias-to-a-family-operation",
         ["%s -c %sp=%s p --prefix=x %s" % (_V, _AP, _SUB, _P)], 1),
        # and the alias is reached through the ordinary carrier / prose passes
        ("vcs-alias-through-a-carrier",
         ["sudo -u root %s -c %sp=%s p" % (_V, _AP, _P)], 1),
        ("vcs-alias-in-prose",
         ["Never run %s -c %sp=%s p yourself" % (_V, _AP, _P)], 1),
        # …including behind an execution carrier this gate does not know by
        # name, where the PROSE pass is the only thing that reaches the alias
        # and therefore the only thing that can hand its shell value on
        ("vcs-alias-shell-value-behind-an-unknown-carrier",
         ["myrunner %s -c '%sp=!%s %s' p" % (_V, _AP, _V, _P)], 1),
        # ---- a `${…}` in an OPERATION position -----------------------------
        # The parameter is unknowable, but the literal in the expansion is on
        # the line, and every operation position asks the same question.
        ("expansion-as-the-subcommand", ["%s ${x:+%s}" % (_V, _P)], 1),
        ("expansion-as-a-family-operation",
         ["%s %s ${x:+%s}" % (_V, _LFS, _P)], 1),
        ("expansion-as-the-forge-subcommand",
         ["%s ${x:+%s} merge 1" % (_G, _R)], 1),
        ("expansion-as-a-forge-action",
         ["%s %s ${x:+merge} 1" % (_G, _R)], 1),
        ("expansion-as-a-forge-family",
         ["%s ${x:+%s} sync owner/x" % (_G, _REPO)], 1),
        ("expansion-as-a-forge-family-action",
         ["%s %s ${x:+create} v1.0" % (_G, _REL)], 1),
        ("expansion-nested", ["%s ${x:+${y:-%s}}" % (_V, _P)], 1),
        # ---- the DASHED family executables ---------------------------------
        ("vcs-dashed-family", ["%s-%s %s origin main" % (_V, _LFS, _P)], 1),
        ("vcs-dashed-family-with-an-option",
         ["%s-%s %s --prefix=x o m" % (_V, _SUB, _P)], 1),
        ("vcs-dashed-family-absolute-path",
         ["/usr/lib/%s-core/%s-%s %s" % (_V, _V, _P4, _SM)], 1),
        # …and at a position OTHER than the head, which is what a shipped
        # sentence naming it actually looks like
        ("vcs-dashed-family-in-prose",
         ["Never run %s-%s %s yourself" % (_V, _LFS, _P)], 1),
        ("vcs-dashed-family-behind-an-unknown-carrier",
         ["ssh host %s-%s %s" % (_V, _LFS, _P)], 1),
        # ---- round-1 gate findings ------------------------------------------
        # An escaped separator inside a substitution's PATTERN is a literal
        # slash, so the replacement really is the publishing word.
        ("expansion-escaped-separator-in-the-pattern",
         ["%s ${x/foo\\/bar/%s}" % (_V, _P)], 1),
        # …and a backslash INSIDE the replacement word is dropped by the shell,
        # so the literal to compare is the unescaped text
        ("expansion-escaped-replacement-word",
         ["%s ${x/y/%s\\%s}" % (_V, _P[:2], _P[2:])], 1),
        # An alias NAME reached through an expansion resolves like any other.
        ("vcs-alias-name-through-an-expansion",
         ["%s -c %sp=%s ${x:+p}" % (_V, _AP, _P)], 1),
        # An expansion body does not split on whitespace: the word is the whole
        # text after the operator, stripped, and the braces are what end it.
        ("expansion-word-with-surrounding-space",
         ["%s ${x:- %s }" % (_V, _P)], 1),
        # ---- round-2 gate findings -----------------------------------------
        # A shell-valued alias runs its value AND the invocation's remaining
        # operands, appended as words — so the publishing word can sit outside
        # the alias definition entirely, unquoted.
        ("vcs-alias-shell-value-appends-the-operands",
         ["%s -c %sp=!%s p %s" % (_V, _AP, _V, _P)], 1),
        # An ESCAPED brace is part of the word and closes nothing, so the
        # substitution's replacement really is the publishing word.
        ("expansion-escaped-brace-inside-the-pattern",
         ["%s ${x/a\\}b/%s}" % (_V, _P)], 1),
        # EVERY candidate an operand could expand to is tried, not just the
        # first: here the first names a family whose operation does not match,
        # or an action whose condition is not met, and the SECOND decides.
        ("vcs-pair-second-candidate-decides",
         ["%s ${a:+%s}${b:+%s} %s" % (_V, _P4, _LFS, _P)], 1),
        ("forge-family-second-candidate-decides",
         ["%s ${a:+%s}${b:+%s} create v1.0" % (_G, _REPO, _REL)], 1),
        ("forge-family-second-action-decides",
         ["%s %s ${a:+create}${b:+sync} owner/x" % (_G, _REPO)], 1),
        # …and the last two candidate positions, closed in round 3a: an alias
        # NAME (whose resolution CONSUMES the alias, so each candidate needs
        # its own copy of the map) and the forge SUBCOMMAND itself.
        ("vcs-alias-second-candidate-decides",
         ["%s -c %sa=status -c %sb=%s ${x:+a}${y:+b}" % (_V, _AP, _AP, _P)], 1),
        ("forge-subcommand-second-candidate-decides",
         ["%s ${a:+%s}${b:+%s} view -f k=v" % (_G, _R, _A)], 1),
        # ---- the guard's next four commits, re-differentialled -------------
        # A QUOTED brace closes nothing either, which is the escaped-brace fact
        # one spelling further out. MEASURED on all three shells here: with x
        # set to `a}b`, `${x/"a}b"/<publish>}` yields the publishing word on
        # bash 3.2.57, zsh 5.9 and ksh93u+.
        ("expansion-quoted-brace-inside-the-pattern",
         ["%s ${x/\"a}b\"/%s}" % (_V, _P)], 1),
        # A quoted SEPARATOR is read BOTH ways, because the shells disagree and
        # each reading is a real publish on some measured shell. ksh93u+ takes
        # the quoted `/` as part of the pattern…
        ("expansion-quoted-separator-in-the-pattern",
         ["%s ${x/\"a/b\"/%s}" % (_V, _P)], 1),
        # …while bash 3.2.57 takes it as the separator, so a pattern-only
        # spelling really does yield the publishing word alone (argc=1).
        ("expansion-quoted-separator-read-naively",
         ["%s ${x/\"a/%s\"}" % (_V, _P)], 1),
        # The default / alternate operators drop a backslash exactly as the
        # replacement side does, and a quoted word contributes its VALUE.
        ("expansion-escaped-value-word",
         ["%s ${x:-%s\\%s}" % (_V, _P[:2], _P[2:])], 1),
        ("expansion-escaped-alternate-word",
         ["%s ${x:+%s\\%s}" % (_V, _P[:2], _P[2:])], 1),
        ("expansion-escaped-bare-dash-word",
         ["%s ${x-%s\\%s}" % (_V, _P[:2], _P[2:])], 1),
        ("expansion-quoted-value-word",
         ["%s ${x:-\"%s\"}" % (_V, _P)], 1),
        # An action's own option consumes its VALUE and nothing more, so a real
        # destination behind it is still the destination.
        ("forge-repo-sync-option-value-then-a-destination",
         ["%s %s sync --source owner/upstream owner/dest" % (_G, _REPO)], 1),
        # …and a cluster whose first letter takes the ATTACHED remainder leaves
        # the following token as the destination.
        ("forge-repo-sync-short-cluster-then-a-destination",
         ["%s %s sync -sb owner/dest" % (_G, _REPO)], 1),
        # The force flag takes no operand, so the destination behind it counts.
        ("forge-repo-sync-force-flag-then-a-destination",
         ["%s %s sync --force owner/dest" % (_G, _REPO)], 1),
        # pflag booleans are LAST-WINS in both directions: a false value
        # followed by a bare re-enable really does publish.
        ("forge-repo-create-publishing-flag-re-enabled-last",
         ["%s %s create o/r --source=. --%s=false --%s"
          % (_G, _REPO, _P, _P)], 1),
        # The VCS subcommands that EXECUTE an operand. The guard needs a table
        # entry per subcommand because it has no quoted-operand pass; here the
        # quoted-operand and positionless passes already reach them, so what is
        # pinned is the FORM rather than a second copy of the table — one case
        # per entry, so a reading change that silently stopped covering one of
        # them fails here instead of in a differential nobody re-ran.
        ("vcs-submodule-runner-quoted",
         ["%s submodule foreach '%s %s'" % (_V, _V, _P)], 1),
        ("vcs-submodule-runner-bare",
         ["%s submodule foreach %s %s" % (_V, _V, _P)], 1),
        ("vcs-submodule-runner-ansi-c",
         ["%s submodule foreach %s" % (_V, _ansi_c("%s %s" % (_V, _P)))], 1),
        ("vcs-bisect-runner-quoted",
         ["%s bisect run '%s %s'" % (_V, _V, _P)], 1),
        ("vcs-bisect-runner-through-a-shell",
         ["%s bisect run sh -c '%s %s'" % (_V, _V, _P)], 1),
        ("vcs-rebase-exec-long",
         ["%s rebase --exec '%s %s' main" % (_V, _V, _P)], 1),
        ("vcs-rebase-exec-short",
         ["%s rebase -x '%s %s' main" % (_V, _V, _P)], 1),
        ("vcs-rebase-exec-attached",
         ["%s rebase --exec=\"%s %s\" main" % (_V, _V, _P)], 1),
        ("vcs-history-rewrite-tree-filter",
         ["%s filter-branch --tree-filter '%s %s' HEAD" % (_V, _V, _P)], 1),
        ("vcs-history-rewrite-index-filter",
         ["%s filter-branch --index-filter '%s %s' HEAD" % (_V, _V, _P)], 1),
        # …and the dashed family executable behind one of those runners
        ("vcs-submodule-runner-dashed-family",
         ["%s submodule foreach %s-%s %s" % (_V, _V, _LFS, _P)], 1),
        # ---- round-4 gate findings ------------------------------------------
        # Each alias candidate needs the map as it stood BEFORE any branch ran,
        # and the two cases already here do not say so: both survive a SHARED
        # map that merely skips an already-consumed alias. This one does not —
        # the first candidate's expansion REDEFINES the second harmlessly and
        # consumes it, so only a branch resolving from the original map reaches
        # the publishing value. Verified against that exact variant: it passes
        # both earlier cases and fails this one.
        ("vcs-alias-candidate-branches-need-the-original-map",
         ["%s -c \"%sa=-c %sb=status b\" -c %sb=%s ${x:+a}${y:+b}"
          % (_V, _AP, _AP, _AP, _P)], 1),
        # A BALANCED empty pattern really can yield the word, so the
        # quote-aware half must keep reporting it. MEASURED with x empty:
        # `${x/""/<publish>}` yields the publishing word on zsh 5.9 and on
        # ksh93u+ (bash 3.2.57 declines, dash rejects the substitution).
        ("expansion-balanced-empty-pattern",
         ["%s ${x/\"\"/%s}" % (_V, _P)], 1),
        # ---- gate rounds 5-7 -------------------------------------------------
        # The emptiness test must ask the QUOTING MODEL, and a set of NEGATIVES
        # cannot say so on its own: a narrowing that strips quote characters
        # answers "empty" on every one of them too. It takes a POSITIVE whose
        # pattern the model reads as a NON-empty value while being made
        # entirely of characters such a narrowing removes — a quoted literal
        # dollar. MEASURED: with x set to that one character, bash 3.2.57
        # yields the publishing word (its separator search is not quote-aware,
        # so this is a naive-reading-only form); zsh 5.9 and ksh93u+ leave the
        # value unchanged and dash rejects the substitution. A real publish on
        # the shell whose reading produces it.
        #
        # An earlier version of this comment claimed "every character-stripping
        # narrowing loses it". **RETRACTED** — it is true of a fixed-set
        # `strip` and false of an ordered one: removing a leading dollar FIRST
        # and stripping quotes afterwards keeps this positive and answers empty
        # on the negatives above. That mutant is in the battery, killed by the
        # generated composite negatives, and the honest statement is the
        # narrow one: no fixture set can pin "asks the model" against an
        # arbitrary normalization, because a normalization can always be built
        # to agree on any finite corpus. The corpus pins the members it names;
        # the reading of the code is what pins the rule. Class (e), stated
        # rather than restated as a stronger claim.
        ("expansion-naive-separator-with-a-quoted-literal-dollar-pattern",
         ["%s ${x/\"$/%s\"}" % (_V, _P)], 1),
        # ---- gate round 8: re-differentialled against the guard at 5abcb8d4 ---
        # ONLY `${` opens a nested expansion; a bare `{` in a body is text. Both
        # readings had counted it, so the body ran past its real terminator and
        # the operands behind it fused into one word. MEASURED on bash 3.2.57
        # with x set to that one character: argc=3, the publishing subcommand
        # alone in $1 (zsh 5.9 and dash reject the line). Two spellings, because
        # the two egress words take different paths out of the walk.
        ("expansion-bare-open-brace-is-text-not-nesting",
         ["%s ${x/{/%s} origin main" % (_V, _P)], 1),
        ("expansion-bare-open-brace-is-text-plumbing",
         ["%s ${x/{/%s} origin" % (_V, _K)], 1),
        # …and the shape that pins the BODY walk specifically. The two sites
        # answer different questions and a fixture can hold for one while the
        # other is still counting: on the single-expansion forms above the body
        # walk's over-extension is undone by `trim_token` (`<publish>}` trims
        # back to the word), so they pass with that site unfixed. It takes TWO
        # expansions in ONE token — the bare `{` in the first one's pattern
        # fuses them, and the second, which is where the publishing word lives,
        # is then never parsed at all. MEASURED on bash 3.2.57 with both
        # parameters unset: argc=3 and the publishing subcommand alone in $1
        # (zsh 5.9 and dash reject the line). Found by fuzzing the body walk
        # against a copy of itself with the counting restored — 8640 generated
        # tokens, 338 verdict divergences, all of this shape.
        ("expansion-bare-open-brace-fuses-two-expansions-in-one-token",
         ["%s ${x//{}${y:-%s} origin main" % (_V, _P)], 1),
    ] + _carrier_positive_cases() + _set_member_positive_cases()


# One EXPLICIT row per member, written out rather than generated from the
# enumeration above — and that distinction is the whole point, measured rather
# than assumed. The first version of these cases WAS generated from the list,
# and the merge gate's narrow-BOTH battery showed what that buys: narrowing the
# production set and the fixture list together made the case vanish along with
# the member, so five of seven narrowings passed a green suite. A case derived
# from the thing it is meant to pin is the self-referential shape this file
# warns about, one level further out than usual — it did not restate a constant,
# it INHERITED its own domain from it.
#
# So the sets are now pinned in THREE places that must agree (production, the
# enumeration, these rows), and every expectation below is BEHAVIOURAL — a
# finding or its absence at a measured line — never a restatement of the member.
_API_BODY_FLAG_CASES = [
    ("-f", "%s %s repos/o/r -f a=b" % (_G, _A)),
    ("-F", "%s %s repos/o/r -F a=b" % (_G, _A)),
    ("--field", "%s %s repos/o/r --field a=b" % (_G, _A)),
    ("--raw-field", "%s %s repos/o/r --raw-field a=b" % (_G, _A)),
    ("--input", "%s %s repos/o/r --input a=b" % (_G, _A)),
]
_API_METHOD_FLAG_CASES = [
    ("-X", "%s %s repos/o/r -X POST" % (_G, _A)),
    ("--method", "%s %s repos/o/r --method POST" % (_G, _A)),
]
# A text emitter in FRONT of the separator, so a finding can only come from the
# walk having SPLIT on that character — not from the operation being read as the
# head of the line, which would hold whether the member is in the set or not.
# The newline row reports on line 2 because the case IS two lines. Measured.
_SEPARATOR_CASES = [
    (";", "semi", "echo x ; %s %s" % (_V, _P), 1),
    ("|", "pipe", "echo x | %s %s" % (_V, _P), 1),
    ("&", "amp", "echo x & %s %s" % (_V, _P), 1),
    ("`", "backtick", "echo x ` %s %s" % (_V, _P), 1),
    # NOT `echo x ( …` / `echo x ) …`: both are SYNTAX ERRORS (measured,
    # `bash -n`), so a recognition expectation on them would freeze
    # over-detection as if it were the real behaviour. These two spellings are
    # the ones where the character genuinely separates a command: a subshell,
    # and a `case` arm.
    ("(", "oparen", "( %s %s )" % (_V, _P), 1),
    # `case a in a)` and not `case $x in a)`: with the subject unset the arm
    # never matches and the line runs NOTHING, which would pin a recognition
    # expectation on a line that performs nothing. Gate round 3 #3.
    (")", "cparen", "case a in a) %s %s ;; esac" % (_V, _P), 1),
    # NOT the two-physical-line spelling, which `scan_text` splits on itself
    # before `split_commands` is ever asked — MEASURED: that spelling stayed
    # green with the newline removed from the split test. The member is live
    # where a newline reaches the splitter INSIDE one logical line, which is a
    # nested command line carrying an ANSI-C escape.
    ("\n", "newline", "eval $'echo x\\n%s %s'" % (_V, _P), 1),
]
# Members whose case does NOT change answer when that member alone is removed
# from the production set, WITH THE MEASURED REASON. Each of these is reported
# by a SECOND, independent path — the clustered short-letter walk — so the set
# membership is defence in depth rather than the only route. MEASURED: with the
# flag removed from BOTH API sets the line is still reported, which is the whole
# evidence for the claim. Being covered twice is fine; not knowing which members
# those are is not, so the table is checked in BOTH directions and a member that
# starts depending must lose its entry here.
_REDUNDANT_MEMBERS = {
    ("forge API flag", "-f"): "clustered short-letter walk",
    ("forge API flag", "-F"): "clustered short-letter walk",
    ("forge API flag", "-X"): "clustered short-letter walk",
    # Three separators whose LINE is still reported with the member removed,
    # each reason measured rather than guessed. Their member-level binding is
    # the quote-naive split assertion above, which builds its own line from the
    # character and so cannot name one member while exercising another.
    ("command separator", "backtick"):
        "the quote-AWARE substitution branch lifts the body before the "
        "separator test is reached (measured: the aware split still separates "
        "it with the member gone)",
    ("command separator", "oparen"):
        "the segment's leading `(` is trimmed by the lead-trim, so the "
        "operation heads the segment anyway (measured)",
    ("command separator", "cparen"):
        "another pass of the same scan still reports the line (measured, and "
        "still true with `;` removed as well, so it is not the neighbouring "
        "separator carrying it)",
}
_EMITTER_CASES = [
    ("echo", 'echo "%s %s"' % (_V, _P)),
    ("printf", 'printf "%s %s"' % (_V, _P)),
    ("true", 'true "%s %s"' % (_V, _P)),
    ("false", 'false "%s %s"' % (_V, _P)),
]


def _set_member_positive_cases() -> list[tuple[str, list[str], int]]:
    """The recognition half: every member of a read-once set, at its site."""
    out = [("api-body-flag-%s" % flag.lstrip("-"), [line], 1)
           for flag, line in _API_BODY_FLAG_CASES]
    out += [("api-method-flag-%s" % flag.lstrip("-"), [line], 1)
            for flag, line in _API_METHOD_FLAG_CASES]
    out += [("separator-%s-splits" % name, [line], want)
            for _ch, name, line, want in _SEPARATOR_CASES]
    return out


# Every way the naive separator search can see a pattern the quoting model
# reads as EMPTY: a run of balanced empty spans followed by one UNTERMINATED
# opener. MEASURED over the whole cross product below, on four shells: bash
# 3.2.57, zsh 5.9 and dash all reject the line outright (unexpected EOF /
# unmatched / unterminated quoted string) and ksh93u+ parses each one and
# substitutes nothing, leaving the parameter's value. So no measured shell runs
# any of them, and every one must stay clean.
_EMPTY_PATTERN_PREFIXES = [("bare", ""), ("dq-empty", '""'), ("sq-empty", "''")]
_EMPTY_PATTERN_OPENERS = [("dq", '"'), ("sq", "'"), ("ansi-c", "$'"),
                          ("locale", '$"')]


def _empty_pattern_negative_cases() -> list[tuple[str, list[str]]]:
    return [("expansion-naive-empty-pattern-%s-%s" % (pname, oname),
             ["%s ${x/%s%s/%s}" % (_V, prefix, opener, _P)])
            for pname, prefix in _EMPTY_PATTERN_PREFIXES
            for oname, opener in _EMPTY_PATTERN_OPENERS]


# The separator space between a keyword and its value, GENERATED from the
# independent whitespace oracle rather than sampled. `_ssh_option_pair`'s
# grammar is `<ws>* keyword <ws>* [ '=' <ws>* ] value`, so the separator is any
# non-empty word over {ws, '='} of that shape; the product below is every such
# word using ONE whitespace character per position, plus the doubled-whitespace
# spelling and the bare `=`. AMENDED: an earlier comment here said "EVERY
# spelling", which was false — this is the finite product just described and it
# omits, for example, a separator MIXING two different whitespace characters
# around the `=` (measured accepted: CR on both sides of it). What the product
# does guarantee, and what the pin in `_tables_are_pinned` enforces, is that
# EVERY MEMBER of the whitespace set is exercised at EVERY position the code
# consumes one — before the keyword, between keyword and `=`, and after `=`.
# That is the property four rounds of this gate kept finding missing.
#
# Four rounds each found one more member of a space, and the lesson was
# recorded there: enumerate the space, do not append the case. (name,
# separator, needs ANSI-C quoting to be written on one line).
_WS_NAMES = {" ": "sp", "\t": "tab", "\r": "cr", "\n": "nl"}


def _ssh_separator_spellings() -> list[tuple[str, str, bool]]:
    out = [("equals", "=", False)]
    for ws in _SSH_SEPARATOR_WS:
        wname = _WS_NAMES.get(ws, "ws%d" % ord(ws))
        ansi = ws not in " "
        out.append(("%s" % wname, ws, ansi))
        out.append(("%s-%s" % (wname, wname), ws + ws, ansi))
        out.append(("%s-equals" % wname, ws + "=", ansi))
        out.append(("equals-%s" % wname, "=" + ws, ansi))
        out.append(("%s-equals-%s" % (wname, wname), ws + "=" + ws, ansi))
    return out


_SSH_SEPARATORS = _ssh_separator_spellings()

# NOT separators, and that is the whole point of `SSH_SEPARATOR_WS`: Python's
# `str.isspace()` accepts both and OpenSSH accepts neither, so a keyword run
# together with a command by one of these is not a command-bearing option at
# all. Reading them as separators would manufacture a command line the tool
# never runs — the guard measured that as a false refusal on its side.
_SSH_NON_SEPARATORS = [("vt", "\v"), ("ff", "\f")]
# ssh_config keywords that carry no command. A value that LOOKS like one here
# must still be nothing.
_SSH_PLAIN_KEYWORDS = ["port", "user", "identityfile", "proxyjump"]


def _ansi_c_line(text: str) -> str:
    """`text` as a single-line ANSI-C quoted word, control characters escaped.

    Only for fixtures: a raw control character inside a fixture line would be
    invisible in every viewer, which is the class of hazard this file's own
    header warns about for the NUL byte."""
    body = text.replace("\\", "\\\\").replace("'", "\\'")
    for raw, esc in (("\t", "\\t"), ("\r", "\\r"), ("\v", "\\v"),
                     ("\f", "\\f"), ("\n", "\\n")):
        body = body.replace(raw, esc)
    return "$'%s'" % body


def _ssh_operand(keyword: str, sep: str, cmd: str, ansi: bool) -> str:
    """One `-o` operand as it is written on a line, quoted so it stays ONE
    argv token."""
    raw = "%s%s%s" % (keyword, sep, cmd)
    return _ansi_c_line(raw) if ansi else "'%s'" % raw


# The operand may OPEN with whitespace — a configuration line's ordinary
# indentation, accepted on `-o` too. MEASURED with `ssh -G` on OpenSSH 9.9p2:
# a leading space, tab, CR and newline each resolve to the same keyword and
# value as the bare spelling. GENERATED from the same oracle as the separators,
# because that is the point of gate round 9 #3: a set can be covered at one
# consumption site and not at another, and only generating both axes from one
# list makes "every member, at every position" a property rather than a hope.
_SSH_KEYWORD_PREFIXES = (
    [(_WS_NAMES.get(ws, "ws%d" % ord(ws)), ws) for ws in _SSH_SEPARATOR_WS]
    + [("%s-x2" % _WS_NAMES.get(ws, "ws%d" % ord(ws)), ws + ws)
       for ws in _SSH_SEPARATOR_WS])


def _carrier_positive_cases() -> list[tuple[str, list[str], int]]:
    """The cross product of the command-bearing keywords with every separator
    spelling — all of them real, since ssh runs each of these four keywords'
    values through a shell."""
    cmd = "%s %s" % (_V, _P)
    out = [("carrier-ssh-%s-%s" % (keyword, sname),
            ["ssh -o %s host" % _ssh_operand(keyword, sep, cmd, ansi)], 1)
           for keyword in _SSH_CMD_KEYWORDS
           for sname, sep, ansi in _SSH_SEPARATORS]
    out += [("carrier-ssh-leading-%s-%s" % (pname, keyword),
             ["ssh -o %s host"
              % _ssh_operand(prefix + keyword, "=", cmd,
                             prefix.strip(" ") != "")], 1)
            for keyword in _SSH_CMD_KEYWORDS
            for pname, prefix in _SSH_KEYWORD_PREFIXES]
    # The ATTACHED long-option spelling, written with an escaped space rather
    # than quotes — which is the spelling nothing else here catches, since the
    # quoted-operand pass has no quoted span to read.
    out.append(("carrier-su-attached-long-command-option",
                ["su --command=%s\\ %s someone" % (_V, _P)], 1))
    # The SECOND command-bearing long option, which has no short spelling.
    out.append(("carrier-su-session-command",
                ["su --session-command=%s\\ %s someone" % (_V, _P)], 1))
    # A terminal option AFTER the destination is the remote command's argument
    # and must not suppress anything — the option region ended at the
    # destination, so the walk never sees it.
    out.append(("carrier-ssh-terminal-option-past-the-destination",
                ["ssh -o %s host -V"
                 % _ssh_operand("proxycommand", "=", "%s %s" % (_V, _P),
                                False)], 1))
    return out


def _carrier_negative_cases() -> list[tuple[str, list[str]]]:
    cmd = "%s %s" % (_V, _P)
    out = [("carrier-ssh-plain-keyword-%s" % keyword,
            ["ssh -o %s host" % _ssh_operand(keyword, "=", "/x/id_%s_%s"
                                             % (_V, _P), False)])
           for keyword in _SSH_PLAIN_KEYWORDS]
    # The DESTINATION rule, whole-line: past the destination the argv belongs
    # to the REMOTE command, so a `-o` there is that command's own argument.
    out.append(("carrier-ssh-option-after-the-destination",
                ["ssh host echo -o %s"
                 % _ssh_operand("proxycommand", "=", cmd, False)]))
    # `--` ends the options exactly, so what follows is the DESTINATION however
    # it is spelled. Measured with `ssh -G`: nothing is configured and the
    # option token becomes an invalid hostname.
    out.append(("carrier-ssh-double-dash-ends-the-options",
                ["ssh -- -o %s host"
                 % _ssh_operand("proxycommand", "=", cmd, False)]))
    # A TERMINAL option: the carrier prints something and exits, so whatever it
    # was also told to run never runs. Both orders — the one where the command
    # option comes FIRST is the one a `break` would get wrong.
    out.append(("carrier-ssh-terminal-option-before-the-command-option",
                ["ssh -V -o %s host"
                 % _ssh_operand("proxycommand", "=", cmd, False)]))
    out.append(("carrier-su-terminal-option-after-the-command-option",
                ["su -c %s\\ %s --help someone" % (_V, _P)]))
    return out


def _negative_cases() -> list[tuple[str, list[str]]]:
    return _carrier_negative_cases() + [
        ("status", ["%s status" % _V]),
        ("filename-lookalike", ["%s %s-dry-note.md" % (_V, _P)]),
        ("echoed", ["echo %s %s" % (_V, _P)]),
        ("echoed-quoted", ['echo "x; %s %s"' % (_V, _P)]),
        ("echoed-quoted-subshell", ["echo '$(%s %s)'" % (_V, _P)]),
        ("forge-view", ["%s %s view 1" % (_G, _R)]),
        ("api-read", ["%s %s repos/o/r" % (_G, _A)]),
        ("api-explicit-get", ["%s %s -X GET repos/o/r" % (_G, _A)]),
        ("api-attached-get", ["%s %s -XGET repos/o/r" % (_G, _A)]),
        ("api-jq", ["%s %s -q .name repos/o/r" % (_G, _A)]),
        ("api-header", ['%s %s -H "Accept: x" repos/o/r' % (_G, _A)]),
        ("local-branch-delete", ["%s branch -d x" % _V]),
        ("local-branch-force-delete", ["%s branch -D x" % _V]),
        ("dashed-local", ["%s-branch -d x" % _V]),
        ("nice-status", ["nice -n 5 %s status" % _V]),
        ("sudo-status", ["sudo -u root %s status" % _V]),
        ("timeout-status", ["timeout 5 %s status" % _V]),
        ("nohup-status", ["nohup %s status" % _V]),
        ("xargs-status", ["xargs -n 1 %s status" % _V]),
        ("sudo-host-long-option", ["sudo --host h %s status" % _V]),
        # `-h` consumes the next non-option token as the HOST, so here the VCS
        # name IS that host and the command is the bare subcommand — which
        # publishes nothing. Reading -h as a bare flag (the pre-round-2 policy)
        # makes this a finding, which is how this case guards the correction.
        ("sudo-host-consumes-the-vcs-name", ["sudo -h %s %s" % (_V, _P)]),
        # the newly-covered carriers must still be quiet on a read-only command
        ("builtin-status", ["builtin %s status" % _V]),
        ("ionice-status", ["ionice -c 2 -n 7 %s status" % _V]),
        ("exec-status", ["exec -a alias %s status" % _V]),
        ("time-status", ["time -o out %s status" % _V]),
        ("doas-status", ["doas -u root %s status" % _V]),
        ("work-tree-status", ["%s --work-tree /tmp status" % _V]),
        ("forge-repo-view", ["%s -R o/r %s view 1" % (_G, _R)]),
        # -S's string is the HEAD of the argv; the operands after it are its
        # arguments, so this executes the text-emitter, not the VCS
        ("env-split-string-echo",
         ['env -S "echo" %s %s' % (_V, _P)]),
        # …and the same when the operand is ATTACHED or clustered: the split
        # string is still the HEAD of the argv, so this executes the emitter
        ("env-split-attached-echo", ["env -Secho %s %s" % (_V, _P)]),
        ("env-split-clustered-echo", ["env -vSecho %s %s" % (_V, _P)]),
        # -C eats the rest of the cluster: no split string, and a read-only
        # subcommand behind it stays clean
        ("env-chdir-cluster-is-not-a-split", ["env -CSx %s status" % _V]),
        # The FIRST operand-taking letter of a cluster wins, and the rest of the
        # token is its VALUE, never further flags. These must stay clean or the
        # walk has started splitting on every letter it recognises.
        #   -i takes the buffering mode, so the mode here is "o" and the
        #   emitter is the program — the real tool rejects the mode and runs
        #   nothing at all
        ("stdbuf-first-letter-eats-the-second",
         ["stdbuf -ie echo %s %s" % (_V, _P)]),
        #   -a takes the auth type, so "u" is the type and the emitter is the
        #   program
        ("sudo-first-letter-eats-the-second",
         ["sudo -au echo %s %s" % (_V, _P)]),
        #   the carrier's cluster is all no-operand letters: it consumes
        #   NOTHING, so the emitter behind it is the program
        ("carrier-cluster-of-bare-flags-consumes-nothing",
         ["xargs -rt echo %s %s" % (_V, _P)]),
        ("env-cluster-of-bare-flags-consumes-nothing",
         ["env -iv echo %s %s" % (_V, _P)]),
        #   an ATTACHED operand is one token and consumes nothing extra
        ("carrier-cluster-attached-operand-consumes-nothing",
         ["xargs -tn5 echo %s %s" % (_V, _P)]),
        # The forge API's jq flag takes an operand, so in this cluster "X" is
        # the QUERY and there is no method flag at all. Observed on forge CLI
        # 2.96: it rejects the call with "accepts 1 arg(s), received 2".
        ("api-jq-cluster-eats-the-method-letter",
         ["%s %s -qX POST repos/o/r/x" % (_G, _A)]),
        ("api-template-cluster-eats-the-body-letter",
         ["%s %s -tf state=closed repos/o/r/x" % (_G, _A)]),
        # a clustered GET is still a GET
        ("api-method-clustered-get",
         ["%s %s -iXGET repos/o/r/x" % (_G, _A)]),
        # round-5 finding 3: an OPTIONAL-operand letter takes an attached
        # remainder and NEVER the following token, so the emitter behind it is
        # the program. Observed on GNU findutils 4.10: `xargs -lE …` answers
        # `invalid number "E" for -l option` and runs nothing at all, while
        # `xargs -teX echo FOO` traces `echo FOO hi`. Reading the trailing
        # letter as a mandatory -E would report a command that never executes.
        ("xargs-optional-letter-eats-the-mandatory-letter",
         ["xargs -lE echo %s %s" % (_V, _P)]),
        ("xargs-optional-replace-attached",
         ["xargs -iX echo %s %s" % (_V, _P)]),
        ("xargs-optional-eof-attached",
         ["xargs -eX echo %s %s" % (_V, _P)]),
        # round-5 finding 2, the other direction: what follows the script is $0
        # and the positional parameters, so the option operand is not a script
        # and the words after the script are not commands
        ("shell-c-option-operand-is-not-the-script",
         ["bash -c -o xtrace 'echo hi' %s %s" % (_V, _P)]),
        ("shell-clustered-option-operand-is-not-the-script",
         ["bash -oc %s 'true' %s" % (_V, _P)]),
        # round-6 finding 1, the other direction: the SAME spellings on the
        # shell whose arity differs, each observed NOT to run the escaped
        # command. bash's `-O` and `-o` take the FOLLOWING token, which here is
        # the `-c` itself ("invalid shell option name -c" / "-c: invalid option
        # name"), so those invocations have no script at all; bash's and zsh's
        # `-T` is bare, so the script is the mask word "0" and the command is
        # only $0; and on zsh `-oc` is `-o` with the option name "c", so there
        # is no command flag ("no such option: c"). A one-model parser cannot
        # hold these AND the positives above at the same time.
        ("shell-bash-shopt-letter-eats-the-command-flag",
         ["bash -O -c %s\\ %s" % (_V, _P)]),
        ("shell-bash-attached-option-name-is-a-cluster",
         ["bash -oerrexit -c %s\\ %s" % (_V, _P)]),
        ("shell-dash-attached-option-name-is-a-cluster",
         ["dash -oerrexit -c %s\\ %s" % (_V, _P)]),
        ("shell-bash-mask-letter-is-bare",
         ["bash -c -T 0 %s\\ %s" % (_V, _P)]),
        ("shell-zsh-mask-letter-is-bare",
         ["zsh -c -T 0 %s\\ %s" % (_V, _P)]),
        ("shell-zsh-attached-operand-eats-the-command-flag",
         ["zsh -oc errexit %s\\ %s" % (_V, _P)]),
        # without a `-c` the first operand is a script FILE, not a command
        # line, on bash / dash / zsh — measured: each answers "No such file or
        # directory" / "cannot open" / "can't open input file" and executes
        # nothing. ksh93 is the one measured model that does NOT do this, and
        # its positives sit in the positive set above; keeping these three here
        # is what stops the first-operand flag from being applied model-blind.
        ("shell-no-command-flag-has-no-script",
         ["bash -x %s\\ %s" % (_V, _P)]),
        ("shell-bash-bare-first-operand-is-a-script-file",
         ["bash %s\\ %s" % (_V, _P)]),
        ("shell-dash-bare-first-operand-is-a-script-file",
         ["dash %s\\ %s" % (_V, _P)]),
        ("shell-zsh-bare-first-operand-is-a-script-file",
         ["zsh %s\\ %s" % (_V, _P)]),
        ("shell-bash-first-operand-after-terminator-is-a-script-file",
         ["bash -- %s\\ %s" % (_V, _P)]),
        ("shell-zsh-first-operand-after-bare-plus-is-a-script-file",
         ["zsh + %s\\ %s" % (_V, _P)]),
        # round-8, the other direction: on zsh a bare `+` ENDS options, so the
        # `-c` behind it is the script FILE and the escaped command never runs
        # (measured: "command not found: vdb", i.e. zsh read `-c` as the file).
        # A bare `-` ends options on every measured shell too — but only on the
        # three whose first operand is a FILE does that mean nothing runs. The
        # ksh spellings of these are POSITIVES (above), because there the token
        # behind the introducer is executed as a command line.
        ("shell-zsh-bare-plus-ends-options",
         ["zsh + -c %s\\ %s" % (_V, _P)]),
        ("shell-bare-dash-ends-options",
         ["bash - -c %s\\ %s" % (_V, _P)]),
        # round-9, the other direction: bash/dash/zsh all take the `-c` as
        # -o's mandatory operand and run nothing; zsh rejects every dashed `+`
        # token longer than `+-`, and bash/dash reject them all.
        ("shell-bash-separate-operand-is-mandatory",
         ["bash -o -c %s\\ %s" % (_V, _P)]),
        ("shell-dash-separate-operand-is-mandatory",
         ["dash -o -c %s\\ %s" % (_V, _P)]),
        ("shell-zsh-separate-operand-is-mandatory",
         ["zsh -o -c %s\\ %s" % (_V, _P)]),
        ("shell-zsh-plusdash-ends-options",
         ["zsh +- -c %s\\ %s" % (_V, _P)]),
        ("shell-zsh-plusdash-lettered-is-rejected",
         ["zsh +-c %s\\ %s" % (_V, _P)]),
        ("shell-bash-plusdash-is-rejected",
         ["bash +- -c %s\\ %s" % (_V, _P)]),
        ("printf-text", ['printf "%s %s\\n"' % (_V, _P)]),
        ("echoed-single-quoted", ["echo '%s %s'" % (_V, _P)]),
        # a BARE parenthesis or bracket inside a text-emitter's argument is
        # literal: neither opens a command substitution
        ("echoed-parenthesised", ['echo "(%s %s)"' % (_V, _P)]),
        ("printf-parenthesised", ['printf "(%s %s)\\n"' % (_V, _P)]),
        ("echoed-bracketed", ["echo [%s %s]" % (_V, _P)]),
        # after a substitution closes, the REST of the string is quoted again,
        # so its `;` is literal text of the emitter's argument
        ("echoed-after-substitution",
         ['echo "$(true) x; %s %s"' % (_V, _P)]),
        # an UNQUOTED substitution likewise leaves the emitter intact: only the
        # body runs, the remaining words are printed
        ("echoed-after-unquoted-substitution",
         ["echo $(true) %s %s" % (_V, _P)]),
        ("echoed-after-backtick-substitution",
         ["echo `true` %s %s" % (_V, _P)]),
        ("xargs-optional-operand-then-emitter",
         ["xargs -l echo %s %s" % (_V, _P)]),
        ("xargs-mandatory-operand", ["xargs -I REPL %s status" % _V]),
        ("printf-single-quoted", ["printf '%s %s'" % (_V, _P)]),
        # after -c the script is ONE operand; what follows is $0 and the
        # positional parameters, so this runs the VCS with no subcommand.
        # These are also what fails if ksh93's operand JOIN is ever applied to
        # a real `-c`: joining here would manufacture the form out of $0 and
        # $1. Measured: `ksh -c 'echo A' ';' 'echo B'` prints only "A".
        ("shell-c-positional-parameters", ["sh -c %s %s" % (_V, _P)]),
        ("shell-ksh-c-positional-parameters", ["ksh -c %s %s" % (_V, _P)]),
        ("shell-bash-c-positional-parameters", ["bash -c %s %s" % (_V, _P)]),
        ("shell-ksh-c-script-does-not-absorb-its-operands",
         ["ksh -c true %s %s" % (_V, _P)]),
        # round-12, the other direction: an appended operand is a WORD, never
        # syntax, so a `;` handed to ksh93 as an operand does NOT start a new
        # command. Measured: `ksh 'echo A' ';' git --version` prints
        # "A ; git --version" — the emitter printed them and nothing ran.
        # A plain space-join reported this line, which was a FALSE POSITIVE;
        # quoting each appended operand is what makes the model exact in this
        # direction as well as the missing one.
        ("shell-ksh93-appended-punctuation-is-a-word-not-a-separator",
         ["ksh echo\\ A ';' %s %s" % (_V, _P)]),
        ("shell-ksh93-appended-separator-does-not-split-the-emitter",
         ["ksh echo\\ A '&&' %s %s" % (_V, _P)]),
        ("prose-vcs-without-subcommand",
         ["the %s repository is published by the daemon" % _V]),
        ("prose-vcs-and-word-in-separate-spans",
         ["the `%s` command and the `%s` mechanic" % (_V, _P)]),
        ("soft-wrap-benign",
         ["run `%s status` to check" % _V, "the worktree is clean"]),
        ("two-command-lines", ["%s status" % _V, "%s log" % _V]),
        # adjacent lines that are separate BLOCKS are not one soft-wrapped
        # sentence, and lines inside a fence are literal commands
        ("heading-then-paragraph",
         ["## %s" % _V, "%s mechanics are daemon-owned" % _P]),
        ("two-list-items",
         ["- %s" % _V, "- %s notifications are disabled" % _P]),
        ("two-numbered-items", ["1. %s" % _V, "2. %s notifications" % _P]),
        ("two-table-rows", ["| %s |" % _V, "| %s notifications |" % _P]),
        # block markers must be read THROUGH the blockquote, and two lines at
        # different quote depths are different blocks (round-18 finding 2)
        ("quoted-two-list-items",
         ["> - %s" % _V, "> - %s notifications are disabled" % _P]),
        ("quoted-two-numbered-items",
         ["> 1. %s" % _V, "> 2. %s notifications" % _P]),
        ("quoted-heading-then-paragraph",
         ["> ## %s" % _V, "> %s mechanics are daemon-owned" % _P]),
        ("quoted-two-table-rows",
         ["> | %s |" % _V, "> | %s notifications |" % _P]),
        ("blockquote-depth-mismatch",
         ["> %s" % _V, "%s notifications are disabled" % _P]),
        ("blockquote-depth-mismatch-nested",
         ["> > %s" % _V, "> %s notifications are disabled" % _P]),
        # a fence and a multi-line HTML comment are literal regions, and both
        # markers are read THROUGH the quoting (round-19 finding 3)
        ("quoted-fence-separate-lines",
         ["> ```", "> %s" % _V, "> %s notifications" % _P, "> ```"]),
        ("html-comment-multiline-separate-lines",
         ["<!--", _V, "%s notifications" % _P, "-->"]),
        ("quoted-html-comment-multiline",
         ["> <!--", "> %s" % _V, "> %s notifications" % _P, "> -->"]),
        ("fenced-separate-lines",
         ["```", _V, "%s notifications" % _P, "```"]),
        ("link-in-prose",
         ["see [the docs](https://x) and %s status" % _V]),
        ("prose", ["the daemon %ses the branch" % _P]),
        # an ESCAPED backslash ends the line: the next line is its own candidate
        ("escaped-backslash", ["%s \\\\" % _V, _P]),
        ("markdown-bullet-status", ["- %s status --porcelain" % _V]),
        ("markdown-numbered-view", ["1. %s %s view 1" % (_G, _R)]),
        ("markdown-blockquote-prose", ["> the lead requests the landing"]),
        ("markdown-checklist-clean", ["- [ ] worktree clean (%s status)" % _V]),
        ("markdown-heading-section", ['## §"Merge to main"']),
        ("shebang", ["#!/usr/bin/env bash"]),
        ("daemon-tool-names", ["%s.%s_branch {repo, branch, sha}" % (_V, _P)]),
        ("ls-remote", ['%s ls-remote origin "<branch>"' % _V]),
        ("fetch-merge", ["%s fetch origin && %s merge --no-ff x" % (_V, _V)]),
        ("yaml-run-clean", ["        run: python3 scripts/check-push-forms.py"]),
        ("prose-with-apostrophes",
         ["- **Branch fully published** — the lead's ref == the close-out's SHA"]),
        # ── the two new quote forms must not widen the false-positive surface ──
        # The text-emitter contract does not depend on how the word is spelled.
        ("ansi-c-echoed", ["echo $'%s %s'" % (_V, _P)]),
        ("locale-quote-echoed", ['echo $"%s %s"' % (_V, _P)]),
        # An escape this decoder does not know keeps its BACKSLASH, exactly as
        # bash does, so the word is not the subcommand.
        ("ansi-c-unknown-escape", ["%s $'\\q%s'" % (_V, _P[1:])]),
        # …and a decode that is simply a different word stays clean, which is
        # what proves the finding above comes from the DECODE and not from the
        # mere presence of a `$'…'` region.
        ("ansi-c-decodes-to-another-word",
         ["%s %s" % (_V, _ansi_c(_P[:3] + "l"))]),
        ("ansi-c-status", ["%s $'status'" % _V]),
        # `$` before an ordinary quote is not a quote form: `$(`, `${` and a
        # bare `$` all stay literal text.
        ("dollar-paren-is-not-a-quote", ["%s status # cost $(x) and ${y}" % _V]),
        ("bare-dollar-in-prose", ["the run costs $5 and the lead's call stands"]),
        # A backslash inside DOUBLE quotes is literal unless it precedes one of
        # the four characters bash treats specially there — reading it as an
        # unconditional escape is what corrupted a nested ANSI-C word.
        ("double-quote-backslash-is-literal",
         ['printf "%%s\\n" "a\\xb" && %s status' % _V]),
        # ---- the TWO-WORD families, in their harmless shapes ----------------
        # A family option that takes a SEPARATE operand consumes the word that
        # follows it, so an operand equal to the operation name is an operand
        # and the real operation is the token behind it.
        ("vcs-pair-long-option-operand-is-not-the-operation",
         ["%s %s --prefix %s split" % (_V, _SUB, _P)]),
        ("vcs-pair-short-option-operand-is-not-the-operation",
         ["%s %s -P %s split" % (_V, _SUB, _P)]),
        # Only the FIRST bare operand is the operation. A family operation this
        # table does not refuse ends the walk; a later token is an argument to
        # THAT operation and must not be read as an operation of its own.
        ("vcs-pair-stops-at-the-first-operand",
         ["%s %s add %s" % (_V, _SUB, _P)]),
        ("vcs-pair-read-only-operation",
         ["%s %s split --prefix=x" % (_V, _SUB)]),
        ("vcs-pair-operation-of-another-family",
         ["%s %s sync" % (_V, _P4)]),
        # each family's operation set is ITS OWN: another family's publishing
        # word is not an operation of this one, and the tool rejects it
        ("vcs-pair-operation-belongs-to-another-family",
         ["%s %s %s" % (_V, _P4, _DC)]),
        ("vcs-pair-hook-plumbing-is-not-another-family-operation",
         ["%s %s %s" % (_V, _SUB, _PP)]),
        # ---- the forge families, in their harmless shapes -------------------
        # Discussion state is not published code.
        ("forge-pr-comment", ["%s %s comment 1 --body x" % (_G, _R)]),
        ("forge-pr-lock", ["%s %s lock 1" % (_G, _R)]),
        # Creating a repository without the publishing flag publishes no code…
        ("forge-repo-create-without-the-flag",
         ["%s %s create x --private" % (_G, _REPO)]),
        # …and syncing with NO destination updates the LOCAL checkout only.
        ("forge-repo-sync-without-a-destination", ["%s %s sync" % (_G, _REPO)]),
        ("forge-repo-sync-flags-are-not-destinations",
         ["%s %s sync --force" % (_G, _REPO)]),
        # forking creates a remote repository but publishes none of this
        # checkout's code
        ("forge-repo-fork", ["%s %s fork owner/x" % (_G, _REPO)]),
        # a family action this table does not refuse ends the walk, and a later
        # word must not be read as the action
        ("forge-family-action-not-refused",
         ["%s %s view create" % (_G, _REL)]),
        # the text-emitter contract holds for the families too
        ("forge-family-echoed", ["echo %s %s create v1.0" % (_G, _REL)]),
        # ---- the INLINE ALIAS, in its harmless shapes -----------------------
        ("vcs-alias-to-a-read-only-subcommand",
         ["%s -c %sp=status p" % (_V, _AP)]),
        # a definition whose NAME is never invoked resolves nothing
        ("vcs-alias-name-not-invoked", ["%s -c %sq=%s p" % (_V, _AP, _P)]),
        # the value comes from the ENVIRONMENT here, not from the command line
        ("vcs-alias-from-the-environment",
         ["%s --config-env %sp=VAR p" % (_V, _AP)]),
        # a config key with no `=` defines nothing
        ("vcs-alias-not-an-assignment", ["%s -c %s%s p" % (_V, _AP, _P)]),
        # an empty value expands to no words at all
        ("vcs-alias-empty-value", ["%s -c %sp= p" % (_V, _AP)]),
        # the alias is POPPED as it resolves, so a self-referential definition
        # terminates instead of looping
        ("vcs-alias-self-referential", ["%s -c %sp=p p" % (_V, _AP)]),
        # a config key that is not in the alias section is just a setting
        ("vcs-alias-wrong-config-section",
         ["%s -c core.p=%s p" % (_V, _P)]),
        # The alias VALUE is NOT case-folded, and that is measured rather than
        # assumed: an upper-cased subcommand is "cannot handle … as a builtin"
        # and runs nothing, with or without an alias in front of it.
        ("vcs-alias-value-is-case-sensitive",
         ["%s -c %sp=%s p" % (_V, _AP, _P.upper())]),
        ("vcs-subcommand-is-case-sensitive", ["%s %s" % (_V, _P.upper())]),
        ("vcs-alias-echoed", ["echo %s -c %sp=%s p" % (_V, _AP, _P)]),
        # ---- a `${…}` that cannot produce the word --------------------------
        # A bare expansion names no literal at all — the same
        # variable-indirection boundary this gate documents for a program named
        # through a variable — and prefix REMOVAL yields a substring of the
        # PARAMETER, never of the pattern.
        ("expansion-bare-parameter", ["%s ${x} %s" % (_V, _P)]),
        ("expansion-prefix-removal", ["%s ${x#%s} status" % (_V, _P)]),
        ("expansion-suffix-removal", ["%s ${x%%%s} status" % (_V, _P)]),
        ("expansion-error-message", ["%s ${x:?%s} status" % (_V, _P)]),
        # a replacement with no second separator DELETES the pattern, so there
        # is no literal left to be a candidate
        ("expansion-replacement-with-no-replacement",
         ["%s ${x/%s}" % (_V, _P)]),
        # The EARLIEST operator decides, not the first one looked at: a removal
        # at the front makes the whole rest of the body its PATTERN, and a
        # value-producing operator sitting inside that pattern produces nothing.
        ("expansion-earliest-operator-decides",
         ["%s ${x#a:-%s} status" % (_V, _P)]),
        # An operator at position ZERO leaves no parameter name, which the
        # shell rejects as a bad substitution — it executes nothing, so there
        # is no candidate. (`${:-<publish>}` is NOT such a case and is a
        # finding: its `-` sits at index 1, behind the colon, so a value
        # operator really is present. The runtime guard reads it the same way.)
        ("expansion-with-no-parameter-name", ["%s ${-%s}" % (_V, _P)]),
        # ---- TERMINAL globals: the VCS prints and exits ---------------------
        # These two cases were POSITIVE until this pass, on the belief that a
        # bare attached-operand-only option is a lone flag whose subcommand is
        # still reached. Measured on 2.54.0, it is not: the exec-path global
        # prints the path and exits 0, and the super-prefix global is rejected
        # outright, that option having been removed. Nothing runs behind
        # either, so the word behind them is not a command — which is how the
        # runtime guard reads them, and the two now agree.
        ("vcs-terminal-exec-path",
         ["%s --exec-path %s origin main" % (_V, _P)]),
        ("vcs-terminal-super-prefix", ["%s --super-prefix %s" % (_V, _P)]),
        ("vcs-terminal-version", ["%s --version %s" % (_V, _P)]),
        ("vcs-terminal-help-short", ["%s -h %s" % (_V, _P)]),
        # …and a terminal global does not disarm the rest of the line: a
        # SEPARATE command after it still runs
        ("vcs-terminal-does-not-cover-the-next-command",
         ["%s --version && %s status" % (_V, _V)]),
        # ---- the raw API under an EXPLICIT GET ------------------------------
        # A field flag alone implies POST and IS a mutation, but under an
        # explicit GET the same flags are a query string — that CLI's own
        # documented search idiom, which this gate reported as a publish until
        # the whole option set was read before deciding.
        ("api-explicit-get-with-a-field",
         ["%s %s -X GET search/issues -f q=repo:foo" % (_G, _A)]),
        ("api-explicit-get-long-with-a-field",
         ["%s %s --method GET repos/o/r -f a=b" % (_G, _A)]),
        ("api-explicit-get-clustered-with-a-field",
         ["%s %s -i -X GET x -f q=1" % (_G, _A)]),
        ("api-explicit-get-with-an-input-body",
         ["%s %s --input body.json -X GET x" % (_G, _A)]),
        ("api-field-operand-is-not-a-method-flag-negative-twin",
         ["%s %s x -f a=b -X GET" % (_G, _A)]),
        ("api-explicit-get-attached-with-a-field",
         ["%s %s -XGET x -fa=b" % (_G, _A)]),
        # the method flag with no operand at all sets nothing
        ("api-method-flag-with-no-operand", ["%s %s x -X" % (_G, _A)]),
        # ---- the DASHED family executables, in their harmless shapes --------
        ("vcs-dashed-family-read-only", ["%s-%s status" % (_V, _LFS)]),
        ("vcs-dashed-family-option-operand-is-not-the-operation",
         ["%s-%s --prefix %s split" % (_V, _SUB, _P)]),
        ("vcs-dashed-family-alone", ["%s-%s" % (_V, _LFS)]),
        ("vcs-dashed-family-echoed",
         ["echo %s-%s %s" % (_V, _LFS, _P)]),
        # ---- round-1 gate findings, the harmless side -----------------------
        # With no UNESCAPED second separator there is no replacement section at
        # all: the publishing word is inside the PATTERN and never survives.
        ("expansion-escaped-separator-leaves-no-replacement",
         ["%s ${x/foo\\/%s}" % (_V, _P)]),
        # A boolean flag carrying a false value publishes nothing.
        ("forge-repo-create-publishing-flag-set-false",
         ["%s %s create o/r --source=. --%s=false" % (_G, _REPO, _P)]),
        ("forge-repo-create-publishing-flag-set-zero",
         ["%s %s create o/r --%s=0" % (_G, _REPO, _P)]),
        # ---- round-2 gate findings, the harmless side ----------------------
        # the appended operands are the TEXT-EMITTER's arguments here
        ("vcs-alias-shell-value-appends-to-an-emitter",
         ["%s -c %sp=!echo p %s" % (_V, _AP, _P)]),
        # the escaped brace is part of the WORD, so the word is not the
        # publishing subcommand
        ("expansion-escaped-brace-is-part-of-the-word",
         ["%s ${x:+a\\}%s}" % (_V, _P)]),
        # …while an UNESCAPED one really does close the body, leaving the rest
        # of the token outside the expansion entirely
        ("expansion-unescaped-brace-closes-the-body",
         ["%s ${x/a}b/%s}" % (_V, _P)]),
        # …and a bare OPEN brace is ordinary text on the same reading, so the
        # first `}` still terminates and the replacement really is that one
        # character. MEASURED on bash 3.2.57 with x=a: argc=3, $1 = `{`. This is
        # the negative half of the round-8 pair — the fix must stop counting the
        # open brace WITHOUT starting to report the word behind the terminator.
        ("expansion-bare-open-brace-as-the-replacement",
         ["%s ${x/a/{} origin main" % _V]),
        # …and neither candidate publishing stays clean, so the branching is
        # not simply reporting everything it tries
        ("vcs-alias-no-candidate-publishes",
         ["%s -c %sa=status -c %sb=log ${x:+a}${y:+b}" % (_V, _AP, _AP)]),
        ("forge-subcommand-no-candidate-publishes",
         ["%s ${a:+%s}${b:+%s} view" % (_G, _R, _A)]),
        # Each alias candidate is resolved on its OWN COPY of the alias map,
        # because resolving one CONSUMES it: here the first candidate resolves
        # through the second, and a shared map would leave the second branch
        # asking for an alias that is no longer there.
        ("vcs-alias-candidate-branches-do-not-consume-each-other",
         ["%s -c %sa=b -c %sb=status ${x:+a}${y:+b}" % (_V, _AP, _AP)]),
        # ---- the guard's next four commits, the harmless side ---------------
        # A quoted brace is part of the WORD, so the word is not the publishing
        # subcommand. MEASURED: `x=1; ${x:+"a}<publish>"}` yields `a}<publish>`.
        ("expansion-quoted-brace-is-part-of-the-word",
         ["%s ${x:+\"a}%s\"}" % (_V, _P)]),
        # …and a quoted word under a REMOVAL operator still yields nothing: the
        # unescaping applies to the word, it does not promote the operator.
        ("expansion-quoted-word-under-a-removal-op",
         ["%s ${x#\"%s\"}" % (_V, _P)]),
        # Unioning the two separator readings is not "report whatever either
        # one finds": neither reading of this one yields the publishing word.
        ("expansion-quoted-separator-with-a-harmless-replacement",
         ["%s ${x/\"a/b\"/log}" % _V]),
        # The sync action's own option VALUE is not a destination: each of
        # these updates the LOCAL checkout and touches no remote. Until the
        # action's option grammar was modelled, all four were findings — and
        # the residual note claiming that cost was shared with the runtime rule
        # table had gone false, which is what the re-differential caught.
        ("forge-repo-sync-branch-option-value",
         ["%s %s sync --branch main" % (_G, _REPO)]),
        ("forge-repo-sync-source-option-value",
         ["%s %s sync --source owner/upstream" % (_G, _REPO)]),
        ("forge-repo-sync-short-branch-option-value",
         ["%s %s sync -b main" % (_G, _REPO)]),
        ("forge-repo-sync-short-source-option-value",
         ["%s %s sync -s owner/upstream" % (_G, _REPO)]),
        # …and with no destination at all there is nothing to publish to.
        ("forge-repo-sync-force-flag-alone",
         ["%s %s sync --force" % (_G, _REPO)]),
        # pflag LAST-WINS: a bare enable followed by an explicit false value
        # publishes nothing, which accumulating the enabled occurrences missed.
        ("forge-repo-create-publishing-flag-disabled-last",
         ["%s %s create o/r --source=. --%s --%s=false"
          % (_G, _REPO, _P, _P)]),
        # The executing-operand subcommands, with a harmless operand: the
        # runner is not itself a publish, so reporting one would be a finding
        # on an ordinary rewrite.
        ("vcs-submodule-runner-harmless-operand",
         ["%s submodule foreach 'echo hi'" % _V]),
        ("vcs-bisect-runner-harmless-operand",
         ["%s bisect run make test" % _V]),
        ("vcs-rebase-exec-harmless-operand",
         ["%s rebase --exec 'make test' main" % _V]),
        # …and the history-rewrite filter whose operand is a DIRECTORY rather
        # than a command line is deliberately outside the runner set: listing
        # it would refuse an ordinary rewrite.
        ("vcs-history-rewrite-directory-filter",
         ["%s filter-branch --subdirectory-filter sub HEAD" % _V]),
        # the text-emitter contract still holds at the head of such a line
        ("vcs-submodule-runner-echoed",
         ["echo %s submodule foreach '%s %s'" % (_V, _V, _P)]),
        # ---- gate rounds 4-7, the harmless side -----------------------------
        # The naive separator reading's ONE artefact, GENERATED over its space
        # rather than written one case at a time. The separator lands inside an
        # UNTERMINATED quoted span, so everything before it unescapes to
        # nothing and the pattern is empty. Three successive gate rounds each
        # found one more member of this space by hand — first the two raw
        # openers, then the other two the quoting model knows, then a composite
        # of a balanced-empty span in front of an opener — which is the signal
        # to enumerate it instead. See `_empty_pattern_negative_cases`.
        ("vcs-family-with-no-operation", ["%s %s" % (_V, _LFS)]),
        # a family name is not a publishing subcommand on its own, and the
        # summary-only request subcommand is deliberately absent from the table
        ("vcs-summary-only-subcommand",
         ["%s request-pull v1.0 origin" % _V]),
        # the text-emitter contract holds for the two-word form too
        ("vcs-pair-echoed", ["echo %s %s %s" % (_V, _SUB, _P)]),
    ] + _empty_pattern_negative_cases() + _set_member_negative_cases()


def _set_member_negative_cases() -> list[tuple[str, list[str]]]:
    """The restraint half of the same three sets.

    Each fails if its member is dropped: a program that emits text rather than
    running it stops being exempt, and the quoted mention it carries becomes a
    false finding. The API read case is the control for the two flag families —
    it proves the flags are what produce those findings, not the subcommand.
    """
    out = [("text-emitter-%s-quoted-mention" % name, [line])
           for name, line in _EMITTER_CASES]
    out.append(("api-read-with-no-body-or-method-flag",
                ["%s %s repos/o/r" % (_G, _A)]))
    out.append(("api-explicit-GET-method", ["%s %s repos/o/r -X GET" % (_G, _A)]))
    return out


def _parser_cases() -> list[tuple[str, list[str], list[str], list[str], str]]:
    """(name, tokens, expected findings, expected nested command lines,
    expected program basename).

    These pin the CARRIER PARSE itself. The whole-line fixtures above are
    unioned over several readings, so a carrier rule can be broken while a
    fallback reading still finds the same form — a test that passes with its
    own fix reverted. `analyze` is single-reading, and the expected PROGRAM is
    asserted too, so a rule that merely stops the parse at the wrong token is
    caught even when the prose pass would still report the form.
    """
    pub = "%s %s" % (_V, _P)
    merge = "%s %s merge" % (_G, _R)
    api_method = "%s %s (non-GET method)" % (_G, _A)
    api_body = "%s %s (request body)" % (_G, _A)
    return [
        # the `--` option terminator is not a program
        ("option-terminator-dropped", ["--", _V, _P], [pub], [], _V),
        # eval concatenates its operands into one command line
        ("eval-collects-operands", ["eval", "--", pub], [], ["-- " + pub], ""),
        # -S is spliced back into env's OWN argv (it may inject env options),
        # and the operands after it are the command's arguments
        ("env-split-resplices-env", ["env", "-S", "-i " + pub], [],
         ["env -i " + pub], ""),
        ("env-split-keeps-trailing-as-args", ["env", "-S", "echo", _V, _P], [],
         ["env echo " + pub], ""),
        # the operand may be ATTACHED to -S, and short options cluster ahead of
        # it; the first operand-taking letter eats the rest of the token, so -u
        # and -C clusters are NOT splits
        ("env-split-attached-operand", ["env", "-S" + _V, _P], [],
         ["env %s %s" % (_V, _P)], ""),
        ("env-split-clustered-operand", ["env", "-vS" + _V, _P], [],
         ["env %s %s" % (_V, _P)], ""),
        ("env-unset-cluster-is-not-a-split",
         ["env", "-uS" + _V, _V, _P], [pub], [], _V),
        ("env-chdir-cluster-is-not-a-split",
         ["env", "-CSx", _V, _P], [pub], [], _V),
        # an optional-operand flag consumes NOTHING; a mandatory one takes the
        # next token; timeout's duration is a positional
        ("env-optional-operand-flag-consumes-nothing",
         ["env", "--block-signal", _V, _P], [pub], [], _V),
        ("env-argv0-consumes-its-value", ["env", "-a", "alias", _V, _P],
         [pub], [], _V),
        ("nice-value-option", ["nice", "-n", "5", _V, _P], [pub], [], _V),
        ("timeout-positional-duration", ["timeout", "5", _V, _P], [pub], [], _V),
        # the -c script is the first OPERAND: options and `--` may precede it,
        # and what FOLLOWS it is $0 and the positional parameters
        ("shell-c-skips-options", ["bash", "-c", "-e", pub], [], [pub], "bash"),
        ("shell-c-option-terminator", ["bash", "-c", "--", pub], [], [pub],
         "bash"),
        # after `--` the next token IS the script even when it looks like an
        # option — which is why the terminator is handled, not just skipped
        ("shell-c-terminator-before-dashed-script",
         ["bash", "-c", "--", "-x " + pub], [], ["-x " + pub], "bash"),
        ("shell-c-script-is-one-operand", ["sh", "-c", _V, _P], [], [_V], "sh"),
        # optional-operand carrier options swallow NOTHING
        ("xargs-optional-operand-consumes-nothing",
         ["xargs", "-i", _V, _P], [pub], [], _V),
        # the operand must NOT be punctuation: `{}` is discarded as
        # punctuation anyway, which would make this case pass with the arity
        # fix reverted
        ("xargs-mandatory-operand-consumes-one",
         ["xargs", "-I", "REPL", _V, _P], [pub], [], _V),
        ("xargs-lowercase-l-consumes-nothing",
         ["xargs", "-l", "echo", _V, _P], [], [], "echo"),
        # ---- the short-option CLUSTER walk, per carrier ------------------
        # The operand-taking letter ENDS the cluster, so its operand is the
        # NEXT token. The expected PROGRAM is the assertion that carries these:
        # with the walk removed each one still reports the form through the
        # prose pass, but under the emitter — so a finding-only check passes
        # with the fix reverted. Each shape was observed to execute the program
        # behind it (printf/echo standing in).
        ("cluster-env-unset-takes-next",
         ["env", "-vu", "echo", _V, _P], [pub], [], _V),
        ("cluster-env-chdir-takes-next",
         ["env", "-vC", "echo", _V, _P], [pub], [], _V),
        ("cluster-env-utilpath-takes-next",
         ["env", "-vP", "echo", _V, _P], [pub], [], _V),
        ("cluster-xargs-eof-takes-next",
         ["xargs", "-tE", "echo", _V, _P], [pub], [], _V),
        ("cluster-xargs-replstr-takes-next",
         ["xargs", "-tJ", "echo", _V, _P], [pub], [], _V),
        ("cluster-time-output-takes-next",
         ["time", "-po", "echo", _V, _P], [pub], [], _V),
        ("cluster-exec-argv0-takes-next",
         ["exec", "-ca", "echo", _V, _P], [pub], [], _V),
        ("cluster-sudo-user-takes-next",
         ["sudo", "-nu", "echo", _V, _P], [pub], [], _V),
        ("cluster-doas-user-takes-next",
         ["doas", "-nu", "echo", _V, _P], [pub], [], _V),
        ("cluster-ionice-classdata-takes-next",
         ["ionice", "-tn", "echo", _V, _P], [pub], [], _V),
        ("cluster-timeout-signal-takes-next-then-duration",
         ["timeout", "-vs", "echo", "5", _V, _P], [pub], [], _V),
        # …and the three ways a cluster consumes NOTHING more: the letter takes
        # its operand from inside the token, no letter takes one at all, or the
        # first operand-taking letter has already eaten the rest of the token.
        ("cluster-attached-operand-consumes-nothing",
         ["xargs", "-tn5", "echo", _V, _P], [], [], "echo"),
        ("cluster-of-bare-flags-consumes-nothing",
         ["xargs", "-rt", "echo", _V, _P], [], [], "echo"),
        ("cluster-first-value-letter-eats-the-rest",
         ["stdbuf", "-ie", "echo", _V, _P], [], [], "echo"),
        ("cluster-sudo-first-value-letter-eats-the-rest",
         ["sudo", "-au", "echo", _V, _P], [], [], "echo"),
        # ---- the same walk on the forge API's flags -----------------------
        ("api-cluster-method-separate",
         [_G, _A, "-iX", "POST", "repos/o/r/x"], [api_method], [], _G),
        ("api-cluster-method-attached",
         [_G, _A, "-iXPOST", "repos/o/r/x"], [api_method], [], _G),
        ("api-cluster-body-separate",
         [_G, _A, "-iF", "a=b", "repos/o/r/x"], [api_body], [], _G),
        ("api-cluster-body-attached",
         [_G, _A, "-ifa=b", "repos/o/r/x"], [api_body], [], _G),
        # the jq letter eats the method letter, so there is no method flag —
        # and the operand it consumed must not be re-read as one either
        ("api-cluster-jq-eats-the-method-letter",
         [_G, _A, "-qX", "POST", "repos/o/r/x"], [], [], _G),
        ("api-cluster-get-is-not-a-mutation",
         [_G, _A, "-iXGET", "repos/o/r/x"], [], [], _G),
        # a cluster ahead of the forge SUBCOMMAND consumes its operand, so the
        # subcommand behind it is still the one that is read
        ("forge-cluster-global-repo-takes-next",
         [_G, "-R", "o/r", _R, "merge", "1"], [merge], [], _G),
        ("forge-cluster-global-repo-attached",
         [_G, "-Ro/r", _R, "merge", "1"], [merge], [], _G),
        # ---- round-5: OPTIONAL-operand letters (attached remainder only) ----
        # The letter terminates the cluster, so the mandatory letter behind it
        # is its VALUE and the following token is NOT consumed — which leaves
        # the emitter as the program. Assert the program: with the optional
        # category removed the form is still reported (under the emitter's
        # operand), so a finding-only check would pass.
        ("optional-letter-eats-the-mandatory-letter",
         ["xargs", "-lE", "echo", _V, _P], [], [], "echo"),
        ("optional-letter-attached-replace",
         ["xargs", "-iX", "echo", _V, _P], [], [], "echo"),
        ("optional-letter-attached-eof",
         ["xargs", "-eX", "echo", _V, _P], [], [], "echo"),
        ("optional-letter-alone-consumes-nothing",
         ["xargs", "-l", "echo", _V, _P], [], [], "echo"),
        # …and the mandatory letters must be untouched by that category
        ("mandatory-letter-still-takes-next",
         ["xargs", "-tE", "echo", _V, _P], [pub], [], _V),
        ("mandatory-letter-attached-consumes-nothing",
         ["xargs", "-EX", "echo", _V, _P], [], [], "echo"),
        # ---- round-5: the shells' own invocation options ------------------
        # The nested command is the SCRIPT, not an option's operand. Asserting
        # the nested string is what carries these: the scan-forward heuristic
        # returned the operand instead, which is a silent miss.
        ("shell-c-then-operand-option",
         ["bash", "-c", "-o", "xtrace", pub], [], [pub], "bash"),
        ("shell-clustered-operand-option",
         ["bash", "-oc", "xtrace", pub], [], [pub], "bash"),
        ("shell-clustered-shopt-option",
         ["bash", "-Oc", "extglob", pub], [], [pub], "bash"),
        ("shell-plus-form-before-c",
         ["bash", "+o", "xtrace", "-c", pub], [], [pub], "bash"),
        ("shell-plus-form-after-c",
         ["bash", "-c", "+o", "xtrace", pub], [], [pub], "bash"),
        ("shell-long-value-option-before-c",
         ["bash", "--rcfile", "/dev/null", "-c", pub], [], [pub], "bash"),
        ("shell-long-value-option-after-c",
         ["bash", "-c", "--init-file", "/dev/null", pub], [], [pub], "bash"),
        # two operand-taking letters in one cluster consume two tokens
        ("shell-two-operand-letters-in-one-cluster",
         ["bash", "-ooc", "xtrace", "posix", pub], [], [pub], "bash"),
        # the option operand is NOT the script, and what follows the script is
        # $0 and the positional parameters
        ("shell-option-operand-is-not-the-script",
         ["bash", "-c", "-o", "xtrace", "echo hi", _V, _P], [], ["echo hi"],
         "bash"),
        # `-c` is not an operand-taking letter: it must not swallow the script
        ("shell-command-letter-consumes-nothing",
         ["bash", "-c", pub], [], [pub], "bash"),
        # ---- round-6: the four shells' arities DIVERGE ---------------------
        # Each pair is the same spelling on two shells with opposite answers,
        # so no single arity model can satisfy both halves. Every line was
        # observed on this host with `printf SENTINEL` as the script.
        #   zsh's -O is bare and the script runs; bash's -O eats the `-c`
        #   itself ("invalid shell option name -c") and nothing runs at all.
        ("shell-zsh-shopt-letter-is-bare",
         ["zsh", "-O", "-c", pub], [], [pub], "zsh"),
        ("shell-bash-shopt-letter-eats-the-command-flag",
         ["bash", "-O", "-c", pub], [], [], "bash"),
        #   zsh/ksh take an ATTACHED option name; bash/dash read the remainder
        #   as further bare letters and take the FOLLOWING token, which is the
        #   `-c`, so those two invocations have no script.
        ("shell-zsh-attached-option-name",
         ["zsh", "-oerrexit", "-c", pub], [], [pub], "zsh"),
        ("shell-ksh-attached-option-name",
         ["ksh", "-oerrexit", "-c", pub], [], [pub], "ksh"),
        ("shell-bash-attached-option-name-is-a-cluster",
         ["bash", "-oerrexit", "-c", pub], [], [], "bash"),
        ("shell-dash-attached-option-name-is-a-cluster",
         ["dash", "-oerrexit", "-c", pub], [], [], "dash"),
        #   …and an attached operand ENDS the cluster, so on zsh and ksh the
        #   `c` of `-oc` is the option NAME and not the command flag, while on
        #   bash and dash the same token is `-o <next>` plus a real `-c`.
        ("shell-zsh-attached-operand-eats-the-command-flag",
         ["zsh", "-oc", "errexit", pub], [], [], "zsh"),
        ("shell-bash-cluster-reaches-the-command-flag",
         ["bash", "-oc", "errexit", pub], [], [pub], "bash"),
        #   ksh93's -T takes a mandatory mask, attached or separate; bash's and
        #   zsh's -T is bare, so there the script is the mask word itself and
        #   the command behind it is only $0.
        #   The NAME `ksh` is a union of the measured ksh93u+ map and the
        #   minimal POSIX one, so a separate mask operand yields BOTH readings:
        #   ksh93 skips the mask and the script is <pub>, while a ksh whose -T
        #   is bare runs the mask word itself. Asserting both, in model order,
        #   is what fails if the union is dropped or collapsed.
        ("shell-ksh-mask-takes-an-operand",
         ["ksh", "-c", "-T", "0", pub], [], [pub, "0"], "ksh"),
        #   …an ATTACHED mask is one token under both readings, so there is one
        #   candidate and it is the script.
        ("shell-ksh-mask-attached-operand",
         ["ksh", "-c", "-T0", pub], [], [pub], "ksh"),
        ("shell-bash-mask-letter-is-bare",
         ["bash", "-c", "-T", "0", pub], [], ["0"], "bash"),
        ("shell-zsh-mask-letter-is-bare",
         ["zsh", "-c", "-T", "0", pub], [], ["0"], "zsh"),
        #   ksh93's -R consumes its scriptname (its own getopt string says
        #   `R:`, and `ksh -c -R <script>` answers "-c requires argument"),
        #   while no other MEASURED model takes an operand for it — zsh
        #   accepts `-R` as a bare option (`zsh -R -c <script>` runs
        #   <script>), and bash and dash reject it outright.
        ("shell-ksh-xref-takes-an-operand",
         ["ksh", "-c", "-R", "x", pub], [], [pub, "x"], "ksh"),
        ("shell-bash-xref-letter-is-bare",
         ["bash", "-c", "-R", "x", pub], [], ["x"], "bash"),
        #   Without a `-c` the first operand is a script FILE on bash, dash and
        #   zsh — whatever options precede it — so there is nothing to scan…
        ("shell-no-command-flag-has-no-script",
         ["bash", "-x", pub, _V, _P], [], [], "bash"),
        ("shell-zsh-no-command-flag-has-no-script",
         ["zsh", "-x", pub], [], [], "zsh"),
        ("shell-dash-no-command-flag-has-no-script",
         ["dash", "-x", pub], [], [], "dash"),
        #   …and on ksh93 it is NOT: the file open fails and the operand TEXT
        #   is executed, so every one of these needs no `-c` and no option
        #   spelling to run. Each was observed to execute `printf SCRIPT` on
        #   ksh93u+; the `ksh` union's dash member finds nothing in any of
        #   them, so the ksh93 reading alone is what makes them findings.
        ("shell-ksh-first-operand-is-a-command",
         ["ksh", pub], [], [pub], "ksh"),
        ("shell-ksh-first-operand-behind-a-flag",
         ["ksh", "-x", pub], [], [pub], "ksh"),
        ("shell-ksh-attached-option-name-then-first-operand",
         ["ksh", "-oc", pub], [], [pub], "ksh"),
        ("shell-ksh-separate-option-name-then-first-operand",
         ["ksh", "-o", "c", pub], [], [pub], "ksh"),
        ("shell-ksh-plus-attached-option-name-then-first-operand",
         ["ksh", "+oc", pub], [], [pub], "ksh"),
        ("shell-ksh-dashed-plus-cluster-then-first-operand",
         ["ksh", "+-xoc", pub], [], [pub], "ksh"),
        ("shell-ksh-first-operand-after-terminator",
         ["ksh", "--", pub], [], [pub], "ksh"),
        #   …and after a terminator the `-c` itself HEADS that command line —
        #   measured: `ksh -- -c <cmd>` answers "-c: not found", so `-c` is the
        #   command and <cmd> is an ARGUMENT to it, never a command of its own.
        #   The candidate is therefore the whole joined line, and the leading
        #   "-c" is what fails if the flag is applied to the wrong token.
        ("shell-ksh-terminated-command-flag-is-the-command",
         ["ksh", "--", "-c", pub], [], ["-c '%s'" % pub], "ksh"),
        #   The `sh` NAME unions ksh93, and ksh93 keeps this behaviour when it
        #   IS /bin/sh — observed through a symlink named `sh`, which really
        #   ran `sh 'git --version'`. So the union carries the reading for the
        #   `sh` spelling too; the other three members find nothing here.
        ("shell-sh-union-first-operand-is-a-command",
         ["sh", "-x", pub], [], [pub], "sh"),
        #   …and the operands BEHIND the first one are part of that command
        #   line, so the candidate is the JOIN, asserted as an exact string.
        #   `ksh X=1 <vcs> <publish>` really publishes (measured with
        #   `--version` in place of the form); resolving only args[idx] gives
        #   "X=1" and finds nothing, which is the miss this closes.
        ("shell-ksh-appended-operands-join-the-command-line",
         ["ksh", "X=1", _V, _P], [], ["X=1 %s %s" % (_V, _P)], "ksh"),
        ("shell-sh-union-appended-operands-join-the-command-line",
         ["sh", "X=1", _V, _P], [], ["X=1 %s %s" % (_V, _P)], "sh"),
        #   …and each appended operand is ONE WORD, so it is re-serialized
        #   QUOTED. Asserting the exact string is what fails if the
        #   reconstruction ever splits an operand back into source: the nested
        #   `-c` script here must stay one token, or the form inside it is lost.
        ("shell-ksh-appended-operand-keeps-its-word-boundary",
         ["ksh", "sh -c", "%s %s" % (_V, _P)], [],
         ["sh -c '%s %s'" % (_V, _P)], "ksh"),
        ("shell-ksh-appended-spaced-option-value-keeps-its-boundary",
         ["ksh", "%s -C" % _V, "/tmp/no such", _P], [],
         ["%s -C '/tmp/no such' %s" % (_V, _P)], "ksh"),
        #   …a bare word needs no quotes and gets none, so the common shape
        #   stays byte-identical to the source spelling. This pins the SHAPE of
        #   the serialization, not a behavioural property: quoting every
        #   appended operand unconditionally instead was measured to change no
        #   answer at all, because `tokenize` discards quoting and `A=1` and
        #   `'A=1'` reduce to the same token VALUE (see the residual note at
        #   `_shell_scripts`). Minimal quoting is kept because it keeps the
        #   reconstruction readable and shorter, not because anything depends
        #   on it.
        ("shell-ksh-appended-bare-words-are-not-requoted",
         ["ksh", "X=1", _V, _P, "origin"], [],
         ["X=1 %s %s origin" % (_V, _P)], "ksh"),
        #   …while a real `-c` script is ONE token and what follows it is $0
        #   and the positional parameters, so nothing is joined there. Both
        #   halves are asserted, so no single reading satisfies them.
        ("shell-ksh-c-script-is-one-token",
         ["ksh", "-c", "true", _V, _P], [], ["true"], "ksh"),
        ("shell-bash-c-script-is-one-token",
         ["bash", "-c", "true", _V, _P], [], ["true"], "bash"),
        ("shell-operand-before-the-command-flag-is-the-script-file",
         ["bash", "somescript", "-c", pub], [], [], "bash"),
        #   …and after `--` the next token is that script FILE too, so the
        #   terminator must not be read as "the script starts here" on its own.
        #   (On ksh93 that same token IS a command line — asserted as its own
        #   case above; the terminator does not create it, the model does.)
        ("shell-terminator-without-the-command-flag",
         ["bash", "--", "-c", pub], [], [], "bash"),
        #   A long option that is NOT in this shell's operand-taking set eats
        #   nothing, so the `-c` behind it is still reached (`bash --norc -c
        #   <script>` runs <script>), and `+c` is the command flag exactly as
        #   `-c` is (observed on all four shells).
        ("shell-unknown-long-option-consumes-nothing",
         ["bash", "--norc", "-c", pub], [], [pub], "bash"),
        ("shell-plus-form-of-the-command-flag",
         ["bash", "+c", pub], [], [pub], "bash"),
        #   …and a command flag with nothing behind it has no script at all
        #   ("-c: option requires an argument").
        ("shell-command-flag-with-no-script",
         ["bash", "-c"], [], [], "bash"),
        ("shell-terminator-with-no-script",
         ["bash", "-c", "--"], [], [], "bash"),
        # ---- round-8: the BARE `+` introducer -------------------------------
        # The same divergence class as the letters, on the one option-introducer
        # token that carries none. bash/dash skip it and reach the `-c` behind
        # it; zsh/ksh93 end options there, so the `-c` behind it is no longer a
        # command FLAG — on zsh it becomes the script FILE, on ksh93 the first
        # OPERAND, which that model runs as a command ("-c: not found").
        # All were measured with `printf SCRIPT`.
        ("shell-bash-bare-plus-is-skipped",
         ["bash", "+", "-c", pub], [], [pub], "bash"),
        ("shell-dash-bare-plus-is-skipped",
         ["dash", "+", "-c", pub], [], [pub], "dash"),
        ("shell-zsh-bare-plus-ends-options",
         ["zsh", "+", "-c", pub], [], [], "zsh"),
        #   …and once `-c` has been seen the two readings agree: the script is
        #   the first operand after the `+`, never the `+` itself. Reading it as
        #   a plain operand — which is what the walk did before — made `+` the
        #   script and lost the real one on ALL FOUR shells.
        ("shell-bash-bare-plus-after-c-is-not-the-script",
         ["bash", "-c", "+", pub], [], [pub], "bash"),
        ("shell-zsh-bare-plus-after-c-is-not-the-script",
         ["zsh", "-c", "+", pub], [], [pub], "zsh"),
        #   the ambiguous names union the two readings, so the `-c` behind a
        #   leading `+` is still reached even for a name that could be zsh/ksh
        #   — and the ksh93 member contributes a SECOND candidate, the literal
        #   "-c", because on that model the token a bare `+` leaves as the
        #   first operand is itself run as a command ("-c: not found"). The
        #   union carries both readings rather than choosing; model order puts
        #   ksh93 first for the `ksh` name and last for `sh`.
        ("shell-sh-union-bare-plus",
         ["sh", "+", "-c", pub], [], [pub, "-c '%s'" % pub], "sh"),
        ("shell-ksh-union-bare-plus",
         ["ksh", "+", "-c", pub], [], ["-c '%s'" % pub, pub], "ksh"),
        #   a bare `-` ends options on every measured shell, so a `-c` behind it
        #   is never a command FLAG — and on the three script-FILE models that
        #   means no script at all (the ksh93 reading is asserted above)
        ("shell-bare-dash-ends-options",
         ["bash", "-", "-c", pub], [], [], "bash"),
        ("shell-bare-dash-after-c-is-not-the-script",
         ["bash", "-c", "-", pub], [], [pub], "bash"),
        # ---- round-9: ksh93's OPTIONAL separate operand ---------------------
        # `ksh -o -c <script>` prints the option list and RUNS <script>; every
        # other shell reads the `-c` as -o's operand and runs nothing.
        ("shell-ksh93-optional-operand-declined",
         ["ksh", "-o", "-c", pub], [], [pub], "ksh"),
        ("shell-ksh93-optional-operand-declined-plus-form",
         ["ksh", "+o", "-c", pub], [], [pub], "ksh"),
        ("shell-zsh-separate-operand-is-mandatory",
         ["zsh", "-o", "-c", pub], [], [], "zsh"),
        ("shell-bash-separate-operand-is-mandatory",
         ["bash", "-o", "-c", pub], [], [], "bash"),
        ("shell-dash-separate-operand-is-mandatory",
         ["dash", "-o", "-c", pub], [], [], "dash"),
        #   …and a NON-option operand is still taken, on ksh93 too
        ("shell-ksh93-nonoption-operand-still-taken",
         ["ksh", "-o", "errexit", "-c", pub], [], [pub], "ksh"),
        # ---- round-9: a `+` token containing a dash -------------------------
        # ksh93 ignores the dashes and parses through; zsh accepts exactly `+-`
        # as end-of-options and rejects every longer form; bash/dash reject all.
        ("shell-ksh93-plusdash-parses-through",
         ["ksh", "+-", "-c", pub], [], [pub], "ksh"),
        ("shell-ksh93-plusdash-long-parses-through",
         ["ksh", "+--", "-c", pub], [], [pub], "ksh"),
        ("shell-ksh93-plusdash-carries-the-command-flag",
         ["ksh", "+-c", pub], [], [pub], "ksh"),
        ("shell-zsh-plusdash-ends-options",
         ["zsh", "+-", "-c", pub], [], [], "zsh"),
        ("shell-zsh-plusdash-after-c-is-not-the-script",
         ["zsh", "-c", "+-", pub], [], [pub], "zsh"),
        ("shell-zsh-plusdash-lettered-is-rejected",
         ["zsh", "+-c", pub], [], [], "zsh"),
        ("shell-bash-plusdash-is-rejected",
         ["bash", "+-", "-c", pub], [], [], "bash"),
    ]


def _table_parser_cases() -> list[tuple[str, list[str], list[str], list[str],
                                        str]]:
    """One parser case per entry of the INDEPENDENT tables above: every
    carrier, every carrier option that consumes an operand — in its separate,
    ATTACHED and CLUSTERED shape, the last only for a carrier that HAS a
    no-operand short flag to cluster behind (`nice` and `stdbuf` have none, and
    `_tables_are_pinned` names them as the exception) — every optional-operand
    short letter, every bare carrier flag that must consume none, every shell
    invocation option that consumes a token, and every operand-consuming
    VCS / forge global option.

    Each case asserts the resulting PROGRAM, not only the finding, and that is
    what makes it regression-sensitive. Drop a carrier from the rule table and
    the form is usually still reported — by the prose pass, under the carrier's
    own name as the program — so a finding-only assertion would pass with the
    entry removed. Drop a VCS global option and the form is not reported at all.
    The operand value is a plain word ("x"), never a subcommand, so an option
    that stops consuming it leaves that word as the head of the parse.
    """
    pub = "%s %s" % (_V, _P)
    merge = "%s %s merge" % (_G, _R)
    api_method = "%s %s (non-GET method)" % (_G, _A)
    api_body = "%s %s (request body)" % (_G, _A)
    cases: list[tuple[str, list[str], list[str], list[str], str]] = []
    for name in sorted(_CARRIER_VALUE_OPTS):
        # timeout's duration sits between the options and the command.
        duration = ["5"] * _CARRIER_POSITIONALS.get(name, 0)
        cases.append(("carrier-%s" % name,
                      [name] + duration + [_V, _P], [pub], [], _V))
        prefix = _CARRIER_CLUSTER_PREFIX.get(name, "")
        for opt in _CARRIER_VALUE_OPTS[name]:
            cases.append(("carrier-%s-operand-%s" % (name, opt.lstrip("-")),
                          [name, opt, "x"] + duration + [_V, _P],
                          [pub], [], _V))
            if not (len(opt) == 2 and opt[0] == "-" and opt[1] != "-"):
                continue
            # An ATTACHED operand is one token and consumes nothing extra…
            cases.append(("carrier-%s-attached-%s" % (name, opt[1]),
                          [name, opt + "x"] + duration + [_V, _P],
                          [pub], [], _V))
            if not prefix:
                continue
            # …and the same option ENDING a cluster takes the NEXT token. The
            # operand is the text-emitter on purpose: a walk that discards the
            # cluster reads the emitter as the program, whose exemption then
            # hides the command — which is the whole defect this shape exists
            # to catch, and it is invisible to a finding-only assertion.
            cases.append(("carrier-%s-clustered-%s" % (name, opt[1]),
                          [name, "-" + prefix + opt[1], "echo"]
                          + duration + [_V, _P], [pub], [], _V))
        for flag in _CARRIER_BARE_FLAGS.get(name, ()):
            cases.append(("carrier-%s-bare-%s" % (name, flag.lstrip("-")),
                          [name, flag] + duration + [_V, _P], [pub], [], _V))
        # Every OPTIONAL-operand letter, in both shapes that matter: attached
        # (it takes the remainder) and alone (it takes nothing). Either way the
        # following token is the program, so the emitter stays the head — which
        # is what fails if the letter is ever read as mandatory.
        for ch in _CARRIER_OPTIONAL_SHORT_CHARS.get(name, ""):
            cases.append(("carrier-%s-optional-attached-%s" % (name, ch),
                          [name, "-" + ch + "x", "echo"] + duration
                          + [_V, _P], [], [], "echo"))
            cases.append(("carrier-%s-optional-alone-%s" % (name, ch),
                          [name, "-" + ch, "echo"] + duration + [_V, _P],
                          [], [], "echo"))
    # The ambiguous NAMES are read as the UNION of their models, in model
    # order: a divergence between two models must surface as BOTH candidate
    # scripts, and asserting the whole nested LIST is what fails if a model is
    # dropped from the union or the union collapses to its first answer. The
    # per-MODEL arity entries are exercised by _model_parser_cases() instead —
    # a name can no longer stand in for a model now that two names are unions.
    cases.append(("shell-sh-union-shopt-letter",
                  ["sh", "-O", "-c", pub], [], [pub], "sh"))
    cases.append(("shell-sh-union-attached-option-name",
                  ["sh", "-oerrexit", "-c", pub], [], [pub], "sh"))
    cases.append(("shell-sh-union-mask-operand",
                  ["sh", "-c", "-T", "0", pub], [], ["0", pub], "sh"))
    # (the `ksh` union's own cases sit with the measured divergence pairs in
    # _parser_cases, where their observations are recorded)
    # Every forge PR action, BOTH halves: each publishing one must be reported
    # and each non-publishing one must not. The program is asserted too, so an
    # action that stops reaching the rule is visible even where the prose pass
    # would have reported the same form anyway.
    for action in _FORGE_PR_MUTATIONS:
        cases.append(("forge-pr-%s" % action, [_G, _R, action, "1"],
                      ["%s %s %s" % (_G, _R, action)], [], _G))
    for action in _FORGE_PR_NON_MUTATIONS:
        cases.append(("forge-pr-not-%s" % action, [_G, _R, action, "1"],
                      [], [], _G))
    # Every non-PR family action, in the shapes its CONDITION turns on and off,
    # plus every action the table deliberately does not refuse.
    push_flag = "--" + _P
    for family in sorted(_FORGE_FAMILIES):
        for action, cond in sorted(_FORGE_FAMILIES[family].items()):
            form = "%s %s %s" % (_G, family, action)
            if cond == "always":
                cases.append(("forge-family-%s-%s" % (family, action),
                              [_G, family, action, "v1.0"], [form], [], _G))
            elif cond == "push-flag":
                cases.append(("forge-family-%s-%s-with-the-flag"
                              % (family, action),
                              [_G, family, action, "x", push_flag],
                              ["%s (%s)" % (form, push_flag)], [], _G))
                cases.append(("forge-family-%s-%s-without-the-flag"
                              % (family, action),
                              [_G, family, action, "x"], [], [], _G))
            elif cond == "positional-destination":
                cases.append(("forge-family-%s-%s-with-a-destination"
                              % (family, action),
                              [_G, family, action, "owner/x"], [form], [], _G))
                cases.append(("forge-family-%s-%s-without-a-destination"
                              % (family, action),
                              [_G, family, action], [], [], _G))
        for action in _FORGE_FAMILY_EXCLUDED.get(family, ()):
            cases.append(("forge-family-%s-not-%s" % (family, action),
                          [_G, family, action, "owner/x"], [], [], _G))
    # Every per-ACTION operand-taking option, in BOTH shapes and in BOTH
    # directions, so an entry cannot be pinned and unexercised. Its value must
    # not be read as the publish condition (the SEPARATE and the ATTACHED
    # spelling both), and a real destination behind it must still be reported —
    # which is what fails if an option is ever listed here that takes none.
    for (family, action), opts in sorted(_FORGE_ACTION_VALUE_OPTS.items()):
        for opt in sorted(opts):
            form = "%s %s %s" % (_G, family, action)
            tag = opt.lstrip("-")
            cases.append(("forge-action-value-opt-%s-%s-%s"
                          % (family, action, tag),
                          [_G, family, action, opt, "v"], [], [], _G))
            cases.append(("forge-action-value-opt-%s-%s-%s-attached"
                          % (family, action, tag),
                          [_G, family, action, opt + "=v"], [], [], _G))
            cases.append(("forge-action-value-opt-%s-%s-%s-then-destination"
                          % (family, action, tag),
                          [_G, family, action, opt, "v", "owner/x"],
                          [form], [], _G))
    # …and the short letters as a CLUSTER, which is the whole input to the
    # cluster walk: the first operand-taking letter takes the rest of the token
    # and the destination behind it is still the destination.
    for (family, action), chars in sorted(_FORGE_ACTION_SHORT_CHARS.items()):
        form = "%s %s %s" % (_G, family, action)
        # A letter in NEITHER modelled set, so a cluster built from it exercises
        # the cluster walk and nothing else. Derived rather than written down,
        # so it cannot quietly become a modelled letter.
        filler = next(c for c in "abcdefghijklmnopqrstuvwxyz"
                      if c not in chars and c not in _FORGE_GLOBAL_SHORT_CHARS)
        for char in chars:
            # The case that separates the CLUSTER walk from an exact-token
            # lookup, which is the only shape where they disagree: a cluster
            # whose LAST letter is the operand-taking one takes the FOLLOWING
            # token (pflag's own rule), so what looks like a destination behind
            # it is that option's VALUE. Without this the whole short-letter
            # half of the table is inert — every other shape is answered by the
            # exact-token branch, and a mutation removing the letters entirely
            # changed no verdict.
            cases.append(("forge-action-short-%s-%s-%s-ends-a-cluster"
                          % (family, action, char),
                          [_G, family, action, "-" + filler + char, "owner/x"],
                          [], [], _G))
            cases.append(("forge-action-short-%s-%s-%s-attached"
                          % (family, action, char),
                          [_G, family, action, "-" + char + "v"], [], [], _G))
            cases.append(("forge-action-short-%s-%s-%s-takes-the-next"
                          % (family, action, char),
                          [_G, family, action, "-" + char, "v"], [], [], _G))
            cases.append(("forge-action-short-%s-%s-%s-then-destination"
                          % (family, action, char),
                          [_G, family, action, "-" + char, "v", "owner/x"],
                          [form], [], _G))
    # Every `${…}` operator, at an operation position: the value and
    # replacement classes must yield the publishing word as a candidate, the
    # non-value class must not. The parameter is unknowable either way — only
    # the visible literal is ever considered.
    for op in _EXPANSION_VALUE_OPS:
        cases.append(("expansion-value-%s" % op,
                      [_V, "${x%s%s}" % (op, _P)], [pub], [], _V))
    for op in _EXPANSION_REPLACE_OPS:
        cases.append(("expansion-replacement-%s" % op,
                      [_V, "${x%sfoo/%s}" % (op, _P)], [pub], [], _V))
    for op in _EXPANSION_NON_VALUE_OPS:
        cases.append(("expansion-non-value-%s" % op,
                      [_V, "${x%s%s}" % (op, _P), "status"], [], [], _V))
    # Every DASHED family executable, and the operation it must not report.
    for family, op in sorted(_VCS_PAIRS):
        dashed = "%s-%s" % (_V, family)
        cases.append(("vcs-dashed-family-%s-%s" % (family, op),
                      [dashed, op, "origin", "main"],
                      ["%s %s" % (dashed, op)], [], dashed))
        cases.append(("vcs-dashed-family-%s-not-%s" % (family, op),
                      [dashed, "status"], [], [], dashed))
    # The inline alias, at the two hop counts where the BOUND decides: a chain
    # exactly as long as the bound resolves to its finding, and one hop longer
    # is REPORTED as unresolved rather than passed. The expected message is
    # written out here, not read from the rule table.
    cases.append(("vcs-alias-chain-within-the-bound",
                  [_V] + _alias_chain(_VCS_ALIAS_MAX_HOPS, _P),
                  [pub], [], _V))
    cases.append(("vcs-alias-chain-past-the-bound",
                  [_V] + _alias_chain(_VCS_ALIAS_MAX_HOPS + 1, _P),
                  ["an unresolved %s alias chain" % _V], [], _V))
    # …and the shell-valued alias, whose finding is a NESTED command line
    # rather than a form of its own.
    cases.append(("vcs-alias-shell-value-is-nested",
                  [_V, "-c", "%sp=%s%s %s" % (_AP, _VCS_ALIAS_SHELL_PREFIX,
                                              _V, _P), "p"],
                  [], ["%s %s" % (_V, _P)], _V))
    # Every family operation this table deliberately does NOT refuse.
    for family, ops in sorted(_VCS_PAIR_EXCLUDED.items()):
        for op in ops:
            cases.append(("vcs-pair-%s-not-%s" % (family, op),
                          [_V, family, op, "x"], [], [], _V))
    # Every false spelling the boolean flag parser accepts, and its true twin.
    for value in sorted(_PFLAG_FALSE):
        cases.append(("forge-repo-create-flag-false-%s" % value,
                      [_G, _REPO, "create", "o/r", push_flag + "=" + value],
                      [], [], _G))
    cases.append(("forge-repo-create-flag-true",
                  [_G, _REPO, "create", "o/r", push_flag + "=true"],
                  ["%s %s create (%s)" % (_G, _REPO, push_flag)], [], _G))
    # One case per TWO-WORD publishing pair, and — for every family option that
    # consumes a separate operand — the two shapes where its arity decides the
    # answer. The operand is the OPERATION NAME on purpose: an option read as
    # bare reports a form the tool never runs, and an option read as
    # operand-taking when it is really bare swallows the operation itself.
    for family, op in sorted(_VCS_PAIRS):
        pair = "%s %s %s" % (_V, family, op)
        cases.append(("vcs-pair-%s-%s" % (family, op),
                      [_V, family, op, "origin", "main"], [pair], [], _V))
        for opt in _VCS_PAIR_OPTS.get(family, ()):
            cases.append(("vcs-pair-%s-%s-behind-%s"
                          % (family, op, opt.lstrip("-")),
                          [_V, family, opt, "x", op, "origin", "main"],
                          [pair], [], _V))
            cases.append(("vcs-pair-%s-%s-is-the-operand-of-%s"
                          % (family, op, opt.lstrip("-")),
                          [_V, family, opt, op, "split"], [], [], _V))
        # An ATTACHED-only option consumes nothing, so the operation behind a
        # bare one is still reached.
        for opt in _VCS_PAIR_ATTACHED_ONLY_OPTS.get(family, ()):
            cases.append(("vcs-pair-%s-%s-behind-bare-%s"
                          % (family, op, opt.lstrip("-")),
                          [_V, family, opt, op, "origin", "main"],
                          [pair], [], _V))
    for opt in _VCS_GLOBAL_VALUE_OPTS:
        cases.append(("vcs-global-%s" % opt.lstrip("-"),
                      [_V, opt, "x", _P, "origin", "main"], [pub], [], _V))
    for opt in _VCS_ATTACHED_ONLY_OPTS:
        # The ATTACHED form is not the terminal form, so the walk must reach
        # past it — for the exec-path global that is the tool's own behaviour
        # (measured: it sets the value and the subcommand really runs), and for
        # the super-prefix global it is the MODELLED shape, since that option
        # was removed and the tool now rejects every spelling of it. Either
        # way, re-listing the option as operand-taking would swallow the
        # subcommand behind it. See the measurement at VCS_TERMINAL_OPTS.
        cases.append(("vcs-attached-operand-%s" % opt.lstrip("-"),
                      [_V, opt + "=x", _P, "origin", "main"], [pub], [], _V))
        # The BARE form of an option that is ALSO terminal runs nothing at all.
        want = [] if opt in _VCS_TERMINAL_OPTS else [pub]
        cases.append(("vcs-attached-only-%s" % opt.lstrip("-"),
                      [_V, opt, _P, "origin", "main"], want, [], _V))
    # Every terminal global: nothing runs behind a bare one…
    for opt in _VCS_TERMINAL_OPTS:
        cases.append(("vcs-terminal-%s" % opt.lstrip("-"),
                      [_V, opt, _P, "origin", "main"], [], [], _V))
        # …while ONLY the exact bare token terminates: any other spelling of
        # the same option is a lone flag, and the subcommand behind it is
        # reached. That is the tool's real behaviour for the exec-path global
        # and the MODELLED shape for the rest, which the tool rejects outright
        # — deliberate over-detection, in lockstep with the runtime table. The
        # measurement is at VCS_TERMINAL_OPTS.
        cases.append(("vcs-terminal-attached-%s" % opt.lstrip("-"),
                      [_V, opt + "=x", _P, "origin", "main"], [pub], [], _V))
    for opt in _FORGE_GLOBAL_VALUE_OPTS:
        cases.append(("forge-global-%s" % opt.lstrip("-"),
                      [_G, opt, "x", _R, "merge", "1"], [merge], [], _G))
    # Every short global letter in its CLUSTER form. The prefix letter is the
    # forge CLI's own -h; as with the option set itself, this pins the gate's
    # MODELLED shape rather than a real invocation (see
    # _FORGE_GLOBAL_VALUE_OPTS), and reading one token too few here would make
    # the operand the subcommand and lose the finding.
    for ch in _FORGE_GLOBAL_SHORT_CHARS:
        cases.append(("forge-global-clustered-%s" % ch,
                      [_G, "-h" + ch, "x", _R, "merge", "1"], [merge], [], _G))
        cases.append(("forge-global-attached-%s" % ch,
                      [_G, "-" + ch + "x", _R, "merge", "1"], [merge], [], _G))
    # Every short API letter, each in the cluster form that makes it matter.
    # A MUTATION letter behind a no-operand letter must still be found; a
    # non-mutating operand-taking letter must SWALLOW the method flag behind it,
    # which is what fails if that letter ever drops out of the set.
    for ch in _FORGE_API_SHORT_CHARS:
        if ch in ("f", "F"):
            cases.append(("forge-api-clustered-body-%s" % ch,
                          [_G, _A, "-i" + ch, "a=b", "repos/o/r/x"],
                          [api_body], [], _G))
            cases.append(("forge-api-clustered-body-attached-%s" % ch,
                          [_G, _A, "-i" + ch + "a=b", "repos/o/r/x"],
                          [api_body], [], _G))
        elif ch == "X":
            cases.append(("forge-api-clustered-method-%s" % ch,
                          [_G, _A, "-i" + ch, "POST", "repos/o/r/x"],
                          [api_method], [], _G))
            cases.append(("forge-api-clustered-method-attached-%s" % ch,
                          [_G, _A, "-i" + ch + "POST", "repos/o/r/x"],
                          [api_method], [], _G))
        else:
            cases.append(("forge-api-clustered-swallows-method-%s" % ch,
                          [_G, _A, "-i" + ch, "-X", "POST", "repos/o/r/x"],
                          [], [], _G))
    return cases


def _model_parser_cases() -> list[tuple[str, str, list[str], str]]:
    """(name, model, args, expected script) for ONE shell arity model at a time.

    Every entry of the hand-written `_SHELL_LETTER_ARITY` / `_SHELL_LONG_VALUE_
    OPTS` / `_SHELL_FIRST_OPERAND` tables, in the shapes where getting it wrong
    loses the script: before `-c`, after `-c`, the `+` form, ending a cluster,
    clustered with `-c`, spelled with an ATTACHED operand, and — for the
    first-operand rule — with no `-c` present at all. The separate operand is a
    plain word ("x"), so a walk that stops consuming reports that word as the
    script instead of the real one, and the ATTACHED shapes assert OPPOSITE
    outcomes for the next-token and attached arities, so one model applied to
    every shell cannot satisfy both halves.

    The THIRD arity is not separated by those two shapes on a model that reads
    its first operand as a command line — there `-o -c <cmd>` answers <cmd>
    either way — so it gets its own family further down (`-o -T <mask> <cmd>`,
    where only a DECLINING `-o` leaves `-T` to eat the mask). Do not read the
    attached/clustered pair as covering all three.

    These drive `_shell_script_index` directly rather than `analyze`, because a
    shell NAME is a union of models and so cannot exercise one model's answer:
    the expected value is the exact SCRIPT the model resolves to (or None), not
    merely "a script was found"."""
    pub = "%s %s" % (_V, _P)
    cases: list[tuple[str, str, list[str], str]] = []
    for model in sorted(_SHELL_LETTER_ARITY):
        first_is_command = _SHELL_FIRST_OPERAND[model] == "command-line"
        for ch, kind in sorted(_SHELL_LETTER_ARITY[model].items()):
            tag = "%s-%s" % (model, ch)
            cases.append(("shell-%s-before-c" % tag, model,
                          ["-" + ch, "x", "-c", pub], pub))
            cases.append(("shell-%s-after-c" % tag, model,
                          ["-c", "-" + ch, "x", pub], pub))
            cases.append(("shell-%s-plus-form" % tag, model,
                          ["+" + ch, "x", "-c", pub], pub))
            cases.append(("shell-%s-cluster-end-takes-next" % tag, model,
                          ["-x" + ch, "y", "-c", pub], pub))
            if kind == "next":
                # The cluster continues THROUGH the letter, so `-<ch>c` still
                # reaches the command flag and the operand is the next token…
                cases.append(("shell-%s-clustered-with-c" % tag, model,
                              ["-" + ch + "c", "x", pub], pub))
                # …and an attached remainder is NOT the operand: the letter
                # still takes the FOLLOWING token, which here is the `-c`
                # itself, so this invocation has no script at all (and the real
                # shell rejects it).
                cases.append(("shell-%s-attached-is-not-an-operand" % tag,
                              model, ["-" + ch + "x", "-c", pub], None))
            else:
                # The attached remainder IS the operand and ends the cluster…
                cases.append(("shell-%s-attached-operand" % tag, model,
                              ["-" + ch + "x", "-c", pub], pub))
                # …so `-<ch>c` is that letter with the operand "c" and there is
                # NO command flag. What follows is then this model's FIRST
                # OPERAND: a script FILE on zsh (None), a command LINE on
                # ksh93. That is the `-oc` bypass — measured, `ksh -oc 'printf
                # SCRIPT'` prints SCRIPT — and expecting <pub> here is what
                # fails if the first-operand flag is ever dropped, while
                # expecting None on zsh is what fails if this model is read
                # with the next-token arity.
                # ksh93's -T and -R over-report in this shape (`ksh -Tc <cmd>`
                # is rejected, `ksh -Rc <cmd>` writes a cross-reference and
                # runs nothing); that is the flag's stated, safe-direction
                # cost, not a claim that they execute.
                cases.append(("shell-%s-attached-eats-the-command-flag" % tag,
                              model, ["-" + ch + "c", pub],
                              pub if first_is_command else None))
    for model in sorted(_SHELL_LONG_VALUE_OPTS):
        for opt in _SHELL_LONG_VALUE_OPTS[model]:
            tag = "%s-%s" % (model, opt.lstrip("-"))
            cases.append(("shell-long-%s-before-c" % tag, model,
                          [opt, "x", "-c", pub], pub))
            cases.append(("shell-long-%s-after-c" % tag, model,
                          ["-c", opt, "x", pub], pub))
    # The THIRD arity, in the shape that separates it: the letter ends its token
    # and the NEXT token is itself an option. Only ksh93 declines the operand
    # there and reaches the `-c`; every other model consumes it and has no
    # script at all. Both halves are asserted, so no single arity satisfies them.
    # A CONSUMING letter on ksh93 lands on <pub> as the first operand instead,
    # which that model executes — so `pub if optional` alone is not the whole
    # answer there, and the two reasons are spelled apart on purpose.
    for model in sorted(_SHELL_LETTER_ARITY):
        first_is_command = _SHELL_FIRST_OPERAND[model] == "command-line"
        for ch, kind in sorted(_SHELL_LETTER_ARITY[model].items()):
            optional = kind == "attached-or-next-nonoption"
            reaches = optional or first_is_command
            cases.append(("shell-%s-%s-option-follows-minus" % (model, ch),
                          model, ["-" + ch, "-c", pub], pub if reaches else None))
            cases.append(("shell-%s-%s-option-follows-plus" % (model, ch),
                          model, ["+" + ch, "-c", pub], pub if reaches else None))
            # …and a NON-option operand is still taken by all three arities
            cases.append(("shell-%s-%s-nonoption-operand-taken" % (model, ch),
                          model, ["-" + ch, "x", "-c", pub], pub))
            # The `+`-introduced next token, which is what separates "an option
            # is not my operand" from "anything that is not dash-prefixed is".
            # Only a declining model reaches the `+c` and reads it as the
            # command flag; a consuming model eats it and has no script at all.
            # Measured: `ksh -o +c <script>` RUNS <script>, while
            # `zsh -o +c <script>` → "no such option: +c" and
            # `bash -o +c <script>` → "+c: invalid option name".
            cases.append(("shell-%s-%s-plus-token-is-not-an-operand"
                          % (model, ch), model,
                          ["-" + ch, "+c", pub], pub if reaches else None))
    # …and the shape that still SEPARATES the third arity once a model reads
    # its first operand as a command line. On such a model `-o -c <cmd>` no
    # longer tells the two readings apart — declining reaches the `-c` and
    # consuming lands on <cmd> as the first operand, so both answer <cmd>. What
    # still separates them is a declined token that takes an operand OF ITS
    # OWN: `-o -T <mask> <cmd>` reaches <cmd> only if `-o` declined and left
    # `-T` to eat <mask>; a consuming `-o` swallows the `-T` and makes <mask>
    # itself the first operand. `-T` is spelled literally because it is this
    # model's own mandatory-operand letter — the loop runs for no other model.
    # Measured: `ksh -o -T 0 'printf SCRIPT'` prints the option list AND then
    # SCRIPT, and `ksh -o +T 0 …` does the same. (`ksh -T -T 0 …` is rejected
    # outright — the "0" this expects there is the flag's stated over-report,
    # not a claim that it runs.)
    for model in sorted(_SHELL_LETTER_ARITY):
        if _SHELL_FIRST_OPERAND[model] != "command-line":
            continue
        for ch, kind in sorted(_SHELL_LETTER_ARITY[model].items()):
            optional = kind == "attached-or-next-nonoption"
            want = pub if optional else "0"
            cases.append(("shell-%s-%s-declined-option-keeps-its-operand"
                          % (model, ch), model,
                          ["-" + ch, "-T", "0", pub], want))
            cases.append(("shell-%s-%s-declined-plus-option-keeps-its-operand"
                          % (model, ch), model,
                          ["-" + ch, "+T", "0", pub], want))
    # A `+` token whose body contains a dash, per model: rejected (bash/dash),
    # exactly `+-` as end-of-options (zsh), or parsed through (ksh93).
    for model in sorted(_SHELL_PLUS_DASH):
        act = _SHELL_PLUS_DASH[model]
        through = act == "parse-through"
        ends = act == "bare-ends-options"
        cases.append(("shell-%s-plusdash-before-c" % model, model,
                      ["+-", "-c", pub], pub if through else None))
        cases.append(("shell-%s-plusdash-after-c" % model, model,
                      ["-c", "+-", pub], pub if (through or ends) else None))
        cases.append(("shell-%s-plusdash-long-before-c" % model, model,
                      ["+--", "-c", pub], pub if through else None))
        cases.append(("shell-%s-plusdash-lettered" % model, model,
                      ["+-c", pub], pub if through else None))
        # A longer dashed form AFTER `-c`: only a parse-through model reaches
        # the script. This is the shape that separates "exactly `+-` ends
        # options" from "any dashed `+` ends options" — before `-c` both answer
        # None for the same reason and cannot tell them apart. Measured:
        # `ksh -c +-- <script>` RUNS <script>; `zsh -c +-- <script>` →
        # "no such option: _"; bash and dash reject it too.
        cases.append(("shell-%s-plusdash-long-after-c" % model, model,
                      ["-c", "+--", pub], pub if through else None))
    # The bare option-introducer tokens, per model. `+` is where the four split
    # — skipped by bash/dash so the `-c` behind it is still reached, and
    # end-of-options on zsh/ksh93 so it is NOT — and the AFTER-`-c` position is
    # where both readings must agree on the script. A bare `-` is
    # end-of-options everywhere; it carries no per-model entry, so it is pinned
    # here directly against every model rather than assumed.
    for model in sorted(_SHELL_BARE_PLUS):
        skips = _SHELL_BARE_PLUS[model] == "skip"
        first_is_command = _SHELL_FIRST_OPERAND[model] == "command-line"
        # A model that ENDS options here makes the `-c` behind the introducer
        # the FIRST OPERAND — a script file on zsh (None), and on ksh93 a
        # command line whose text is the literal "-c" (measured: `ksh + -c
        # <cmd>` and `ksh - -c <cmd>` both answer "-c: not found", so the
        # resolved script is "-c" and <cmd> is never reached). Asserting the
        # exact string, not merely "something", is what separates the two.
        cases.append(("shell-%s-bare-plus-before-c" % model, model,
                      ["+", "-c", pub],
                      pub if skips else ("-c" if first_is_command else None)))
        cases.append(("shell-%s-bare-plus-after-c" % model, model,
                      ["-c", "+", pub], pub))
        cases.append(("shell-%s-bare-dash-before-c" % model, model,
                      ["-", "-c", pub], "-c" if first_is_command else None))
        cases.append(("shell-%s-bare-dash-after-c" % model, model,
                      ["-c", "-", pub], pub))
        cases.append(("shell-%s-terminator-after-c" % model, model,
                      ["-c", "--", pub], pub))
    # The FIRST OPERAND with no `-c` anywhere — the divergence that needs no
    # option spelling at all, at every position a plain operand is reachable
    # from. bash/dash/zsh answer None (a script FILE); ksh93 answers the
    # operand, because it runs that text as a command line when the file open
    # fails. Each ksh93 shape here was observed to EXECUTE `printf SCRIPT`:
    # bare, behind an option, behind an option WITH an operand, after `--`,
    # after a bare `-`, and after a bare `+`.
    for model in sorted(_SHELL_FIRST_OPERAND):
        want = pub if _SHELL_FIRST_OPERAND[model] == "command-line" else None
        cases.append(("shell-%s-first-operand-bare" % model, model,
                      [pub], want))
        cases.append(("shell-%s-first-operand-after-a-flag" % model, model,
                      ["-x", pub], want))
        cases.append(("shell-%s-first-operand-after-an-option-operand" % model,
                      model, ["-o", "errexit", pub], want))
        cases.append(("shell-%s-first-operand-after-terminator" % model, model,
                      ["--", pub], want))
        cases.append(("shell-%s-first-operand-after-bare-dash" % model, model,
                      ["-", pub], want))
        cases.append(("shell-%s-first-operand-after-bare-plus" % model, model,
                      ["+", pub], want))
        # …and the SECOND operand is not a second command line: it is $1.
        cases.append(("shell-%s-first-operand-not-the-second" % model, model,
                      ["first", pub], "first" if want else None))
    return cases


def _quote_model_cases() -> list[tuple[str, str, list[str]]]:
    """(name, raw segment text, expected argv) for the QUOTING model alone.

    These drive `tokenize` rather than `scan_text`, for the same reason the
    shell-model cases drive `_shell_script_index`: a whole-line fixture is a
    UNION of readings, so the quote-aware tokenizer can be wrong about a word
    while the quote-naive re-read or the code-span pass still reports the same
    form — a test that passes with its own fix reverted. The expected value
    here is the exact argv, so a decode that produces the wrong CHARACTERS
    fails even when the finding would have surfaced anyway.

    Every expectation was printed by this host's bash before it was written
    down (`printf '%s\\n' <word>`), the two `\\u`/`\\U` cases excepted — bash
    3.2.57(1) predates them and prints them literally, while bash >= 4.2 and
    the floor guard both decode them. Those two are marked, and they are the
    only entries here that are DOCUMENTED rather than observed."""
    return [
        # the pre-existing two forms must be unchanged by the widening
        ("plain-word", "%s %s" % (_V, _P), [_V, _P]),
        ("single-quoted-run", "'a b'", ["a b"]),
        ("double-quoted-run", '"a b"', ["a b"]),
        ("empty-single-quotes", "''", [""]),
        ("backslash-escape-outside-quotes", "a\\ b", ["a b"]),
        ("unterminated-single-quote", "'abc", ["abc"]),
        # inside DOUBLE quotes a backslash escapes only these four characters;
        # anywhere else it stays literal. `"a\\xb"` printing `a\\xb` is what
        # makes the nested-ANSI-C case below work at all.
        ("double-quote-backslash-literal", '"a\\xb"', ["a\\xb"]),
        ("double-quote-backslash-escapable", '"a\\$b"', ["a$b"]),
        # ANSI-C: the escapes are DECODED
        ("ansi-c-hex", _ansi_c(_V), [_V]),
        ("ansi-c-octal", _ansi_c(_P, "o"), [_P]),
        ("ansi-c-simple-escape", "$'a\\tb'", ["a\tb"]),
        ("ansi-c-control-char", "$'\\cA'", ["\x01"]),
        # an escape the decoder does not know keeps its backslash — bash does
        # the same, and this is what keeps an unknown escape from spelling the
        # subcommand
        ("ansi-c-unknown-escape", "$'\\q%s'" % _P[1:], ["\\q" + _P[1:]]),
        # a backslash-escaped closing quote does NOT end the region
        ("ansi-c-escaped-quote", "$'it\\'s'", ["it's"]),
        # a word ASSEMBLED across regions, in both spellings
        ("ansi-c-concatenated-onto-prefix",
         "%s$'%s'" % (_P[:2], _P[2:]), [_P]),
        ("ansi-c-two-adjacent-regions",
         "$'%s'$'%s'" % (_P[:2], _P[2:]), [_P]),
        # DOCUMENTED (bash >= 4.2), not observed on this host — see above.
        ("ansi-c-unicode-short", _ansi_c(_P[0], "u"), [_P[0]]),
        ("ansi-c-unicode-long", _ansi_c(_P[0], "U"), [_P[0]]),
        # locale translation is a DOUBLE-quoted string wearing a `$`
        ("locale-quote", '$"%s"' % _P, [_P]),
        ("locale-quote-dq-escape", '$"a\\$b"', ["a$b"]),
        ("locale-quote-keeps-dq-literal-backslash", '$"a\\xb"', ["a\\xb"]),
        # ANSI-C is NOT performed inside double quotes — the region travels
        # through as literal text and the INNER shell decodes it. Getting this
        # wrong in either direction breaks a real form: decoding here would
        # make the outer word wrong, and dropping the backslash (the pre-fix
        # behaviour) rewrote it to `$'x70ush'`.
        ("ansi-c-is-inert-inside-double-quotes",
         '"%s %s"' % (_V, _ansi_c(_P)), ["%s %s" % (_V, _ansi_c(_P))]),
        # `$` followed by anything else is an ordinary character
        ("dollar-paren-is-not-a-quote", "$(x)", ["$(x)"]),
        ("dollar-brace-is-not-a-quote", "${y}", ["${y}"]),
        ("bare-dollar", "$5", ["$5"]),
        # A quoted span inside a `${…}` body is handed over VERBATIM, quotes
        # and all — the same treatment a backslash gets there, and for the same
        # reason: the expansion's own grammar has to see whether its `}` or its
        # `/` was quoted, and a collapsed span has already thrown that away.
        # OUTSIDE a body the span still contributes its VALUE, so this is a
        # body-local rule and not a change to the quoting model.
        ("expansion-body-keeps-a-quoted-brace-verbatim",
         '${x/"a}b"/%s}' % _P, ['${x/"a}b"/%s}' % _P]),
        ("expansion-body-keeps-a-quoted-separator-verbatim",
         '${x/"a/b"/%s}' % _P, ['${x/"a/b"/%s}' % _P]),
        ("expansion-body-keeps-a-single-quoted-span-verbatim",
         "${x:-'%s'}" % _P, ["${x:-'%s'}" % _P]),
        # …and a quoted span carrying a SPACE stays in the one token, because a
        # body does not split on whitespace at all
        ("expansion-body-quoted-span-with-a-space",
         '${x:-"a b"}', ['${x:-"a b"}']),
        ("quoted-span-outside-a-body-still-contributes-its-value",
         '"a}b"', ["a}b"]),
        # A bare `{` inside a body is TEXT, so the first `}` terminates and the
        # operands behind it stay SEPARATE words. This is the tokenizer half of
        # the round-8 fix, and it is here rather than only in the whole-line
        # fixture because the whole-line reading is a union: the quote-naive
        # re-read splits on whitespace regardless and would report the form even
        # with the quote-aware tokenizer still fusing the line into one word.
        ("expansion-body-bare-open-brace-does-not-nest",
         "%s ${x/{/%s} origin main" % (_V, _P),
         [_V, "${x/{/%s}" % _P, "origin", "main"]),
        # …and `${` inside a body still does nest, so the INNER `}` closes the
        # inner expansion and the outer token still ends at the outer one.
        ("expansion-body-dollar-brace-still-nests",
         "%s ${x:-${y:-%s}} origin" % (_V, _P),
         [_V, "${x:-${y:-%s}}" % _P, "origin"]),
    ]


def _carrier_parser_cases() -> list[tuple[str, list[str], list[str], list[str],
                                          str]]:
    """The string-exec carriers' OWN option grammar, asserted on `analyze`'s
    nested output rather than on a whole line.

    Here for the same reason `_quote_model_cases` exists: a whole-line fixture
    is a UNION of readings, and on these forms the union hides most of the
    grammar. The quoted-operand pass re-reads the `-o` operand as a command
    line, so every spelling whose separator is ORDINARY whitespace already
    flags through that pass with this table absent — and, in the other
    direction, the two NON-separators below also flag through it, because the
    tokenizer splits on Python's `str.isspace()`, which accepts VT and FF while
    the shell's IFS and ssh_config both do not. That divergence is
    over-detection and is left standing (this gate is biased that way and the
    line is prose either way).

    So the honest claim, narrowed from "a whole-line fixture cannot tell a
    correct separator set from a wrong one": a whole-line fixture DOES catch
    some wrong sets — losing `=` breaks the spellings whose words would
    otherwise stay glued — and cannot catch any wrong set whose members are all
    ordinary whitespace, which is every remaining member. These cases can,
    because the expectation is the exact nested list."""
    cmd = "%s %s" % (_V, _P)
    out: list[tuple[str, list[str], list[str], list[str], str]] = []
    for keyword in _SSH_CMD_KEYWORDS:
        for sname, sep, _ansi in _SSH_SEPARATORS:
            out.append(("carrier-pair-%s-%s" % (keyword, sname),
                        ["ssh", "-o", "%s%s%s" % (keyword, sep, cmd), "host"],
                        [], [cmd], "ssh"))
    for keyword in _SSH_CMD_KEYWORDS:
        for pname, prefix in _SSH_KEYWORD_PREFIXES:
            out.append(("carrier-pair-leading-%s-%s" % (pname, keyword),
                        ["ssh", "-o", "%s%s=%s" % (prefix, keyword, cmd),
                         "host"], [], [cmd], "ssh"))
    for sname, sep in _SSH_NON_SEPARATORS:
        # The keyword and the command fuse into ONE keyword, which is not a
        # command-bearing one, so the option carries nothing.
        out.append(("carrier-pair-non-separator-%s" % sname,
                    ["ssh", "-o", "proxycommand%s%s" % (sep, cmd), "host"],
                    [], [], "ssh"))
    for keyword in _SSH_PLAIN_KEYWORDS:
        out.append(("carrier-pair-plain-keyword-%s" % keyword,
                    ["ssh", "-o", "%s=%s" % (keyword, cmd), "host"],
                    [], [], "ssh"))
    return out + [
        # The keyword is CASE-INSENSITIVE (ssh_config(5)); the value is not
        # touched.
        ("carrier-keyword-is-case-insensitive",
         ["ssh", "-o", "ProxyCommand=%s" % cmd, "host"], [], [cmd], "ssh"),
        ("carrier-keyword-is-case-insensitive-upper",
         ["ssh", "-o", "PROXYCOMMAND=%s" % cmd, "host"], [], [cmd], "ssh"),
        # An EMPTY value is no command line.
        ("carrier-empty-value", ["ssh", "-o", "proxycommand=", "host"],
         [], [], "ssh"),
        # The operand may be ATTACHED to the option letter.
        ("carrier-attached-operand",
         ["ssh", "-oproxycommand=%s" % cmd, "host"], [], [cmd], "ssh"),
        # getopt(3)'s cluster rule, both ways round. A letter taking no operand
        # is walked THROUGH…
        ("carrier-cluster-reaches-the-command-option",
         ["ssh", "-vo", "proxycommand=%s" % cmd, "host"], [], [cmd], "ssh"),
        # …while an operand-taking letter EARLIER in the cluster hides what
        # follows it: here the port is the single character "o", and the next
        # token is the destination, not an option's value.
        ("carrier-cluster-earlier-value-letter-hides-the-command-option",
         ["ssh", "-po", "proxycommand=%s" % cmd, "host"], [], [], "ssh"),
        # Options end AT THE DESTINATION for a carrier that joins its trailing
        # operands: this `-o` is an argument to the REMOTE command.
        ("carrier-option-after-the-destination-is-not-ours",
         ["ssh", "host", "echo", "-o", "proxycommand=%s" % cmd],
         [], [], "ssh"),
        ("carrier-slogin-has-the-same-grammar",
         ["slogin", "-o", "proxycommand=%s" % cmd, "host"], [], [cmd],
         "slogin"),
        # `rsh` has NO command-bearing option. Its `-k` DOES take an
        # operand — a Kerberos realm — so this pins the row itself rather than
        # the arity: the operand is read and then carried nowhere. A negative
        # spelled with an unknown letter would not (the cluster walk drops the
        # token before `cmd_opts` is ever consulted).
        ("carrier-rsh-has-no-command-option",
         ["rsh", "-k", cmd, "host"], [], [], "rsh"),
        ("carrier-rsh-unknown-letter-is-a-lone-flag",
         ["rsh", "-o", "proxycommand=%s" % cmd, "host"], [], [], "rsh"),
        # `su` takes its command from `-c` wherever it appears — its option
        # walk does NOT stop at an operand, which is what `destinations: None`
        # says. Both orders, because only the second one distinguishes it.
        ("carrier-su-command-option", ["su", "-c", cmd, "someone"],
         [], [cmd], "su"),
        ("carrier-su-command-option-after-the-user",
         ["su", "someone", "-c", cmd], [], [cmd], "su"),
        # …and its long spelling, as a SEPARATE operand.
        ("carrier-su-long-command-option", ["su", "--command", cmd, "someone"],
         [], [cmd], "su"),
        ("carrier-su-attached-long-command-option",
         ["su", "--command=%s" % cmd, "someone"], [], [cmd], "su"),
        ("carrier-su-session-command",
         ["su", "--session-command", cmd, "someone"], [], [cmd], "su"),
        ("carrier-su-session-command-attached",
         ["su", "--session-command=%s" % cmd, "someone"], [], [cmd], "su"),
        # TERMINAL options. Recorded, not broken on: the command option may
        # already have been read and it still never runs.
        ("carrier-terminal-option-before-the-command-option",
         ["ssh", "-V", "-o", "proxycommand=%s" % cmd, "host"], [], [], "ssh"),
        ("carrier-terminal-option-after-the-command-option",
         ["ssh", "-o", "proxycommand=%s" % cmd, "-V", "host"], [], [], "ssh"),
        ("carrier-su-terminal-option-after-the-command-option",
         ["su", "-c", cmd, "--help", "someone"], [], [], "su"),
        # …but the option region ENDS at the destination, so a terminal option
        # spelled past it belongs to the remote command and suppresses nothing.
        ("carrier-terminal-option-past-the-destination",
         ["ssh", "-o", "proxycommand=%s" % cmd, "host", "-V"], [], [cmd],
         "ssh"),
        # An attached long option that is NOT command-bearing carries nothing,
        # and the walk continues past it rather than stopping.
        ("carrier-su-attached-long-non-command-option",
         ["su", "--shell=/bin/sh", "-c", cmd, "someone"], [], [cmd], "su"),
        # `--` is the exact option TERMINATOR: what follows is the destination,
        # not an option, however it is spelled.
        ("carrier-double-dash-ends-the-options",
         ["ssh", "--", "-o", "proxycommand=%s" % cmd, "host"], [], [], "ssh"),
        ("carrier-double-dash-ends-su-options-too",
         ["su", "--", "-c", cmd, "someone"], [], [], "su"),
        # `su` has no `-o` keyword grammar at all, so its `-c` value is taken
        # WHOLE — a keyword-looking prefix is part of the command line.
        ("carrier-su-does-not-read-ssh-keywords",
         ["su", "-c", "proxycommand=%s" % cmd, "someone"],
         [], ["proxycommand=%s" % cmd], "su"),
    ]


def _all_parser_cases() -> list[tuple[str, list[str], list[str], list[str],
                                      str]]:
    return _parser_cases() + _table_parser_cases() + _carrier_parser_cases()


def _scan_paths_reports_what_it_read() -> list[str]:
    """`scan_paths` must never certify a path it could not read.

    The bug this pins, measured at the final integration gate: an unreadable or
    missing path was skipped, the summary printed the REQUESTED count as if it
    had been scanned, and the exit status was 0 — so a file the gate never
    opened was indistinguishable from a clean one, in the reassuring direction.

    Every branch is asserted against a POSITIVE CONTROL — the same bytes, made
    readable, must still produce the finding — because a failure path that
    returns 2 for everything would satisfy the failure assertions alone while
    proving the scan no longer works at all.
    """
    import shutil
    import tempfile
    problems: list[str] = []
    tmp = tempfile.mkdtemp(prefix="push-form-selftest-")
    try:
        dirty = os.path.join(tmp, "dirty.md")
        clean = os.path.join(tmp, "clean.md")
        gone = os.path.join(tmp, "absent.md")
        gitlink = os.path.join(tmp, "submodule")
        with open(dirty, "w") as fh:
            fh.write("%s %s origin main\n" % (VCS, PUBLISH))
        with open(clean, "w") as fh:
            fh.write("nothing to see here\n")
        os.mkdir(gitlink)
        for label, paths, links, want in (
                # the controls first: the scan still works
                ("a readable file carrying the form", [dirty], (), 1),
                ("a readable file carrying nothing", [clean], (), 0),
                # a directory the INDEX calls a submodule is the one legal skip
                ("a directory the index records as a submodule",
                 [gitlink], (gitlink,), 0),
                # ...and the same directory NOT so recorded is a read failure.
                # This pair is the whole point: without the negative half, any
                # directory would be waved through as a submodule, which is the
                # bug the first version of this guard shipped with.
                ("a directory the index does NOT record as a submodule",
                 [gitlink], (), 2),
                # the failure paths the bug hid
                ("a path that does not exist", [gone], (), 2),
                ("an unreadable path beside a clean one", [clean, gone], (), 2)):
            got = _quiet_scan_paths(paths, links)
            if got != want:
                problems.append("scan_paths on %s returned %d, expected %d — a "
                                "path the scan could not read must never exit 0"
                                % (label, got, want))
        # The count must be what was READ, not what was asked for.
        out = _captured_scan_paths([clean, gitlink], (gitlink,))
        if "1 files scanned" not in out:
            problems.append("scan_paths reported %r for one readable file plus "
                            "one submodule pointer — the summary must count what "
                            "it read, not what it was handed" % out.strip())
        # And the index reader must actually distinguish the two modes, or the
        # pair above is asserted against a classification nothing produces.
        problems += _tracked_entries_reads_the_index(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return problems


def _tracked_entries_reads_the_index(tmp: str) -> list[str]:
    """The index PARSER must tell a gitlink from a regular file.

    `scan_paths`' gitlink cases are handed the classification directly, so they
    hold however `tracked_entries` behaves — which is this class one layer in
    again: mutating `mode == GITLINK_MODE` to `False` left the whole selftest
    green. That mutation fails CLOSED (a real submodule becomes a read error,
    which is loud), but "loud" is not "checked", and the opposite drift would be
    silent. So the parser is exercised against a real index carrying both modes.

    The gitlink is fabricated with `update-index --cacheinfo` rather than a real
    submodule: it produces exactly the index record being parsed, needs no second
    repository and no network, and keeps the case hermetic.
    """
    import shutil
    problems: list[str] = []
    repo = os.path.join(tmp, "indexprobe")
    os.mkdir(repo)
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CONFIG_SYSTEM=os.devnull)

    def git(*args):
        # `input=b""` is load-bearing, not hygiene: without it these calls
        # INHERIT the caller's stdin. Measured while writing this case — a `git`
        # reading stdin consumed the harness's own input, the probe bailed out,
        # and three different mutations were then all "caught" by the identical
        # setup-failure message. That is a mutation caught by a bail-out rather
        # than by its case, which proves nothing, and it is the same trap as a
        # mutation caught by a traceback.
        return subprocess.run(("git", "-C", repo) + args, env=env,
                              capture_output=True, input=b"")
    try:
        if git("init", "-q").returncode:
            return ["cannot create the index probe repository — the gitlink "
                    "classification is UNVERIFIED in this run"]
        with open(os.path.join(repo, "plain.md"), "w") as fh:
            fh.write("nothing\n")
        git("add", "plain.md")
        # Reuse the blob's own object id as the fabricated gitlink's commit id:
        # git does not require a gitlink's target to exist in this repository,
        # and borrowing a real id keeps the probe correct under any object-format
        # (sha1 or sha256) without hard-coding a hash length.
        staged = git("ls-files", "-s", "plain.md").stdout.decode().split()
        oid = staged[1] if len(staged) > 1 else ""
        if not oid:
            return ["cannot fabricate a gitlink entry — the classification is "
                    "UNVERIFIED in this run"]
        git("update-index", "--add", "--cacheinfo",
            "%s,%s,sub" % (_GITLINK_MODE_FIXTURE, oid))
        cwd = os.getcwd()
        try:
            os.chdir(repo)
            entries = dict(tracked_entries())
        finally:
            os.chdir(cwd)
        if entries.get("sub") is not True:
            problems.append("tracked_entries did not classify a mode-%s index "
                            "entry as a gitlink (got %r) — every submodule "
                            "pointer would be reported as unreadable"
                            % (_GITLINK_MODE_FIXTURE, entries.get("sub")))
        if entries.get("plain.md") is not False:
            problems.append("tracked_entries classified a regular file as a "
                            "gitlink (got %r) — an unread file would be waved "
                            "through as a submodule" % entries.get("plain.md"))
    finally:
        shutil.rmtree(repo, ignore_errors=True)
    return problems


def _quiet_scan_paths(paths: list[str], gitlinks=()) -> int:
    """`scan_paths`'s status with its output suppressed."""
    return _run_scan_paths(paths, gitlinks)[0]


def _captured_scan_paths(paths: list[str], gitlinks=()) -> str:
    """`scan_paths`'s stdout."""
    return _run_scan_paths(paths, gitlinks)[1]


def _run_scan_paths(paths: list[str], gitlinks=()) -> tuple[int, str]:
    import io
    import contextlib
    out = io.StringIO()
    err = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = scan_paths(list(paths), gitlinks)
    return rc, out.getvalue()


# Every family, and the number of cases it must produce. The selftest PRINTS
# totals; until this table existed it did not ASSERT them, and MEASURED at the
# merge gate: dropping `_table_parser_cases()` from the aggregate reported
# `selftest OK` with the parser count falling 711 -> 265, and dropping
# `_carrier_parser_cases()` reported OK at 565. Nothing said a family had gone.
# A count that is only printed is not a gate — it is the reassuring direction of
# the same class this whole file is about.
#
# A number here is a DELIBERATE pin, not a transcript: when a family legitimately
# grows, update it in the same commit that grows it and say by how much. That is
# the point — the change becomes visible instead of silent.
_CORPUS_FAMILIES = [
    ("_positive_cases", 469),
    ("_negative_cases", 223),
    ("_parser_cases", 119),
    ("_table_parser_cases", 446),
    ("_carrier_parser_cases", 146),
    ("_all_parser_cases", 711),
    ("_model_parser_cases", 150),
    ("_quote_model_cases", 32),
    ("_carrier_positive_cases", 119),
    ("_carrier_negative_cases", 8),
    ("_empty_pattern_negative_cases", 12),
    ("_set_member_positive_cases", 14),
    ("_set_member_negative_cases", 6),
]



# --------------------------------------------------------------------------
# THE CLASS ITSELF, not another instance of it.
#
# Nine times on this file a rule table has been found consumed at a site no case
# reached, so narrowing it left the whole selftest green while a real form
# flipped. Each was fixed one at a time; each fix was followed by another
# instance in the next review round. The instances differ, the shape does not:
# a table is DECLARED, is READ somewhere, and nothing anywhere asserts the
# relationship. Fixing them one per round is not convergence, it is a queue.
#
# This is the structural close. Every module-level table is classified exactly
# once, as either PINNED (a fixture compares it both ways, and something asserts
# a member is consumed) or RESIDUAL (honestly not covered yet). A table in
# NEITHER list fails the selftest, so a new one cannot arrive unclassified and an
# existing one cannot be quietly dropped from the ledger.
#
# THE RESIDUAL LIST IS NOT A COVERAGE CLAIM - it is the opposite: the written-down
# list of tables where the next instance of this class will be found. Shrinking it
# is the work; a name moved from RESIDUAL to PINNED needs a fixture AND a
# consumption assertion, both, or the move is a lie. What this guard buys is that
# the list can only shrink deliberately, and can never grow silently.
_PINNED_TABLES = {
    "ANSI_C_SIMPLE", "API_BODY_FLAGS", "API_METHOD_FLAGS", "CONTROL_WORDS",
    "DQ_ESCAPABLE", "FORGE_FAMILY_RULES", "FORGE_VALUE_OPTS", "GITLINK_MODE",
    "KNOWN_PROGRAMS", "LEAD_TRIM", "MARKUP_CHARS", "NON_EXECUTING",
    "PROSE_EXEMPT", "SEPARATOR_CHARS", "SHELL_MODELS", "SSH_CMD_KEYWORDS",
    "SSH_SEPARATOR_WS", "STRING_EXEC_CARRIERS", "STRING_EXEC_SPEC", "TAIL_TRIM",
    "VCS_EGRESS", "VCS_EGRESS_PAIRS", "VCS_PAIR_FAMILIES", "VCS_TERMINAL_OPTS",
    "VCS_VALUE_OPTS", "WRAPPER_SPEC", "WRAPPERS",
    # Production tables that happen to be underscore-named. Gate round 7c: the
    # inventory skipped every leading-underscore binding, so these two escaped
    # all three ledgers while the guard's own docstring promised "every
    # module-level table" — the guarantee was false and so was the count.
    "_SSH_VALUE_CHARS",
}
# The SELFTEST's own oracles — the independently written fixtures, the generated
# case lists, and these ledgers themselves. They are not production tables and
# are not pinned BY anything: they ARE the pinning. Listed explicitly rather than
# derived from a name pattern, because a derived exclusion is the hole this whole
# guard exists to close — `_X_FIXTURE` as a rule would let any table be exempted
# by renaming it.
#
# STATED RESIDUAL, because a guard that overclaims is the thing this file keeps
# finding: these ledgers stop a table from escaping SILENTLY — a new one with no
# entry fails, and a name in two ledgers fails. They cannot stop a DELIBERATE
# misclassification. Someone who adds a production table and also adds its name
# here passes, and no check in this file can tell that apart from a real oracle,
# because an oracle and a table are the same shapes and types. The scalar ledger
# is narrowed by a type check; this one has no equivalent. What the ledger buys
# is that misclassifying is now an explicit, reviewable edit to a named list
# instead of an omission nobody can see — which is the whole difference between
# a residual and a blind spot.
_SELFTEST_ORACLES = {
    "_SELFTEST_ORACLES",
    "_A",
    "_ANSI_C_SIMPLE_FIXTURE",
    "_AP",
    "_API_BODY_FLAGS",
    "_API_BODY_FLAG_CASES",
    "_API_METHOD_FLAGS",
    "_API_METHOD_FLAG_CASES",
    "_CARRIER_BARE_FLAGS",
    "_CARRIER_CLUSTER_PREFIX",
    "_CARRIER_OPTIONAL_SHORT_CHARS",
    "_CARRIER_POSITIONALS",
    "_CARRIER_SHORT_VALUE_CHARS",
    "_CARRIER_VALUE_OPTS",
    "_CONTROL_WORDS_FIXTURE",
    "_CORPUS_FAMILIES",
    "_DC",
    "_DQ_ESCAPABLE_FIXTURE",
    "_EMITTER_CASES",
    "_EMPTY_PATTERN_OPENERS",
    "_EMPTY_PATTERN_PREFIXES",
    "_EXPANSION_NON_VALUE_OPS",
    "_EXPANSION_REPLACE_OPS",
    "_EXPANSION_VALUE_OPS",
    "_FORGE_ACTION_SHORT_CHARS",
    "_FORGE_ACTION_VALUE_OPTS",
    "_FORGE_API_SHORT_CHARS",
    "_FORGE_FAMILIES",
    "_FORGE_FAMILY_EXCLUDED",
    "_FORGE_GLOBAL_SHORT_CHARS",
    "_FORGE_GLOBAL_VALUE_OPTS",
    "_FORGE_PR_MUTATIONS",
    "_FORGE_PR_NON_MUTATIONS",
    "_G",
    "_GITLINK_MODE_FIXTURE",
    "_K",
    "_KNOWN_PROGRAMS_FIXTURE",
    "_LEAD_TRIM_FIXTURE",
    "_LFS",
    "_MARKUP_CHARS_FIXTURE",
    "_NON_EXECUTING",
    "_P",
    "_P4",
    "_PFLAG_FALSE",
    "_PINNED_TABLES",
    "_PP",
    "_PROSE_EXEMPT_FIXTURE",
    "_R",
    "_REDUNDANT_MEMBERS",
    "_REL",
    "_REPO",
    "_RESIDUAL_TABLES",
    "_SCALAR_CONSTANTS",
    "_SEPARATOR_CASES",
    "_SEPARATOR_CHARS",
    "_SEPARATOR_NAMES",
    "_SHELL_BARE_PLUS",
    "_SHELL_FIRST_OPERAND",
    "_SHELL_LETTER_ARITY",
    "_SHELL_LONG_VALUE_OPTS",
    "_SHELL_NAME_MODELS",
    "_SHELL_PLUS_DASH",
    "_SM",
    "_SSH_CMD_KEYWORDS",
    "_SSH_KEYWORD_PREFIXES",
    "_SSH_NON_SEPARATORS",
    "_SSH_PLAIN_KEYWORDS",
    "_SSH_SEPARATORS",
    "_SSH_SEPARATOR_WS",
    "_SSH_VALUE_CHARS_FIXTURE",
    "_STRING_EXEC_CARRIERS",
    "_STRING_EXEC_CMD_OPTS",
    "_STRING_EXEC_DESTINATIONS",
    "_STRING_EXEC_TERMINAL",
    "_SUB",
    "_SVN",
    "_TAIL_TRIM_FIXTURE",
    "_V",
    "_VCS_ALIAS_MAX_HOPS",
    "_VCS_ALIAS_SHELL_PREFIX",
    "_VCS_ATTACHED_ONLY_OPTS",
    "_VCS_EGRESS_FIXTURE",
    "_VCS_GLOBAL_VALUE_OPTS",
    "_VCS_PAIRS",
    "_VCS_PAIR_ATTACHED_ONLY_OPTS",
    "_VCS_PAIR_EXCLUDED",
    "_VCS_PAIR_OPTS",
    "_VCS_TERMINAL_OPTS",
    "_WS_NAMES",
}
# Not tables: bounded-walk limits, carried here so the ledger covers every public
# uppercase name and the guard needs no type filter to exclude them.
_SCALAR_CONSTANTS = {"EXPANSION_MAX_DEPTH", "VCS_ALIAS_MAX_HOPS"}
_RESIDUAL_TABLES = {
    # Read at two carrier rows and compared against no independent fixture;
    # the ssh terminal carve-out asserts BEHAVIOUR through it but nothing pins
    # its membership. Recorded rather than claimed.
    "_SSH_TERMINAL_OPTS",
    "ALIAS_BOUND_FORM",
    "API_SHORT_VALUE_CHARS",
    "API_SUB",
    "DCOMMIT",
    "ENV_SPLIT_CHAR",
    "ENV_SPLIT_OPTS",
    "EVAL_WRAPPERS",
    "EXPANSION_NON_VALUE_OPS",
    "EXPANSION_REPLACE_OPS",
    "EXPANSION_VALUE_OPS",
    "FORGE",
    "FORGE_ACTION_SHORT_VALUE_CHARS",
    "FORGE_ACTION_VALUE_OPTS",
    "FORGE_COND_DESTINATION",
    "FORGE_COND_PUSH_FLAG",
    "FORGE_SHORT_VALUE_CHARS",
    "LFS",
    "P4",
    "PACK",
    "PFLAG_FALSE",
    "PRE_PUBLISH",
    "PR_MUTATIONS",
    "PR_SUB",
    "PUBLISH",
    "RELEASE",
    "REPO",
    "REPO_CREATE_PUSH_FLAGS",
    "SHELLS",
    "SHELL_ATTACHED_OR_NEXT",
    "SHELL_ATTACHED_OR_NEXT_NONOPT",
    "SHELL_BARE_PLUS",
    "SHELL_COMMAND_CHAR",
    "SHELL_FIRST_OPERAND",
    "SHELL_FIRST_OPERAND_COMMAND",
    "SHELL_FIRST_OPERAND_FILE",
    "SHELL_LONG_VALUE_OPTS",
    "SHELL_NEXT",
    "SHELL_OPTION_ARITY",
    "SHELL_PLUSDASH_BARE_ENDS_OPTIONS",
    "SHELL_PLUSDASH_PARSE_THROUGH",
    "SHELL_PLUSDASH_REJECT",
    "SHELL_PLUS_DASH",
    "SHELL_PLUS_ENDS_OPTIONS",
    "SHELL_PLUS_SKIP",
    "SUBMIT",
    "SUBTREE",
    "SVN",
    "SVN_BRANCH",
    "SVN_COMMIT_DIFF",
    "SVN_SET_TREE",
    "SVN_TAG",
    "VCS",
    "VCS_ALIAS_PREFIX",
    "VCS_ALIAS_SHELL_PREFIX",
    "VCS_PAIR_VALUE_OPTS",
    "WRAPPER_OPTIONAL_SHORT_CHARS",
    "WRAPPER_SHORT_VALUE_CHARS",
}


def _interpreter_globals() -> tuple[set[str], dict[str, tuple[str, object]]]:
    """The names CPython installs in THIS module's namespace — and only those.

    Returned as two halves, because they are held to account differently:

    * UNCONDITIONAL — always present. `_every_table_is_classified` fails on one
      that is not in `globals()`, so every entry here is exercised and a name the
      interpreter does not install cannot be added back quietly.
    * CONDITIONAL — present only in some runs, each with the reason and a value
      of the type CPython gives it. `_exclusions_are_exercised` uses that value
      to create the binding and assert the guard tolerates it.

    `__conditional_annotations__` is gated on the running interpreter, not
    excluded outright: only 3.14+ installs it (PEP 649), so on an older one
    naming it would be an exclusion for something that cannot exist — a hiding
    place, the exact defect this whole round is closing. Because the exercise
    probe reads this same dict, the older interpreter neither excludes the name
    nor manufactures a binding for it, and a table spelled that way there is
    caught by the ordinary inventory. `__annotations__` stays on both: 3.13 and
    earlier install it for an annotated module, and 3.14 caches it into the
    module dict the first time anything reads `module.__annotations__`.

    `__annotate__`, the other half of PEP 649, is deliberately NOT named: it is a
    function, so the code-object filter already excludes it, and naming it would
    add a hiding place for a table the type filter cannot reach.
    """
    unconditional = {
        "__name__", "__doc__", "__package__", "__loader__", "__spec__",
        "__file__", "__cached__", "__builtins__",
    }
    conditional: dict[str, tuple[str, object]] = {
        "__annotations__": ("a module-level annotation, or any read of "
                            "`module.__annotations__`", {}),
        "__warningregistry__": ("a warning raised while this module is "
                                "imported", {"version": 0}),
    }
    if sys.version_info >= (3, 14):
        conditional["__conditional_annotations__"] = (
            "a module-level annotation, on 3.14+ (PEP 649)", {0})
    return unconditional, conditional


def _every_table_is_classified() -> list[str]:
    """No module-level table may be absent from every ledger.

    Two claims, and the second is what makes the first true: every module-level
    DATA binding must be uppercase (callables and imported modules excepted by
    type, not by name), and every uppercase binding must appear in exactly one
    ledger. Without the first, the second only covers the tables that happened
    to follow the convention.

    This is the guard the nine one-at-a-time fixes did not add. It does not make
    a residual table safe; it makes an UNCLASSIFIED one impossible, which is the
    only part that was silent.
    """
    problems: list[str] = []
    # NO TYPE FILTER. The first version of this guard inventoried only
    # set/frozenset/dict/str/tuple/list, so a table of any other runtime type —
    # a mapping proxy, any other Mapping or Sequence implementation, a bytes
    # table — was invisible to the very check written to make tables visible
    # (measured at gate round 5c with a MappingProxyType). A guard with a
    # allow-list of types has the shape of the defect it exists to close, so it
    # has none: every public uppercase binding is classified, scalars included.
    # THE NAMING CONVENTION IS PART OF THE GUARD, not decoration. Gate round 8c:
    # the inventory selected `name.isupper()`, so a lowercase or mixed-case
    # module-level table evaded all four ledgers with no deliberate act at all —
    # while the docstring above claimed to cover every one. A guard whose reach
    # is decided by a naming convention has to ENFORCE that convention, or the
    # convention is just where the exception hides.
    #
    # So: every module-level data binding is inventoried first, and one that is
    # not uppercase fails on that alone. Callables and imported modules are not
    # data and are excluded by what they ARE, not by what they are called.
    # `callable()` is NOT the data/code boundary — gate round 9c: a callable dict
    # subclass, a class carrying rule data, and a `functools.partial` wrapping a
    # lookup set all satisfied `callable()` and vanished from the inventory. The
    # boundary is the CODE OBJECT: functions, builtins and imported modules are
    # what this file defines as code; everything else at module level is data,
    # a class that carries a table included.
    import types as _types
    _CODE = (_types.FunctionType, _types.BuiltinFunctionType, _types.ModuleType)
    # Exclude the INTERPRETER's own globals by NAME, explicitly — not every
    # dunder-prefixed name. Gate round 10c: `not name.startswith("__")` meant a
    # module-level `__PRIVATE_RULE_TABLE` evaded both inventory passes. Same shape
    # as every earlier hole in this guard: a pattern used as an exclusion is a
    # place to hide, and only an enumerated list has no such place.
    #
    # ROUND 11: AN ENUMERATED LIST HAS NO PLACE TO HIDE ONLY IF EVERY ENTRY IS A
    # NAME THE INTERPRETER REALLY INSTALLS HERE. The first spelling of this list
    # was wrong in both directions at once. It named `__all__`, `__version__`,
    # `__dict__`, `__debug__` and `__path__` — CPython installs none of those in
    # this module's namespace, and `__all__`/`__version__` are ordinary things an
    # author writes — so each was an exact hiding place, this file's own defect
    # class wearing a list instead of a pattern. And it MISSED two globals the
    # interpreter installs CONDITIONALLY, so an ordinary maintenance edit turned
    # the gate red on a name that has nothing to do with what this lint checks: a
    # module-level annotation installs `__conditional_annotations__` (a set, PEP
    # 649, 3.14+; `__annotations__` on 3.13 and earlier), and a warning raised
    # while this module is imported installs `__warningregistry__` (a dict).
    # Neither is a code object, so both reached the inventory and failed it.
    #
    # So the set is split by WHEN the interpreter installs the name, and both
    # halves are held to account. An UNCONDITIONAL entry must be in `globals()`
    # right now — the loop below fails on one that is not, which is what makes
    # each of those entries exercised and what stops a non-global name from being
    # quietly added back. A CONDITIONAL entry cannot be exercised that way, so it
    # carries its reason and is exercised by `_exclusions_are_exercised()`, which
    # creates the binding CPython would create and asserts this guard tolerates
    # it — and, in the same breath, that it still catches a table under a name
    # that is not excluded at all. Both halves come from `_interpreter_globals()`
    # so the guard and its exercise cannot drift.
    _INTERPRETER_GLOBALS, _CONDITIONAL_INTERPRETER_GLOBALS = _interpreter_globals()
    for name in sorted(_INTERPRETER_GLOBALS - set(globals())):
        problems.append("%r is excluded from the inventory as an interpreter "
                        "global but is not in globals() — an exclusion naming "
                        "something the interpreter does not install is a place "
                        "to hide a table, not an exclusion; drop it, or move it "
                        "to the conditional set with the reason it is sometimes "
                        "absent" % name)
    _EXCLUDED = _INTERPRETER_GLOBALS | set(_CONDITIONAL_INTERPRETER_GLOBALS)
    data = {
        name: value for name, value in globals().items()
        if name not in _EXCLUDED and not isinstance(value, _CODE)
    }
    for name in sorted(n for n in data if not n.isupper()):
        problems.append("module-level data binding %r is not UPPERCASE — the "
                        "ledger identifies tables by that convention, so a "
                        "lower-case one would evade every ledger silently; "
                        "rename it, or make it a local" % name)
    live = set(data)
    for name in sorted(live - _PINNED_TABLES - _RESIDUAL_TABLES - _SCALAR_CONSTANTS - _SELFTEST_ORACLES):
        problems.append("table %r is in neither the pinned nor the residual "
                        "ledger - classify it: pin it with an independent "
                        "fixture AND a consumption assertion, or record it as a "
                        "residual" % name)
    for name in sorted((_PINNED_TABLES | _RESIDUAL_TABLES | _SCALAR_CONSTANTS
                        | _SELFTEST_ORACLES) - live):
        problems.append("table %r is in a ledger but no longer exists - a "
                        "ledger that names a table nobody has is not tracking "
                        "anything" % name)
    # EXACTLY one classification each, checked PAIRWISE over all three ledgers.
    # Gate round 6c: only pinned-vs-residual was compared, so `_SCALAR_CONSTANTS`
    # was a third door — a real table added to it was accepted with no pinned or
    # residual entry at all, laundering it past the accountability the other two
    # ledgers exist to enforce. A guard with an unchecked third list has the same
    # shape as the tables it polices.
    _LEDGERS = (("pinned", _PINNED_TABLES), ("residual", _RESIDUAL_TABLES),
                ("scalar", _SCALAR_CONSTANTS), ("selftest-oracle", _SELFTEST_ORACLES))
    for i, (a_name, a) in enumerate(_LEDGERS):
      for b_name, b in _LEDGERS[i + 1:]:
        for name in sorted(a & b):
            problems.append("%r is in BOTH the %s and %s ledgers, so its status "
                            "is whatever the reader assumed" % (name, a_name, b_name))
    # And the scalar ledger must hold only scalars, or it becomes the place a
    # table goes to avoid being classified as one.
    for name in sorted(_SCALAR_CONSTANTS):
        value = globals().get(name)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            problems.append("%r is in the scalar ledger but holds a %s — the "
                            "scalar ledger is not a place to put a table"
                            % (name, type(value).__name__))
    return problems


def _exclusions_are_exercised() -> list[str]:
    """Every name the inventory excludes is exercised by something.

    Gate round 11. Ten rounds of this file say a guard's exclusion is where the
    next defect lives, and an exclusion NO CASE EXERCISES is indistinguishable
    from one that is wrong: nothing fails when it is deleted, and nothing fails
    when a table is bound under it. `_every_table_is_classified` exercises its
    UNCONDITIONAL exclusions itself — an entry not in `globals()` fails there.
    This exercises the CONDITIONAL ones, which by definition are absent in an
    ordinary run: each binding is created with the type CPython gives it, and the
    guard must ignore it.

    `__builtins__` is exercised here too, for a reason worth stating: it is
    always in `globals()`, but it is the builtins MODULE when this file is run as
    a script and the builtins DICT when it is imported. Only the dict form
    reaches the inventory (a module is a code object), so under `--selftest`
    alone its entry looks redundant. The dict form is probed below, which is what
    makes that entry load-bearing rather than decorative.

    Tolerance proves nothing on its own — a guard that tolerates everything would
    pass every probe above — so the last probe is the opposite direction: a table
    bound under a name that is excluded NOWHERE must still be reported.

    RESIDUAL, stated: nothing here catches this function itself being emptied.
    That is the guard-of-the-guard regress every checker in this file stops at,
    and buying one more level would cost another guard that overclaims.
    """
    import builtins as _bi
    problems: list[str] = []
    g = globals()
    # THE PROBE LIST IS STATED INDEPENDENTLY, and then asserted equal to the
    # ledger. Deriving it from `_interpreter_globals()` was tried first and is
    # wrong in a way worth recording: a derived probe disappears with the entry
    # it was supposed to exercise, so deleting a conditional exclusion left the
    # selftest green — the exercise evaporated exactly when it was needed, which
    # is this file's defect class one more time. Two independent statements plus
    # an equality check give both properties at once: an entry deleted from the
    # ledger is still probed and still fails, and a probe for a name the ledger
    # does not exclude is caught by the check below rather than blessing it.
    #
    # The version gate is repeated here for the same reason it exists there: on
    # an interpreter that cannot install `__conditional_annotations__` the name
    # must be neither excluded nor manufactured, or the probe would be the only
    # reason it looked tolerated.
    probes = [("__annotations__", {}),
              ("__warningregistry__", {"version": 0})]
    if sys.version_info >= (3, 14):
        probes.append(("__conditional_annotations__", {0}))
    _unconditional, _conditional = _interpreter_globals()
    if {n for n, _v in probes} != set(_conditional):
        problems.append("the conditional-exclusion ledger %r and the probes "
                        "that exercise it %r name different sets — an exclusion "
                        "the probes do not reach is unexercised, and a probe "
                        "the ledger does not carry manufactures a binding to "
                        "bless a name nothing excludes"
                        % (sorted(_conditional), sorted(n for n, _v in probes)))
    probes.append(("__builtins__", dict(vars(_bi))))
    for name, value in probes:
        # A conditional global may ALREADY be bound — a module-level annotation
        # or an import-time warning does that, and `__builtins__` is always
        # bound. Then reality is the probe: assert the guard tolerates what is
        # actually there. Reporting the collision instead would turn the gate red
        # on exactly the ordinary edit this entry exists to tolerate.
        present = name in g
        before = g.get(name)
        # Bind INSIDE the try, so no path — an asynchronous exception included —
        # can leave a fabricated global behind; and restore an originally-absent
        # name with `pop`, which cannot raise on a binding already gone.
        try:
            if not present:
                g[name] = value
            reported = [p for p in _every_table_is_classified() if repr(name) in p]
            if not reported and present and not isinstance(before, type(value)):
                # probe the OTHER shape this name takes, then put the real one
                # back — `__builtins__` as a dict is the imported-module form.
                g[name] = value
                reported = [p for p in _every_table_is_classified()
                            if repr(name) in p]
        finally:
            if present:
                g[name] = before
            else:
                g.pop(name, None)
        if reported:
            problems.append("the conditional interpreter global %r (%s) is "
                            "reported by the ledger guard, so an ordinary "
                            "maintenance edit turns this gate red on a name "
                            "that has nothing to do with what the lint checks: "
                            "%s" % (name, type(value).__name__, reported[0]))
    probe = "__EXCLUSION_NON_VACUITY_PROBE__"
    if probe in g:
        problems.append("%r is already bound, so the non-vacuity probe below "
                        "would assert nothing" % probe)
    else:
        try:
            g[probe] = {"push", "publish"}
            reported = [p for p in _every_table_is_classified() if repr(probe) in p]
        finally:
            g.pop(probe, None)
        if not reported:
            problems.append("a module-level table bound as %r was NOT reported "
                            "— the guard tolerating the interpreter's own "
                            "globals proves nothing if it tolerates everything"
                            % probe)
    return problems


def _corpus_is_whole() -> list[str]:
    """Every family is present, the declared size, and uniquely named.

    Cardinality alone would not catch a family swapped for another of the same
    size, so the aggregates are additionally checked to be exactly the ORDERED
    concatenation of the families they are built from — no number involved.
    """
    problems: list[str] = []
    for name, want in _CORPUS_FAMILIES:
        got = len(globals()[name]())
        if got != want:
            problems.append("family %s() produced %d case(s), the pin says %d "
                            "— update the pin in the commit that changes it"
                            % (name, got, want))
    def names(fn):
        return [case[0] for case in fn()]
    if names(_all_parser_cases) != (names(_parser_cases)
                                    + names(_table_parser_cases)
                                    + names(_carrier_parser_cases)):
        problems.append("the parser aggregate is not exactly its three "
                        "families in order — a family is missing, reordered "
                        "or duplicated")
    for label, aggregate, tail in (
            ("positive", _positive_cases,
             [_carrier_positive_cases, _set_member_positive_cases]),
            ("negative", _negative_cases,
             [_empty_pattern_negative_cases, _set_member_negative_cases])):
        want: list[str] = []
        for fn in tail:
            want += names(fn)
        if names(aggregate)[-len(want):] != want:
            problems.append("the %s aggregate does not end with %s — an "
                            "appended family was dropped or reordered"
                            % (label, [fn.__name__ for fn in tail]))
    for label, fn in (("positive", _positive_cases),
                      ("negative", _negative_cases),
                      ("parser", _all_parser_cases),
                      ("shell-model", _model_parser_cases),
                      ("quote-model", _quote_model_cases)):
        seen = names(fn)
        dupes = sorted({n for n in seen if seen.count(n) > 1})
        if dupes:
            problems.append("%s case name(s) %r are used more than once, so "
                            "one case's failure names another" % (label, dupes))
    return problems


def selftest() -> int:
    failures = 0
    for problem in _every_table_is_classified():
        print("SELFTEST FAIL: table ledger: %s" % problem, file=sys.stderr)
        failures += 1
    for problem in _exclusions_are_exercised():
        print("SELFTEST FAIL: inventory exclusion: %s" % problem, file=sys.stderr)
        failures += 1
    for problem in _corpus_is_whole():
        print("SELFTEST FAIL: corpus incomplete: %s" % problem, file=sys.stderr)
        failures += 1
    for problem in _identities_are_right():
        print("SELFTEST FAIL: rule-table identity wrong: %s" % problem,
              file=sys.stderr)
        failures += 1
    for problem in _tables_are_pinned():
        print("SELFTEST FAIL: rule-table coverage drift: %s" % problem,
              file=sys.stderr)
        failures += 1
    for problem in _scan_paths_reports_what_it_read():
        print("SELFTEST FAIL: scan reporting: %s" % problem, file=sys.stderr)
        failures += 1
    if failures:
        print("SELFTEST: %d failure(s)." % failures, file=sys.stderr)
        return 1
    for name, lines, expected in _positive_cases():
        found = scan_text("\n".join(lines))
        if not found:
            print("SELFTEST FAIL: positive case '%s' produced no finding" % name,
                  file=sys.stderr)
            failures += 1
            continue
        if found[0][0] != expected:
            print("SELFTEST FAIL: positive case '%s' reported line %d, expected %d"
                  % (name, found[0][0], expected), file=sys.stderr)
            failures += 1
    for name, lines in _negative_cases():
        found = scan_text("\n".join(lines))
        if found:
            print("SELFTEST FAIL: negative case '%s' produced %r"
                  % (name, found), file=sys.stderr)
            failures += 1
    for name, toks, want_forms, want_nested, want_prog in _all_parser_cases():
        forms, nested, prog = analyze(list(toks))
        if forms != want_forms or nested != want_nested or prog != want_prog:
            print("SELFTEST FAIL: parser case '%s' gave forms=%r nested=%r "
                  "prog=%r, expected forms=%r nested=%r prog=%r"
                  % (name, forms, nested, prog, want_forms, want_nested,
                     want_prog), file=sys.stderr)
            failures += 1
    for name, text, want_toks in _quote_model_cases():
        got = tokenize(text, True)
        if got != want_toks:
            print("SELFTEST FAIL: quote-model case '%s' tokenized %r to %r, "
                  "expected %r" % (name, text, got, want_toks), file=sys.stderr)
            failures += 1
    for name, model, args, want_script in _model_parser_cases():
        found = _shell_script_index(list(args), model)
        # the INDEX-level answer only: the fallback's operand JOIN is asserted
        # end-to-end in _table_parser_cases, against `analyze`'s nested output
        got = None if found is None else args[found[0]]
        if got != want_script:
            print("SELFTEST FAIL: shell-model case '%s' resolved the script to "
                  "%r under model %r, expected %r"
                  % (name, got, model, want_script), file=sys.stderr)
            failures += 1
    # RE-RUN THE INVENTORY LAST. Gate round 9c: it ran once, before the cases, so
    # a module global bound lazily DURING the run — by any code the cases reach —
    # was never inventoried, and the suite reported its full counts and exited 0.
    # A namespace check that only looks before the work cannot see what the work
    # added, which is this file's own defect class pointed at its own timeline.
    for problem in _every_table_is_classified():
        print("SELFTEST FAIL: table ledger (post-run): %s" % problem,
              file=sys.stderr)
        failures += 1
    if failures:
        print("SELFTEST: %d failure(s)." % failures, file=sys.stderr)
        return 1
    print("selftest OK (%d positive, %d negative, %d parser, %d shell-model, "
          "%d quote-model cases)"
          % (len(_positive_cases()), len(_negative_cases()),
             len(_all_parser_cases()), len(_model_parser_cases()),
             len(_quote_model_cases())))
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--selftest":
        if len(argv) > 1:
            print(__doc__, file=sys.stderr)
            return 2
        return selftest()
    if argv:
        return scan_paths(argv)
    try:
        entries = tracked_entries()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print("PUSH-FORM-CHECK: cannot list tracked files: %s" % exc,
              file=sys.stderr)
        return 2
    return scan_paths([path for path, _ in entries],
                      gitlinks={path for path, is_link in entries if is_link})


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
