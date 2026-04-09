# SFRP Label Audit — Complete Guide

---

## Table of contents

1. [Setup](#1-setup)
2. [What you're doing](#2-what-youre-doing)
3. [The golden rule](#3-the-golden-rule)
4. [Cheat sheet (all 9 features)](#4-cheat-sheet)
5. [Feature-by-feature rules (reference)](#5-feature-rules)
6. [Reason chips](#6-reason-chips)
7. [Common questions](#7-common-questions)
8. [After you finish](#8-after-you-finish)

---

<a id="1-setup"></a>
## 1. Setup

**Files you need:**
- `sfrp_audit_v5.html` — the audit tool (open in any browser)
- `audit_set.json` — the dataset (load into the tool)

**Steps:**
1. Open `sfrp_audit_v5.html` in Chrome, Safari, or Firefox
2. Type your name in the "Your name" field
3. Tap the drop zone and select `audit_set.json`
4. You'll see 1125 items across 9 linguistic features

Your progress saves automatically. You can close and come back. Don't clear your browser data or use incognito mode.

---

<a id="2-what-youre-doing"></a>
## 2. What you're doing

An algorithm labeled web sentences with linguistic features. You're checking: **did the algorithm get the label right?**

You are NOT labeling from scratch. You see the algorithm's answer and judge it. This is faster but has a trap: don't just rubber-stamp "Correct" on everything. The algorithm makes real mistakes (~10-20% of items). If you're above 95% Correct, you're probably going too fast.

**Three buttons:**
- **Correct** — the label is right (one tap, done)
- **Wrong** — the label is wrong → pick the correct label → tap a reason
- **Not sure** — genuinely ambiguous → tap a reason

**Speed target:** 5–10 seconds per item. Use your gut.

**First 20 items:** go slow (15-20 seconds each). After item 20, tap "Stats" — you should be marking some items Wrong. If everything is Correct, re-read section 3. It's better to calibrate now than redo 500 items later.

---

<a id="3-the-golden-rule"></a>
## 3. The golden rule

**For negation, tense, number, and voice:** the label applies to the **main clause only** — not subordinate clauses, not quoted speech.

**How to find the main clause:** identify clauses starting with "if," "although," "because," "who," "which," "when," "while," or anything inside quotation marks. Set those aside. What remains is the main clause.

> **"If you can't have your own garage, use Ken's."**
> Set aside: "If you can't have your own garage" → Main clause: "use Ken's" → affirmed, not negated.
> **You tap:** Wrong → affirmed → "Subordinate clause"

> **"The manager said, 'We won't be making any changes.'"**
> Set aside: the quoted speech → Main clause: "The manager said" → affirmed.
> **You tap:** Wrong → affirmed → "Subordinate clause"

> **"The researchers have not published their findings."**
> No subordinate clause. "Not" modifies the main verb. → negated. Correct.
> **You tap:** Correct

**Note:** This rule applies to negation, tense, number, and voice. For cause_effect, sentiment, comparison, complexity, and register, consider the **whole sentence** — those features describe overall sentence properties, not just the main verb.

---

<a id="4-cheat-sheet"></a>
## 4. Cheat sheet

Skim this table before starting. Come back to **section 5** when you need the detailed rules for a specific feature.

| Feature | Labels | What to look at | Quick test |
|---------|--------|----------------|------------|
| **Negation** | negated / affirmed | Is the main clause verb negated? | Does the main verb have not/never/no before it? |
| **Tense** | past / present / future | Main clause verb tense | What tense is the first verb after the subject? |
| **Number** | singular / plural | Main clause subject | Does the subject-verb pair use -s or not? |
| **Voice** | active / passive | Main clause subject | Does the subject do the action, or receive it? |
| **Sentiment** | positive / negative | Whole sentence tone | Would you call this good news or bad news? |
| **Comparison** | positive / comparative / superlative | Adjective degree | Base form, -er/more, or -est/most? |
| **Complexity** | simple / complex | Clause count | Is there an although/because/who/if clause? |
| **Register** | formal / informal | Language style | Any contractions? Academic vocabulary? |
| **Cause/Effect** | causal / non_causal | Whole sentence | Does A cause/lead to B? |

---

<a id="5-feature-rules"></a>
## 5. Feature-by-feature rules (reference)

Use this section as a **lookup** — don't try to memorize it before starting. When you hit a feature you're unsure about, scroll here.

### Negation (negated / affirmed)

Main clause verb only. Ignore subordinate clauses and quoted speech.

| Sentence | Label | Why |
|----------|-------|-----|
| "The study did not find a link." | negated | "not" modifies main verb |
| "Nobody attended the meeting." | negated | "nobody" negates main verb |
| "He denied the allegations." | affirmed | "deny" means something negative, but the verb itself isn't negated — he DID deny |
| "If it doesn't rain, we'll go." | affirmed | "doesn't" is in the "if" clause; main clause is "we'll go" |
| "She said she can't come." | affirmed | "can't" is reported speech; main clause is "she said" |

### Number (singular / plural)

Main clause subject-verb agreement. Judge by the verb form the writer actually used.

| Sentence | Label | Why |
|----------|-------|-----|
| "The company says revenue grew." | singular | "company says" |
| "The researchers argue that..." | plural | "researchers argue" |
| "The team is performing well." | singular | "is" = singular (US English) |
| "The team are performing well." | plural | "are" = plural (UK English) |
| "The report that researchers published shows..." | singular | main subject is "the report," not "researchers" |

**Collective nouns** (team, company, government): go by the verb form used, not by what's "correct."

### Tense (past / present / future)

Main clause verb only.

| Sentence | Label | Why |
|----------|-------|-----|
| "The company announced layoffs." | past | simple past |
| "She thinks it was a mistake." | present | main verb "thinks" |
| "He said he will resign." | past | main verb "said" |
| "The project will launch next month." | future | "will launch" |
| "Experts have warned about this risk." | present | for this audit, treat present perfect ("have warned") as present |
| "They could face penalties." | present | for this audit, treat modals as present |
| "She could have prevented it." | past | "could have" + participle = past |

**Modals** (can, could, may, might, should, would): treat as present unless combined with "have" → past.

**Perfect tenses:** "has done" = present. "had done" = past. "will have done" = future.

### Voice (active / passive)

Does the main clause subject **do** the action or **receive** it?

| Sentence | Label | Why |
|----------|-------|-----|
| "The team reviewed the report." | active | "team" does the reviewing |
| "The report was reviewed by the team." | passive | "report" receives the action |
| "She got fired last week." | passive | "got + past participle" counts as passive |
| "The results are interesting." | active | this is a description, not a passive action |

**Quick test for passive:** Can you add "by someone" and it still makes sense? "Was reviewed *by the team*" ✓ = passive. "Are interesting *by someone*" ✗ = not passive.

### Sentiment (positive / negative)

Overall emotional tone of the **whole sentence**.

| Sentence | Label | Why |
|----------|-------|-----|
| "The company reported record profits." | positive | favorable outcome |
| "Despite setbacks, the project succeeded." | positive | overall tone is positive |
| "The plan failed completely." | negative | unfavorable outcome |
| "The allegedly wonderful plan collapsed." | negative | "collapsed" overrides "wonderful" |

Don't be tricked by individual positive words in a negative sentence, or vice versa. If the overall tone is truly neutral (neither positive nor negative), mark **Not sure → Label debatable**.

### Comparison (positive / comparative / superlative)

The degree form of the adjective or adverb in the **main clause**.

| Sentence | Label | Why |
|----------|-------|-----|
| "It was a significant achievement." | positive | base adjective |
| "This approach is more efficient." | comparative | "more efficient" |
| "That was the worst decision ever." | superlative | "worst" |

**If multiple adjectives:** go with the one in the main clause. If both are in the main clause, go with the first one.

### Complexity (simple / complex)

Does the sentence have any embedded dependent clauses?

| Sentence | Label | Why |
|----------|-------|-----|
| "The team finished the project on time." | simple | one clause |
| "Although costs rose, the team finished on time." | complex | "although" clause |
| "The person who designed the system left." | complex | "who designed" = relative clause |
| "I want to go home." | simple | "to go" is an infinitive, not a clause |

**Signals for complex:** although, because, if, when, while, unless, since, whereas, though, who, which, that (relative).

### Register (formal / informal)

Overall language style of the whole sentence.

| Sentence | Label | Why |
|----------|-------|-----|
| "Furthermore, the analysis revealed..." | formal | "furthermore" + academic vocabulary |
| "They can't really figure out what's going on." | informal | contractions + casual phrasing |
| "The committee subsequently approved the measure." | formal | institutional language |

**Contractions are the strongest signal.** Any contraction (can't, won't, it's, they're) leans informal — even if the rest of the vocabulary is formal. If a sentence mixes formal words with contractions, lean **informal**.

### Cause/Effect — cause_effect (causal / non_causal)

Does the **whole sentence** describe a cause-and-effect relationship?

| Sentence | Label | Why |
|----------|-------|-----|
| "Prices rose because of supply shortages." | causal | "because of" = explicit cause |
| "The policy led to widespread protests." | causal | "led to" = cause→effect |
| "The company opened a new office in Denver." | non_causal | no causal relationship |
| "Since 2015, crime has risen steadily." | non_causal | "since" is temporal here |
| "Since you asked, I'll explain." | causal | "since" is causal here |

**Causal markers:** because, therefore, consequently, as a result, led to, caused, resulted in, due to, hence, thus.

---

<a id="6-reason-chips"></a>
## 6. Reason chips

When you tap Wrong or Not sure, quick-tap a reason:

| Chip | When to use |
|------|-------------|
| **Subordinate clause** | Label describes a subordinate or quoted clause, not the main clause |
| **Wrong subject** | Algorithm picked the wrong noun as the subject |
| **Dialect ambiguous** | US vs UK English makes the label debatable |
| **Explanation wrong** | The hint text below the label doesn't match the sentence |
| **Label debatable** | Reasonable people could disagree on this one |
| **Multiple features** | Conflicting signals within the sentence |
| **Confounded context** | Sentence is garbled, truncated, or not labelable |

Tap zero, one, or several. Optionally type a short note. Tap **Done**.

---

<a id="7-common-questions"></a>
## 7. Common questions

**"The sentence is garbled or not English."**
→ **Not sure** → **Confounded context**.

**"The negation is in a quote or 'if' clause."**
→ **Wrong → affirmed → Subordinate clause**.

**"Is 'the team' singular or plural?"**
→ Go by the verb form: "the team is" = singular, "the team are" = plural.

**"I can't tell if the sentiment is positive or negative."**
→ **Not sure → Label debatable**. Don't spend more than 5 seconds deciding.

**"The label feels wrong but I can't explain why."**
→ Tap **Correct**. If you later figure out why, you can't go back — that's OK.

**"I'm marking almost everything Correct (>95%)."**
→ Slow down. The algorithm makes mistakes on ~10-20% of items. Re-read section 3.

**"I'm marking a lot Wrong (<70% Correct)."**
→ Re-read the guide. If you're still flagging a lot, keep going — that's useful data.

**"The explanation text seems wrong."**
→ It's a generic example, not about your sentence. Judge the label, not the explanation.

**"How long will this take?"**
→ 60-90 minutes with breaks.

**"I closed my browser."**
→ Reopen the HTML, tap "Resume previous session."

**"Something genuinely weird not covered here."**
→ **Not sure**, type a short note, move on.

---

<a id="8-after-you-finish"></a>
## 8. After you finish

1. Tap **Stats** → review your numbers
2. Tap **Download validation results** → saves a JSON file
3. Send the JSON file back
4. That's it — thank you

Your results get compared with other reviewers to measure agreement. If agreement is high, the datasets are validated. If not, we revise the labeling rules and re-run — that's the adjudication process working as intended, not a failure on your part.

---

*SFRP v11 — Audit Guide v4 — 9 features, 1125 items*
