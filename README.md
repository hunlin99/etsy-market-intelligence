# Etsy Market Intelligence Skill

**Turn digital product ideas into evidence-based decisions about what to investigate, test, or build on Etsy.**

Etsy Market Intelligence Skill is an AI research and decision-support skill designed to help creators evaluate digital product opportunities. It brings together market observations, competitor information, customer feedback, and your own constraints to answer a practical question: **Is this idea worth my next investment of time and money?**

> **Development status:** The project is at the initial scaffold stage. The capabilities and outputs below describe the intended product; they are not yet implemented or tested.

## What it helps you do

- **Check a product idea:** Explore whether a niche deserves further research or a small test.
- **Compare opportunities:** Weigh candidate products against demand signals, competition, differentiation, and your available time and budget.
- **Understand customer needs:** Look for recurring problems, unmet needs, and gaps in existing offers.
- **Challenge your assumptions:** Consider the strongest reasons an idea might fail, including free alternatives and weak evidence of willingness to pay.
- **Choose a next step:** Decide what to learn, prototype, test, revise, or stop before making a larger commitment.
- **Revisit a decision:** Use new evidence and results from your own experiments to update the recommendation.

## The problems it addresses

A popular listing is not automatically a profitable opportunity. Reviews, search results, and bestseller badges can provide clues, but they do not establish sales, revenue, or future demand.

This skill is designed to help you avoid research that sounds convincing but leaves you unsure what to do. It separates observed facts from interpretations, assumptions, and unknowns, and connects recommendations to the evidence behind them. When information is missing or conflicting, the result should make that clear.

It also challenges enthusiasm for an idea: your preference should shape the question, while the evidence shapes the recommendation.

## What you can expect to receive

| Output | What it gives you |
| --- | --- |
| **Quick Check** | A concise assessment of an idea, its main risks, and the next useful action. |
| **Opportunity Comparison** | A side-by-side view of candidate ideas and the tradeoffs between them. |
| **Evidence Log** | A traceable account of sources, observations, limitations, and unanswered questions. |
| **Decision Summary** | A recommendation tied to the specific decision you are making, with confidence and a counter-case. |
| **Validation Plan** | A small experiment with observable outcomes, time and budget limits, and conditions for continuing or stopping. |

The intended result is a clearer decision, a realistic next step, and an understanding of what evidence could change your mind. No assessment guarantees sales or profitability.

## Example

**You ask:**

> “I’m considering a pet care handover template. I have notes on six competitors and some customer reviews. With five hours a week and a small budget, is it worth testing?”

**The intended response would:**

- Explain what the supplied competitor notes and reviews actually support.
- Identify a possible customer need and the strongest argument against the idea.
- Flag missing information, such as whether buyers will pay instead of using a free alternative.
- Recommend a bounded next step based on the available evidence.
- Suggest a small test and define what results would justify continuing, revising, or stopping.

The recommendation depends on the evidence; it is not a predetermined “yes.”

## Development direction

The first milestone focuses on Quick Checks and comparisons using supplied information and prepared examples. Later milestones aim to add deeper Etsy research, including discovery, costs, and policy considerations. Cross-platform research is a future direction.

Live Etsy research and automated monitoring are not available in the current scaffold.

For the full project proposal, see the [development specification](docs/Etsy_Market_Intelligence_Skill_Development_Spec_v1.0.md).
