export const meta = {
  name: 'deck-synthesis',
  description: 'Turn captured interview answers into a reviewable per-section slide-spec for the deck adapter: one agent per section drafts slides from that section answers + build notes, then an editorial pass tightens voice, removes cross-section redundancy, and flags gaps. Parameterized via args.',
  phases: [
    { title: 'Draft slides', detail: 'one agent per section drafts slides from captured answers' },
    { title: 'Editorial pass', detail: 'tighten voice, dedupe across sections, flag gaps' },
  ],
}

// args shape:
//   title          deck title
//   profile        the voice source (who the expert is + how they talk)
//   sections       [ { id, title, promise, capturedMarkdown } ]
//                  capturedMarkdown = the section's filled Q&A block (with any "> Build note:" lines) lifted from interview.md.
//                  Only pass sections that have enough captured to synthesize.

const A = args || {}
const TITLE = A.title || 'Deck'
const PROFILE = A.profile || ''
const SECTIONS = (A.sections || []).filter((s) => s && s.capturedMarkdown && s.capturedMarkdown.trim())

const SLIDE_SCHEMA = {
  type: 'object',
  properties: {
    sectionId: { type: 'string' },
    sectionTitle: { type: 'string' },
    slides: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          bullets: { type: 'array', items: { type: 'string' } },
          speakerNotes: { type: 'string' },
          source: { type: 'string' },
        },
        required: ['title', 'bullets', 'speakerNotes'],
      },
    },
  },
  required: ['sectionId', 'sectionTitle', 'slides'],
}

const EDIT_SCHEMA = {
  type: 'object',
  properties: {
    sections: {
      type: 'array',
      items: SLIDE_SCHEMA,
    },
  },
  required: ['sections'],
}

const VOICE_RULES = `- Write titles and speaker notes in the expert's voice and candor, drawn from PROFILE. A blunt captured phrase makes a better title than a sanitized one.
- Build every slide from what was ACTUALLY said in the captured answers. Do not invent claims, do not smooth out the candor, do not swap a specific story for a generic principle.
- Bullets are phrases (3 to 5 per slide), not sentences. The story lives in the speaker notes.
- Honor any "> Build note:" line in the captured text - it says which slide an answer belongs on and why. A build note overrides default placement.
- If a slide needs a beat the answers do not cover, put "TODO: needs <what>" in the bullets rather than fabricating.
- Never use em dashes.`

phase('Draft slides')
log(`drafting slides for ${SECTIONS.length} captured sections in parallel`)

const drafts = await parallel(SECTIONS.map((s) => () =>
  agent(
    `You are turning an expert's captured interview answers into slides for a deck titled "${TITLE}". The captured answers are the ground truth; the slides must be built from them, in the expert's voice.

WHO THE EXPERT IS AND HOW THEY TALK (PROFILE):
${PROFILE}

THE SECTION:
${s.id} - ${s.title}
${s.promise ? `Promise / thesis of this section: ${s.promise}` : ''}

THE CAPTURED ANSWERS FOR THIS SECTION (raw, with any build notes):
${s.capturedMarkdown}

RULES:
${VOICE_RULES}

Open the section by stating its promise. Turn the strongest captured stories and hot-takes into their own slides; one good answer is usually one to three slides. Set sectionId to ${s.id}. For each slide, set "source" to the question number(s) it draws from. Return through the structured output tool.`,
    { label: `slides:${s.id}`, phase: 'Draft slides', schema: SLIDE_SCHEMA, effort: 'high' }
  )
))

const drafted = drafts.filter(Boolean)

phase('Editorial pass')
log('tightening voice, deduping across sections, flagging gaps')

const edited = await agent(
  `You are the editor of a deck titled "${TITLE}". You are given drafted slides for every section. Tighten them as a set.

WHO THE EXPERT IS AND HOW THEY TALK (PROFILE):
${PROFILE}

DRAFTED SLIDES PER SECTION (JSON):
${JSON.stringify(drafted)}

Do this:
- Make the voice consistent across all sections and true to PROFILE.
- Remove redundancy where two sections make the same point; keep the stronger slide.
- Tighten titles to be punchy and in the expert's voice; tighten bullets to phrases.
- Keep every "TODO: needs <what>" marker; do not paper over a real gap.
- Do not invent new claims that are not grounded in the drafted slides.
- Never use em dashes.

Return the full set of sections with their refined slides through the structured output tool.`,
  { label: 'editorial', phase: 'Editorial pass', schema: EDIT_SCHEMA, effort: 'high' }
)

const finalSections = (edited && edited.sections && edited.sections.length) ? edited.sections : drafted

const renderSection = (sec) => {
  const lines = [`# ${sec.sectionTitle} - slide spec`, '']
  let n = 1
  for (const sl of sec.slides || []) {
    lines.push(`### Slide ${n}: ${sl.title}`)
    for (const b of sl.bullets || []) lines.push(`- ${b}`)
    if (sl.speakerNotes) lines.push(`\nSpeaker notes: ${sl.speakerNotes}`)
    if (sl.source) lines.push(`\nSource: ${sl.source}`)
    lines.push('')
    n++
  }
  return lines.join('\n')
}

const slideSpecs = finalSections.map((sec) => ({
  sectionId: sec.sectionId,
  sectionTitle: sec.sectionTitle,
  markdown: renderSection(sec),
}))

const totalSlides = finalSections.reduce((acc, sec) => acc + ((sec.slides || []).length), 0)

return { slideSpecs, totalSlides, sectionsSynthesized: slideSpecs.length }
