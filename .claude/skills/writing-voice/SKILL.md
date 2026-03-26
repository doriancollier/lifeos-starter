---
name: writing-voice
description: Write messages and documents in the vault owner's authentic voice. Use when drafting emails, Slack messages, SMS texts, or any written communication on their behalf.
---

# Writing Voice Skill

Write messages and documents in {{user_first_name}}'s authentic voice. This skill activates when drafting emails, Slack messages, SMS texts, or any written communication on {{user_first_name}}'s behalf.

## When to Use

- Drafting emails (professional or personal)
- Writing Slack messages
- Composing SMS/text messages
- Creating documentation in first person
- Any written communication that should sound like {{user_first_name}}

## Core Voice Characteristics

### Tone
- **Direct and efficient** - gets to the point without excessive preamble
- **Warm but not effusive** - friendly without being over-the-top
- **Honest and realistic** - hedges appropriately ("we hope", "no promises")
- **Takes initiative** - "I'll go ahead and..." rather than asking permission for small things

### Sentence Structure
- Prefers shorter sentences
- Uses fragments naturally in casual contexts
- Mixes complete sentences with brief acknowledgments
- Natural roughness - not overly polished

### Punctuation Patterns
- **Ellipsis (...)** for trailing thoughts or pauses: "was away from computer, etc."
- **Triple exclamation (!!!)** for genuine excitement (rare, only when truly excited)
- **Double punctuation (!!, ??)** for emphasis in casual contexts
- **Often omits periods** at end of short replies
- **Never uses em dashes** - this is an anti-pattern

### Contractions
Always use contractions: I'm, don't, can't, we'll, he's, doesn't, they'll, haven't

## Context-Specific Profiles

> **Full examples**: See `writing-voice-examples.md` for complete message samples (if available).

[Configure these profiles based on your communication style:]

### SMS - Partner/Very Close

- [Configure casual communication patterns]
- Natural openers for longer messages
- Abbreviations used (e.g., "u" for "you")
- Expressive patterns
- Emoji usage (sparingly or frequently)

### SMS - Family

- Casual with care, gives context
- Follow-up questions show care
- Updates lead with key info

### SMS - Co-parent (if applicable)

- More structured, manages expectations
- Thorough explanations with context
- Clear next steps

### Slack - Close Colleagues

- **Greetings**: Configure typical greetings
- Use of nicknames and initials
- How to structure complex updates
- Expressions for approval/excitement

### Slack - Group Threads

- Tags people with @
- Explains thinking process
- Pragmatic decision-making

### Email - Close Collaborator

- **Opener**: Configure typical opener
- **Sign-off**: "- [initial]" or "- {{user_first_name}}"
- Bullet points for updates
- Brief, punchy sentences

### Email - Professional Contact (not close)

- **Opener**: Warm acknowledgment
- **Sign-off**: "- {{user_first_name}}"
- Brief and friendly

### Email - Semi-Formal (School staff, service providers)

- **Opener**: "Hi [Title] [Last Name]," or "Hi [First Name],"
- **Sign-off**: "- {{user_first_name}}"
- Brief but complete sentences

### Email - Cold/Institutional

- **Opener**: "Hello,"
- **Sign-off**: "Thank you!" (with exclamation)
- Clear purpose statement
- Direct ask

### Email - Cold Outreach (New Professional Contact)

- **Opener**: "Hi [Name],"
- **Sign-off**: "- {{user_first_name}}"
- Reference the connection
- Brief context on who you are

### Documentation (PRDs, guides, etc.)

- Clear headers and structure
- Bullet points for lists
- Direct statements
- No excessive hedging or preamble

## Signature Phrases

Use these naturally:
- "No worries" (acknowledgment/forgiveness)
- "Sounds good" / "That sounds good"
- "I dig it" (approval, casual contexts)
- "Awesome" (positive reaction)
- "Let me know"
- "heads up," (always with comma after)
- "Quick update:"
- "pretty [adjective]" (softener: "pretty flexible")
- "I'll go ahead and..."
- "etc." (natural trailing)
- "IMO" (in Slack)
- "Let me know if you have any feedback, thoughts, or questions" (preferred closing for work updates)
- "Been thinking about..." (soft opener for ideas)
- "Not married to it but wanted to get your take" (for uncertain ideas)
- "Does that still work?" (for confirmations)

## Anti-Patterns to AVOID

### AI Vocabulary (Never Use)
- "delve", "delving"
- "comprehensive"
- "crucial", "pivotal", "essential"
- "robust"
- "leverage" (as verb)
- "navigate" (metaphorically)
- "landscape", "realm"
- "multifaceted"
- "nuanced"
- "tapestry"
- "unleash"
- "embark"
- "foster"
- "harness"
- "spearhead"
- "streamline"
- "synergy"
- "at the intersection of"
- "a testament to"

### Corporate/Business Jargon (Never Use)
- "commoditized" / "commoditize" → say "cheap" or "everywhere"
- "exponentially" → say "way more"
- "at the forefront of" → just use action verbs ("builds", "creates")
- "depreciating" (non-financial) → say "losing value" or "not paying off"
- "ROI" (non-financial contexts) → say "payoff" or "return"
- "era of [disruption/change]" → cut preamble, lead with specifics
- "segment of one" → say "making things for one person"
- "reshaping" (AI is reshaping...) → say "changing"
- "profound disruption" → just state what's changing
- "forefront" → say "leading" or use action verbs

### AI Structural Tells
- **Em dashes (—)** - Almost never use these
- **"Moreover", "Furthermore", "In addition"** - too formal
- **"It's important to note that..."** - hedging preamble
- **"It's worth mentioning..."** - unnecessary
- **"In today's fast-paced world..."** - cliche opener
- **"In conclusion..."** - formulaic
- **"Let's dive in..."** - AI-ism
- Paragraphs of identical length
- Overly balanced arguments
- Perfect grammar with no natural roughness

### User-Specific Anti-Patterns

[Configure based on personal communication anti-patterns:]
- [Configure specific phrases to avoid]
- [Configure regional expressions to avoid]
- [Configure context-specific cautions]

## Quick Reference by Context

| Context | Greeting | Sign-off | Formality | Key Features |
|---------|----------|----------|-----------|--------------|
| SMS Partner | Configure | None | Casual | [Configure patterns] |
| SMS Family | Configure | None | Casual | Context-giving, open questions |
| SMS Co-parent | "Hi [Name]," | None | Respectful | Manages expectations |
| Slack Close | Configure | None | Casual-professional | Configure typical patterns |
| Slack Group | None | None | Professional | @tags, explains thinking |
| Email Close | Configure | "- [initial]" | Casual | Bullets, brief sentences |
| Email Professional | Warm opener | "- {{user_first_name}}" | Warm-professional | Brief |
| Email Semi-formal | "Hi [Name]," | "- {{user_first_name}}" | Polite | Brief but complete |
| Email Cold Outreach | "Hi [Name]," | "- {{user_first_name}}" | Warm-professional | Reference connection |
| Email Cold Institutional | "Hello," | "Thank you!" | Formal | Clear purpose, direct ask |

## Usage Instructions

When asked to write something for {{user_first_name}}:

1. **Identify the context** - Who is the recipient? What's the relationship?
2. **Match the profile** - Use the appropriate formality level and patterns
3. **Use signature phrases** - Incorporate natural expressions from the list
4. **Avoid anti-patterns** - Check against AI tells before finalizing
5. **Keep natural roughness** - Don't over-polish; leave some imperfection
6. **Check punctuation** - Use ellipsis for pauses, avoid em dashes
7. **Verify contractions** - Always use contractions (I'm, don't, etc.)

## Coaching Mode

Every message drafted is a coaching opportunity. The user's communication style has clear strengths but also growth edges.

### Known Growth Edges (Reference: `2-Areas/Personal/context.md`)

[Configure based on personal communication patterns:]

| Pattern | Risk | Growth Direction |
|---------|------|------------------|
| [Pattern 1] | [Risk] | [Growth Direction] |
| [Pattern 2] | [Risk] | [Growth Direction] |
| [Pattern 3] | [Risk] | [Growth Direction] |

### When Drafting Messages

**Default behavior:** Draft in {{user_first_name}}'s natural voice (preserve strengths).

**When to offer enhancement:** If the message involves:
- Close relationships ({{partner_name}}, family)
- Important professional moments (pitching ideas, difficult conversations)
- Situations where warmth or confidence would land better

**How to offer enhancement:**

```
[Natural version]

---

**Enhanced version** (adds [brief description]):
[Enhanced version]

The enhancement [one sentence explaining what it adds and why it might land better].
```

**Keep it light.** Don't lecture. One sentence of explanation, max.

### When Analyzing User's Writing

If asked to analyze something the user wrote:

1. **Acknowledge strengths first** - What's working well
2. **Identify patterns** - Connect to known tendencies (hedging, brevity, etc.)
3. **Offer one specific improvement** - Not a rewrite, just one targeted suggestion
4. **Frame as growth, not criticism** - "This could land even stronger if..."

### Integration with Daily Workflow

During `/daily:eod` reflection, if significant communication happened:
- Surface one communication highlight (strength demonstrated)
- Surface one opportunity (where warmth/confidence could have been added)

This is gentle, not exhaustive. The goal is awareness over time, not perfection in any single message.

## Enhancements

### Warmth Prompts

[Configure based on personality type.] When stakes are high, actively prompt for warmth:

**High-stakes communication triggers:**
- Messages to {{partner_name}} (especially during conflict or difficult conversations)
- Messages to {{child_name}} (especially around emotions or support)
- Difficult professional conversations (feedback, disagreements)
- Relationship repair attempts
- Moments requiring vulnerability

**When drafting high-stakes messages, surface these prompts:**

**Explicit Appreciation:**
- "Have you included explicit appreciation? {{partner_name}}/{{child_name}} may not infer it."
- "What specifically are you grateful for in this situation?"
- "Consider leading with appreciation before the ask or concern."

**Vulnerability:**
- "Is there space for vulnerability here? Could sharing your own uncertainty or feeling strengthen connection?"
- "Would admitting 'I don't have this figured out' or 'I'm worried about...' land better than the efficient version?"
- "Consider: 'I feel...' instead of 'I think...'"

**Warmth Without Losing Clarity:**
- "Could this land warmer without losing clarity?"
- "Add one sentence that acknowledges their experience or feelings."
- "Replace efficiency with presence: 'I'm here' > 'Let me know if you need anything'"

**Draft format for high-stakes messages:**
```
[Natural version - efficient, direct]

---

**Warmer version** (adds explicit appreciation/vulnerability):
[Version with warmth added]

This version [brief explanation of what emotional need it addresses].
```

### Relationship Communication (Partner and Child)

For messages to {{partner_name}} and {{child_name}} specifically, apply heightened awareness:

**For {{partner_name}}:**
- Default to the "warmer version" unless speed is critical
- Check for turning toward vs. turning away (is this responding to their bid for connection?)
- Ensure appreciation is explicit, not assumed
- Watch for efficiency that reads as dismissal
- For shared business: Keep work context separate from relationship context
- Reference: 5:1 ratio awareness (are you making a deposit or withdrawal?)

**For {{child_name}}:**
- Listen more than lecture - even in text
- Ask questions instead of giving directives
- Validate before problem-solving
- Match energy level appropriately
- Support with clear, simple structure
- Avoid shame-inducing language about responsibilities

**Specific patterns to watch:**

| Pattern | Risk | Better Approach |
|---------|------|-----------------|
| Short responses to emotional content | Feels dismissive | Acknowledge the feeling first |
| Problem-solving immediately | Skips connection | "That sounds [hard/frustrating/etc]. Do you want to talk it through or want ideas?" |
| Smoothing over concerns | Masks what matters | "I hear you. Let's figure this out." |
| Instructions without context | Feels controlling | Explain the why |

### Four Horsemen Awareness

When drafting or analyzing communication, flag potential Four Horsemen patterns:

**The Four Horsemen (predict relationship breakdown with 94% accuracy):**

| Horseman | Signs in Writing | Alternative |
|----------|-----------------|-------------|
| **Criticism** | "You always...", "You never...", attacking character | "I feel [feeling] when [behavior]. I need [specific request]." |
| **Contempt** | Sarcasm, mockery, eye-rolling language, superiority | Express appreciation; assume good intent |
| **Defensiveness** | "Yes, but...", counter-complaints, victim stance | Own your part: "You're right about [X]. My part in this was..." |
| **Stonewalling** | Non-response, minimal engagement, shutting down | "I need a break to process. Can we continue in [time]?" |

**When to flag:**
- Any message that contains "You always" or "You never"
- Messages with sarcastic or dismissive tone
- Responses that only defend without acknowledging partner's point
- Very short responses to emotional topics (may indicate stonewalling)

**How to flag:**
```
Note: This message contains a potential [Horseman] pattern ("You always...").
Consider reframing: "I feel [X] when [specific situation]."
```

**Special consideration for communication patterns:**
- Efficiency can read as stonewalling when partner needs engagement
- Logical rebuttals can feel like defensiveness
- Directness can land as criticism if missing warmth buffer
- Wanting to fix things quickly can dismiss emotional needs

### Integration with Coaching Prompts

During communication drafting, integrate with core coaching behaviors:

**Before sending to {{partner_name}}:**
- "Did you turn toward their bid for connection or just respond to the content?"
- "Are you treating {{partner_name}} as A-priority or just efficient output?"
- "Is this work conversation or relationship conversation? Match the mode."

**Before sending to {{child_name}}:**
- "Are you being the present parent or the busy provider in this message?"
- "Does this message listen or lecture?"
- "Would this land better with explicit support or just information?"

**For difficult conversations:**
- "What fear are you avoiding by keeping this efficient?"
- "What's your part in this? Have you acknowledged it?"
- "Is this courage AND love, or just one?"
