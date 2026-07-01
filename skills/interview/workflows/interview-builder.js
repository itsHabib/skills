export const meta = {
  name: 'interview-builder',
  description: 'Fan out one agent per section to draft deep, voice-tuned, story-eliciting interview questions, run a breadth critic for cross-cutting sections and gaps, and assemble a fillable, resumable interview.md. Parameterized via args.',
  phases: [
    { title: 'Draft questions', detail: 'one agent per section drafts deep questions in the expert voice' },
    { title: 'Critique + fill gaps', detail: 'breadth critic adds cross-cutting sections + per-section gap-fills' },
  ],
}

// args shape (all strings unless noted):
//   title          the interview title, e.g. "Intern talk series"
//   artifactNoun   what the captured answers become, e.g. "deck" (default "artifact")
//   profile        the SHARED block: who the expert is + their world
//   rules          the question-design rules (optional; a sensible default is used if absent)
//   spine          the throughline / connective thesis (optional)
//   sections       [ { id, title, promise, subTopics: [ { name, note } ] } ]
//   crossCutting   [ { section, focus, placement } ] placement "before" | "after" (default "after"); warm-up goes "before"

const A = args || {}
const TITLE = A.title || 'Interview'
const ARTIFACT = A.artifactNoun || 'artifact'
const PROFILE = A.profile || ''
const SPINE = A.spine || ''
const SECTIONS = A.sections || []
const CROSS = A.crossCutting || []

const DEFAULT_RULES = `- The goal is to make the expert talk. Favor questions answerable only with a story, an opinion, or a specific example from their career.
- Avoid generic LinkedIn-style questions. Avoid yes/no questions. Avoid questions that just restate the definition of the sub-topic.
- Ground a question in their actual world where it fits naturally; do not force it where it does not.
- Blunt or edgy framing is welcome where it matches their voice. Match their candor.
- Keep each question tight, one or two sentences.
- Never use em dashes. Use a normal hyphen or restructure the sentence.`
const RULES = A.rules || DEFAULT_RULES

const SECTION_SCHEMA = {
  type: 'object',
  properties: {
    sectionId: { type: 'string' },
    sectionTitle: { type: 'string' },
    subTopics: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          questions: { type: 'array', items: { type: 'string' } },
        },
        required: ['name', 'questions'],
      },
    },
  },
  required: ['sectionId', 'sectionTitle', 'subTopics'],
}

const CRITIC_SCHEMA = {
  type: 'object',
  properties: {
    crossCuttingQuestions: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          section: { type: 'string' },
          questions: { type: 'array', items: { type: 'string' } },
        },
        required: ['section', 'questions'],
      },
    },
    perSectionGapFills: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          sectionId: { type: 'string' },
          additionalQuestions: { type: 'array', items: { type: 'string' } },
        },
        required: ['sectionId', 'additionalQuestions'],
      },
    },
  },
  required: ['crossCuttingQuestions', 'perSectionGapFills'],
}

phase('Draft questions')
log(`drafting deep questions for ${SECTIONS.length} sections in parallel`)

const drafts = await parallel(SECTIONS.map((s) => () =>
  agent(
    `You are designing interview questions for an expert (referred to as "the expert") who is producing a ${ARTIFACT}. Produce deep, open-ended questions that pull out their STORIES, OPINIONS, and CONCRETE EXAMPLES, not textbook definitions they already know. They will answer in a brain-dump and the answers become the ${ARTIFACT} content.

SHARED CONTEXT ABOUT THE EXPERT:
${PROFILE}

THE SECTION YOU ARE COVERING:
Title: ${s.id} - ${s.title}
Promise / thesis: ${s.promise || ''}
Sub-topics (with their own shorthand notes):
${(s.subTopics || []).map((st, i) => `${i + 1}. ${st.name} - ${st.note || ''}`).join('\n')}

INTERVIEW DESIGN RULES:
${RULES}

For EACH sub-topic above, write 4 to 7 questions. Vary them across these types: a war-story prompt ("tell me about a time..."), a hot-take or unpopular-opinion prompt, a contrast prompt ("what separates someone who gets this from someone who does not"), a failure prompt ("when did this bite you, or what did you get wrong"), a tactical prompt ("what do you ACTUALLY do, step by step"), and a transmission prompt ("the one thing you would force the audience to internalize"). Address every question to the expert in the second person. Preserve the exact sub-topic names. Set sectionId to ${s.id}. Return through the structured output tool.`,
    { label: `draft:${s.id}`, phase: 'Draft questions', schema: SECTION_SCHEMA, effort: 'high' }
  )
))

phase('Critique + fill gaps')
log('running breadth critic over the full draft')

const forCritic = SECTIONS.map((s, i) => ({
  sectionId: s.id,
  title: s.title,
  subTopics: drafts[i] ? drafts[i].subTopics : [],
}))

const crossList = CROSS.map((c) => `- "${c.section}": ${c.focus || ''}`).join('\n')

const critic = await agent(
  `You are a completeness and breadth critic reviewing a draft interview question set for an expert who is producing a ${ARTIFACT} titled "${TITLE}".

SHARED CONTEXT ABOUT THE EXPERT:
${PROFILE}

${SPINE ? `THE THROUGHLINE / SPINE:\n${SPINE}\n` : ''}
DRAFT QUESTIONS PER SECTION (JSON):
${JSON.stringify(forCritic)}

Do two things:

1. crossCuttingQuestions: design questions that do NOT belong to any single section, grouped into exactly these sections (use these exact section names):
${crossList || '- (none requested)'}
   Write 5 to 8 questions per section, in the second person, story-eliciting. If no cross-cutting sections were requested, return an empty array.

2. perSectionGapFills: for each sectionId in the JSON, identify missing angles, thin sub-topics, or obvious follow-ups the drafter did not cover, and add 1 to 4 strong additional questions. If a section is already strong, return an empty additionalQuestions array for it. Use the exact sectionId values from the JSON.

Never use em dashes. Return everything through the structured output tool.`,
  { label: 'critic', phase: 'Critique + fill gaps', schema: CRITIC_SCHEMA, effort: 'high' }
)

let grand = 0
const renderGroups = (groups) => {
  const parts = []
  let n = 1
  for (const g of groups) {
    if (g.name) parts.push(`### ${g.name}`)
    for (const q of g.questions) {
      parts.push(`**Q${n}.** ${q}\n\n_Answer:_ \n`)
      n++
      grand++
    }
  }
  return parts.join('\n\n')
}

const cc = (critic && critic.crossCuttingQuestions) || []
const placementOf = (name) => {
  const explicit = CROSS.find((c) => c.section === name)
  if (explicit && explicit.placement) return explicit.placement
  if (/warm|who you are|background|origin|intro/i.test(name)) return 'before'
  return 'after'
}
const before = cc.filter((c) => placementOf(c.section) === 'before')
const after = cc.filter((c) => placementOf(c.section) === 'after')
const gapFills = (critic && critic.perSectionGapFills) || []

const sectionNames = []
before.forEach((c) => sectionNames.push(c.section))
SECTIONS.forEach((s) => sectionNames.push(`${s.id} - ${s.title}`))
after.forEach((c) => sectionNames.push(c.section))
const progress = sectionNames.map((nm) => `- [ ] ${nm}`).join('\n')

const out = []

out.push(`# ${TITLE} - interview

Working interview to capture the expert's real stories, opinions, and concrete examples for the ${ARTIFACT}. Fill answers inline under each "Answer:" line and come back any time. The structure lives in outline.md; this doc is where the CONTENT gets captured before it becomes the ${ARTIFACT}.

## How to use this doc

- Answer in your own words under each "Answer:" line. Brain-dump, because tangents are usually the best material.
- Skip any question that does not spark. Not every question needs an answer.
- Check a section off in Progress below as you go, so you can stop and resume.
- Add a "> Build note:" line under any answer to flag where it belongs in the ${ARTIFACT}.
- When a section has enough captured, say so and it becomes part of the ${ARTIFACT}.

## Progress

${progress}`)

for (const c of before) {
  out.push(`## ${c.section}\n\n_Status: not started_\n\n${renderGroups([{ name: null, questions: c.questions }])}\n\n---`)
}

for (let i = 0; i < SECTIONS.length; i++) {
  const s = SECTIONS[i]
  const d = drafts[i]
  const groups = []
  if (d && d.subTopics) groups.push(...d.subTopics)
  const gf = gapFills.find((g) => g.sectionId === s.id)
  if (gf && gf.additionalQuestions && gf.additionalQuestions.length) {
    groups.push({ name: 'More (deeper cuts)', questions: gf.additionalQuestions })
  }
  const body = groups.length ? renderGroups(groups) : '_(drafting failed for this section - rerun)_'
  out.push(`## ${s.id} - ${s.title}\n\n_${s.promise || ''}_\n\n_Status: not started_\n\n${body}\n\n---`)
}

for (const c of after) {
  out.push(`## ${c.section}\n\n_Status: not started_\n\n${renderGroups([{ name: null, questions: c.questions }])}\n\n---`)
}

const markdown = out.join('\n\n')

return { markdown, totalQuestions: grand, sectionsCovered: drafts.filter(Boolean).length }
