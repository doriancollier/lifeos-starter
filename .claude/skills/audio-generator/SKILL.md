---
name: audio-generator
description: Generate speech audio using ElevenLabs. Activates when user mentions audio generation, text-to-speech, daily practice audio, or ElevenLabs.
---

# Audio Generator

Generate speech audio using the ElevenLabs MCP server for text-to-speech, voice cloning, and audio playback.

## When to Activate

- User asks to generate audio, create audio, or use text-to-speech
- User mentions daily practice audio, affirmation audio, or morning ritual audio
- User mentions ElevenLabs or voice generation
- Working on projects that require audio output

## Pronunciation Handling (CRITICAL)

**Before calling `mcp__ElevenLabs__text_to_speech`, always apply pronunciation replacements.**

ElevenLabs doesn't support PLS lexicon files, so we handle pronunciation via text replacement before sending to the API.

### Pronunciation File

Location: `.claude/skills/audio-generator/pronunciation.yaml`

```yaml
replacements:
  {{child_name}}: "Deeus"              # Son's name - pronounced "Day-us"
```

### How to Apply

1. **Before any TTS call**, read `pronunciation.yaml`
2. Apply all replacements to the text (case-sensitive)
3. Send the modified text to ElevenLabs

```python
# Example workflow:
original_text = "[calm] {{child_name}} deserves a solid foundation."

# After applying pronunciation.yaml replacements:
modified_text = "[calm] Deeus deserves a solid foundation."

# Send modified_text to ElevenLabs
mcp__ElevenLabs__text_to_speech(text: modified_text, ...)
```

### Adding New Pronunciations

When ElevenLabs mispronounces a word:
1. Edit `.claude/skills/audio-generator/pronunciation.yaml`
2. Add: `OriginalWord: "PhoneticSpelling"`
3. The phonetic spelling should be how you want it pronounced

**Note**: For project-specific audio (like Daily Practice), the source files may already have phonetic spellings baked in. The pronunciation.yaml is the canonical reference for how words should be spelled for TTS.

---

## Common Pitfalls (Read First!)

### 1. Always Specify Model Explicitly

**The `model_id` parameter defaults to `eleven_multilingual_v2` if omitted.** This means:
- Audio tags like `[calm]`, `[excited]` will be ignored (v2 doesn't support them)
- SSML breaks will work (v2 supports them)

If you want v3 features (audio tags), you MUST pass `model_id: "eleven_v3"` explicitly.

```python
# WRONG - will use v2, audio tags ignored
mcp__ElevenLabs__text_to_speech(
  text: "[calm] Hello world",
  voice_name: "Will"
)

# CORRECT - explicitly uses v3
mcp__ElevenLabs__text_to_speech(
  text: "[calm] Hello world",
  voice_name: "Will",
  model_id: "eleven_v3"  # ← Required for audio tags!
)
```

### 2. Library Voices Must Be Added to Your Account

There are two voice sources:
- **Personal voices** (`search_voices`) — Already in your account, ready to use
- **Library voices** (`search_voice_library`) — Public library, must be added first

If you find a voice via `search_voice_library`, you must add it to your account in the ElevenLabs UI before using it with `text_to_speech`. Otherwise you'll get `voice_not_found` errors.

### 3. Prefer voice_id Over voice_name

Voice names can fail if they don't match exactly. Voice IDs are more reliable:

```python
# Less reliable - name must match exactly
voice_name: "Will - Relaxed Optimist"

# More reliable - ID always works if voice is in your library
voice_id: "bIHbv24MWmeRgasZH58o"
```

When testing new voices, use `search_voices` to get both name and ID, then use the ID for generation.

---

## Model Selection

### Available Models

| Model | Quality | Latency | Cost | Best For |
|-------|---------|---------|------|----------|
| **eleven_v3** | Highest | High | 1 credit/char | Expressive content, audiobooks, emotional delivery |
| **eleven_multilingual_v2** | Very High | Medium | 1 credit/char | Proven quality, long-form, multilingual |
| **eleven_turbo_v2_5** | High | ~250ms | 0.5 credit/char | Balance of quality and speed |
| **eleven_flash_v2_5** | Good | ~75ms | 0.5 credit/char | Real-time, conversational AI, bulk |

### When to Use Each Model

| Use Case | Model | Why |
|----------|-------|-----|
| Daily practice, affirmations | **eleven_v3** | Maximum emotional expressiveness |
| Audiobooks, narration | **eleven_v3** | Audio tags for sighs, whispers, emotion |
| Quick TTS, bulk generation | **eleven_multilingual_v2** | Stable, proven, higher char limit |
| Real-time applications | **eleven_flash_v2_5** | Ultra-low latency |
| Multilingual content | **eleven_multilingual_v2** | 29 languages with consistent voice |

### Model Constraints

| Model | Character Limit | SSML Support | Audio Tags | Stability Values |
|-------|-----------------|--------------|------------|------------------|
| **eleven_v3** | 5,000 | ❌ NO | ✅ YES | **Discrete**: 0.0, 0.5, 1.0 only |
| **eleven_multilingual_v2** | 10,000 | ✅ YES | ❌ NO | Continuous 0-1 |
| **eleven_turbo_v2_5** | 40,000 | ✅ YES | ❌ NO | Continuous 0-1 |
| **eleven_flash_v2_5** | 40,000 | ✅ YES | ❌ NO | Continuous 0-1 |

### v3 Stability Settings (IMPORTANT)

**eleven_v3 only accepts these discrete stability values:**

| Value | Name | Effect | Best For |
|-------|------|--------|----------|
| `0.0` | Creative | Maximum variation, best audio tag response | Emotional content, transformation, peaks |
| `0.5` | Natural | Balanced variation and consistency | Most content, general use |
| `1.0` | Robust | Maximum consistency, minimal variation | Narration, professional, consistent tone |

**Common Error**: Using values like `0.35` or `0.45` will fail with `invalid_ttd_stability`. Always use exactly `0.0`, `0.5`, or `1.0` for v3.

---

## Eleven v3 (Recommended for Expressive Content)

### CRITICAL: v3 Does NOT Support SSML

**Eleven v3 does not support SSML break tags.** Tags like `<break time="2s"/>` will be ignored or cause issues.

### Creating Pauses in v3

**V3 has dedicated pause audio tags** (use these instead of SSML `<break>` tags):

| Tag | Effect |
|-----|--------|
| `[short pause]` | Brief pause |
| `[long pause]` | Extended pause |
| `[pause]` | Standard pause |

**Other techniques for pacing:**

| Technique | Example | Effect |
|-----------|---------|--------|
| **Ellipses (...)** | `Stand tall ... breathe deep.` | Adds pauses and weight |
| **Punctuation** | Periods, commas | Natural rhythm |
| **Line structure** | Short sentences | Natural pacing |
| **Breathing tags** | `[sighs]`, `[exhales]` | Non-verbal pause with sound |

**Example with v3 pause tags:**
```
[calm] {{user_first_name}}, Superman Stance...

[pause]

Stand tall...

[short pause]

Smile. A real smile.

[long pause]

[exhales] Feel it... Enjoy it...
```

### Audio Tags (v3 Only)

Inline tags that modify delivery. Place in square brackets where you want the effect.

#### Emotion & Tone
- `[calm]` — Steady, peaceful delivery
- `[sad]` — Melancholic coloring
- `[excited]` — Energetic delivery
- `[confident]` — Strong, assured tone
- `[curious]` — Questioning tone
- `[sarcastic]` — Ironic delivery

#### Voice Delivery
- `[whispers]` — Quiet, intimate speech
- `[shouting]` — Loud, intense delivery
- `[singing]` — Melodic attempt

#### Non-Verbal Sounds
- `[sighs]` — Sigh sound (creates pause + sound)
- `[exhales]` — Breath out
- `[exhales sharply]` — Sharp exhale
- `[inhales deeply]` — Deep inhale sound
- `[clears throat]` — Natural pause with sound
- `[laughs]` — Laughter
- `[chuckles]` — Light laughter
- `[crying]` — Emotional delivery

#### Pauses (v3 Only)
- `[short pause]` — Brief pause
- `[pause]` — Standard pause
- `[long pause]` — Extended pause

#### Combining Tags
Tags can be combined: `[calm][whispers]` for calm whispered delivery.

### v3 Emphasis

| Technique | Example | Effect |
|-----------|---------|--------|
| **CAPS** | `I am STRONG` | Emphasizes word |
| **Punctuation** | `I am strong!` | Energetic delivery |
| **Tags + CAPS** | `[excited] BUST THROUGH!` | Maximum intensity |

### v3 Example

```
[calm] Thank you for another day ...

Thank you for giving me the will and opportunity to seek knowledge.

...

[whispers] Everything I want is on the other side of fear.

[confident] Today, I will face my fears and live my dreams!
```

### v3 Constraints

1. **Minimum prompt length**: Under 250 characters may produce inconsistent results
2. **Voice alignment**: Tags work best when aligned with voice characteristics
3. **Don't fight the voice**: A whispering voice won't suddenly shout with `[shout]`
4. **Stability setting**: Use "Creative" or lower stability for maximum tag responsiveness

---

## Multilingual v2 (Fallback / Proven)

### SSML Formatting (v2 Only)

#### Pauses
- `<break time="1.0s"/>` — Natural pause (up to 3 seconds)
- `<break time="3.0s"/>` — Longer reflection pause

#### Example with SSML
```
Good morning. <break time="1.0s"/>

Today, I focus on what MATTERS most. <break time="0.5s"/>

Fundamentals... first.
```

**Note**: Too many `<break>` tags can cause instability (audio artifacts, speed changes). Use sparingly.

---

## Core MCP Tools

| Tool | Purpose |
|------|---------|
| `mcp__ElevenLabs__text_to_speech` | Generate audio from text |
| `mcp__ElevenLabs__play_audio` | Play audio files locally |
| `mcp__ElevenLabs__search_voices` | Find available voices |
| `mcp__ElevenLabs__get_voice` | Get details of a specific voice |
| `mcp__ElevenLabs__list_models` | List available models |

## Key Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| `voice_name` | string | Voice to use (e.g., "Will - Relaxed Optimist") |
| `voice_id` | string | Alternative to voice_name |
| `model_id` | string | Model to use (e.g., "eleven_v3", "eleven_multilingual_v2") |
| `stability` | 0-1 | Lower = more emotional range, higher = more consistent |
| `similarity_boost` | 0-1 | Voice matching fidelity |
| `speed` | 0.7-1.2 | Speaking pace (1.0 = normal) |
| `output_directory` | path | Where to save files |
| `output_format` | string | Default: "mp3_44100_128" |

## Voice Presets

| Preset | Stability | Speed | Similarity | Use For |
|--------|-----------|-------|------------|---------|
| **Calm & Grounded** | 0.6 | 0.9 | 0.75 | Daily practice, affirmations, meditation |
| **Natural & Varied** | 0.4 | 1.0 | 0.75 | Conversational content, narration |
| **Energetic & Motivating** | 0.5 | 1.1 | 0.75 | Pump-up content, motivational audio |
| **v3 Expressive** | 0.3-0.5 | 1.0 | 0.75 | Maximum audio tag responsiveness |

## Available Premade Voices

| Voice | Character |
|-------|-----------|
| Will | Relaxed Optimist |
| Sarah | Mature, Reassuring, Confident |
| Roger | Laid-Back, Casual, Resonant |
| River | Relaxed, Neutral, Informative |
| Matilda | Knowledgeable, Professional |
| Liam | Energetic, Social Media Creator |
| Laura | Enthusiastic, Quirky Attitude |
| Jessica | Playful, Bright, Warm |
| Harry | Fierce Warrior |
| Lily | Velvety Actress |

Use `mcp__ElevenLabs__search_voices` to find more voices or search by name.

## Voice Selection Guidance

### For Personal Development / Daily Practice Audio

**Recommendation**: Same-gender voice as the listener for first-person content.

| Content Type | Voice Gender | Why |
|--------------|--------------|-----|
| First-person affirmations ("I am strong") | Same as listener | Easier to internalize |
| Second-person coaching ("You've got this") | Either | External coach/mentor |
| Third-person quotes | Either | External authority |

### Voice Attributes by Personality

| Listener Type | Ideal Voice Attributes |
|---------------|----------------------|
| **INTJ / Analytical** | Calm, grounded, confident without bravado, measured pace |
| **High-energy / Extroverted** | Energetic, warm, enthusiastic |
| **Anxious / Stressed** | Soothing, warm, slow, reassuring |

### Top Male Voices for Calm/Grounded Content

| Voice | ID | Notes |
|-------|----|----|
| **Will - Relaxed Optimist** | bIHbv24MWmeRgasZH58o | Premade, safe choice |
| **Atlas - The Mentor** | Rdm6yU4x8gd9jBg3BzUF | Deep, "calm yet powerful" |
| **Jason** | 3CaMzawzg6y7TDtDbxXr | Warm, trustworthy |
| **Chuck** | HpwvRGB4etieKEmtZLPD | "Quiet intensity" |

### Testing Emotional Range

If content has emotional variation (calm → excited → grounded), test on the most emotionally varied section first. For daily practice, test Track 10 (Transformation) with `[excited]` tags.

## Custom/Cloned Voices

- **{{user_first_name}}** (cloned voice) — Requires Starter tier ($5/mo) to use via API
- Cloned voices work better with v2 models; v3 alpha has limited clone support

## File Storage Pattern

| Type | Location | Purpose |
|------|----------|---------|
| **Scratch/Testing** | `8-Scratch/Audio/` | Temporary files, experiments |
| **Permanent** | User-specified or `~/Music/DailyPractice/` | Final keeper files |

### Workflow
1. Generate to scratch location first
2. Play and evaluate quality
3. If keeper, move to permanent location using Bash `mv` command

## Subscription & Limitations

| Constraint | Details |
|------------|---------|
| **Free tier** | 10,000 characters/month (~10-12 min audio) |
| **Cloned voices** | Require Starter tier ($5/mo) |
| **VPN** | Blocks free tier — disable VPN when using |
| **v3 char limit** | 5,000 chars per request (chunk longer content) |
| **v2 char limit** | 10,000 chars per request |

## Generation Workflow

### For v3 (Expressive Content)

```
mcp__ElevenLabs__text_to_speech(
  text: "[calm] Your script with audio tags...",
  voice_name: "Will - Relaxed Optimist",
  model_id: "eleven_v3",
  stability: 0.4,
  speed: 1.0,
  similarity_boost: 0.75,
  output_directory: "/path/to/8-Scratch/Audio"
)
```

### For v2 (Stable/Long-form)

```
mcp__ElevenLabs__text_to_speech(
  text: "Your script with <break time=\"2s\"/> tags...",
  voice_name: "Will - Relaxed Optimist",
  model_id: "eleven_multilingual_v2",
  stability: 0.6,
  speed: 0.9,
  similarity_boost: 0.75,
  output_directory: "/path/to/8-Scratch/Audio"
)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "voice_not_found" | Voice isn't in your personal library — add it via ElevenLabs UI first, or use a different voice |
| "ivc_not_permitted" | Cloned voice needs paid tier — use premade voice or upgrade |
| "detected_unusual_activity" | Disable VPN and retry |
| "invalid_ttd_stability" | v3 only accepts 0.0, 0.5, or 1.0 — not continuous values |
| Audio sounds rushed | Lower the speed parameter (try 0.85) |
| Audio sounds monotone | Lower stability (try 0.4-0.5) |
| Weird artifacts | Reduce number of `<break>` tags (v2) or simplify tags (v3) |
| Audio tags ignored | Make sure you're using v3 model; v2 doesn't support them. **Check that `model_id: "eleven_v3"` is explicitly set!** |
| SSML breaks ignored | Make sure you're using v2 model; v3 doesn't support SSML. **For v3, use `[short pause]`, `[pause]`, `[long pause]` instead** |
| Inconsistent v3 output | Increase prompt length (min 250 chars), adjust stability |

---

## Project Tracking Patterns

For multi-track audio projects requiring iteration and reproducibility, use a **three-layer tracking system**:

### The Three Layers

| Layer | Purpose | Location |
|-------|---------|----------|
| **Recipe** | Planned settings per track | Frontmatter in source files |
| **Log** | Attempt history with notes | `generation-log.md` in project |
| **Manifest** | Final keeper files | `manifest.md` in final folder |

### Frontmatter Schema

Add a `generation:` section to each source file's YAML frontmatter:

```yaml
---
title: "Track Name"
char_count: 1200
status: "draft"  # draft | generated | final
generation:
  service: "ElevenLabs"
  model: "eleven_v3"
  voice_name: "Will - Relaxed Optimist"
  voice_id: "bIHbv24MWmeRgasZH58o"
  stability: 0.40
  speed: 1.00
  similarity_boost: 0.75
  output_format: "mp3_44100_128"
---
```

**Why**: Settings travel with content. When updating text later, the generation recipe is right there.

### Generation Log Format

Track attempts in a central `generation-log.md`:

```markdown
### track-name

#### Take 1 — YYYY-MM-DD HH:MM

| Setting | Value |
|---------|-------|
| Voice | Will - Relaxed Optimist |
| Stability | 0.40 |
| Speed | 1.00 |

**File**: `track-name-take1.mp3`
**Duration**: 1:23
**Notes**: [Observations about quality, pacing, tag responsiveness]
**Verdict**: ✅ Keeper / ❌ Retry / 🔄 Adjust settings
```

### Manifest Format

Document final keeper files in `manifest.md`:

```markdown
| Track | File | Voice | Stability | Speed | Duration | Generated |
|-------|------|-------|-----------|-------|----------|-----------|
| 01 | 01-track.mp3 | Will | 0.50 | 0.90 | 2:15 | 2026-01-04 |
```

### Testing Strategy

**Test the most emotionally complex content first.**

If content has emotional variation (calm → excited → grounded), generate the most demanding section first to evaluate:
- Audio tag responsiveness
- Voice emotional range
- Transition smoothness

If that works, simpler content will work too.

### File Naming Convention

```
[track]-take[N].mp3
```

Examples: `05-theme-take1.mp3`, `05-theme-take2.mp3`

When finalized: `05-theme.mp3` (no take number)

---

## Self-Talk Voice Research

Research-backed guidance for personal development audio (affirmations, daily practice, coaching).

### First vs Second vs Third Person

Based on Kross/Moser research on self-distancing and emotion regulation:

| Voice | Example | Effect | Best For |
|-------|---------|--------|----------|
| **First-person ("I")** | "I am strong" | Direct identification | Identity statements you believe |
| **Second-person ("You")** | "You've got this, [Name]" | Self-distancing, coaching | Challenges, stress, coaching |
| **Third-person (Name)** | "[Name] is strong" | Maximum psychological distance | Anxiety, emotional regulation |

### The Self-Distancing Effect

- Second/third person creates psychological distance
- Allows more objective self-view (like giving advice to a friend)
- Activates different neural pathways than first-person
- Works quickly without significant cognitive effort

### Voice Strategy Matrix

| Content Type | Recommended Voice | Why |
|--------------|-------------------|-----|
| Gratitude | First-person | Direct emotional experience |
| External quotes | Third-person (author) | Wisdom from authority |
| Physical coaching | Second-person | Instruction mode |
| Identity statements | First-person | Direct ownership |
| Fear/stress management | Second-person | Distance from fear |
| Vision/future self | Second-person | Painting picture for self |
| Closing commitments | First-person | Ownership of commitment |

### When to Use Listener's Name

Using first name (e.g., "{{user_first_name}}, stand tall...") is especially effective for:
- Managing anxiety (high effectiveness)
- Pre-performance situations (high effectiveness)
- Processing negative emotions (high effectiveness)
- Everyday affirmations (moderate effectiveness)

Less effective for deep identity work where first-person may be better.

### Affirmation Caveat

Research shows affirmations work best when you have some existing belief in them. For statements that feel false:
- Frame as aspirational: "I am becoming..."
- Use second-person coaching voice
- Or skip until belief develops

### Sources

- Kross, E., et al. (2017). Third-person self-talk facilitates emotion regulation. *Scientific Reports*.
- Dolcos, S., & Albarracín, D. (2014). The inner speech of behavioral regulation. *European Journal of Social Psychology*.

## Integration Points

- **Pronunciation lexicon**: See `.claude/skills/audio-generator/pronunciation.yaml` for word replacements
- **Daily Practice project**: See `1-Projects/Current/Daily-Practice-Refresh-2026/audio-generation-workflow.md` for a real-world example of the three-layer tracking system
- **document-generator skill**: Complements printable materials with audio
- **personal-insight skill**: Captures self-insights that could inform personal development audio content

## References

- [ElevenLabs v3 Best Practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- [ElevenLabs Models Documentation](https://elevenlabs.io/docs/overview/models)
