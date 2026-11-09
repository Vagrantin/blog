{
  "title": "Open Source: The Future of Software Sovereignty?",
  "publishDate": "2026-05-06T09:00:00+09:00",
  "draft": false,
  "url": "/20260506/OSSNotDead.html",
  "params": {
    "legacy": true
  },
  "description": "Context: this is a topic I have been chewing on for a while, mostly because of what I see at work between the AI tooling on one side and customers asking more and more questions about who really controls…"
}

## Open Source Is Dead, Long Live Open Source

Context: this is a topic I have been chewing on for a while, mostly because of what I see at work between the AI tooling on one side and customers asking more and more questions about who really controls their software. This is an opinion piece, not a study, and I may well be wrong on part of it.

My position in a nutshell: open source is not dying, it is becoming the default. Two forces are pushing in that direction, AI and geopolitics. Let’s brake this down.

### The Value Is Leaving the Code

#### Software Becomes a Commodity

As AI is being currently highly subsidized, generated code and agentic workflows are making software much cheaper to produce . A small internal tool, a migration script, a protocol adapter: this used to be a team and months of work. Now it is often an afternoon.

When the cost of production collapses, the value moves somewhere else. For most software the IP was never really the algorithm, it was the accumulated effort of writing it, debugging it and maintaining it over years. If that effort becomes cheap to reproduce, keeping the source closed protects very little. Your competitor does not need to steal your code anymore, he just needs to describe it.

So I do not see closed source as a strong position anymore. Hiding the source to protect a value that is not in the source costs you trust, and it does not buy much in return.

#### Developers Are Needed More Than Ever

Careful though, the commodity is the code, not the engineering.

Generating a plausible implementation is now the cheap part of the job. Deciding what should exist, how it fails, where the security boundaries are, what the data model will cost in three years, and whether the generated code is correct or only looks correct: this is the expensive part. AI has actually made it more expensive, because there is much more code to review than before.

Effectively the job moves up a level: less typing, more specifying, integrating and reviewing, at a volume nobody had to sustain until now. That is not a job for fewer developers.

### Distrust Is Now an Architecture Requirement

The second force has nothing to do with technology. We have entered a period of distrust between states, and this is re-shuffling the partnerships between regions of power. Export controls, sanctions, extraterritorial data laws: all of this pushes the same question into every procurement discussion, which is what happens to this system if the relationship with the vendor country goes bad.

A contract is a promise. Source code, with the right and the ability to build it and run it, is a capability. When a relationship breaks the promise is worth nothing and the capability still works. This is the whole point of open source in an untrusted business relationship, and it does not require anybody to be nice.

This is why I think everything ends up open source for the customer. Not because vendors suddenly like the idea, but because customers with sovereignty constraints will progressively stop buying anything else. This is also what regionalises the usage of software: open source becomes the only way to collaborate across borders without giving away control.

### Now Let Us Take the Argument Apart

#### Nobody Actually Wants to Build Their Own Software

Having the source is not the same as being able to use it. Most customers do not want to package, patch, upgrade and support their own stack, and honestly they are right: this work never stops and it competes with their real business. The right to fork is a right that almost nobody will exercise. A turnkey product is attractive exactly because somebody else takes the pain.

#### The Models Will Keep Hallucinating

There is no LLM today, and I do not believe there will be one, that produces perfect code. Hallucination is not a bug waiting for a patch, it is how these systems work, they produce what is plausible. And the dangerous output is not the code that does not compile, it is the code that looks perfectly reasonable but plain wrong.

In broadcast, in infrastructure, in anything regulated, the cost of a wrong line has never been the time needed to write it. So review, tests and operational discipline stay mandatory, and this caps how much of the promised speed you actually collect.

#### The Lock-In Moves, It Does Not Disappear

Owning the source of something you cannot operate is a receipt, not independence.

What I see coming is the lock-in moving from the licence to the operations: the managed control plane, the identity provider, the model API, the hardware supply. A stack that is 100% open source and 100% operated by a single hyperscaler is not sovereign in any way that would survive a political dispute. The SaaS overlord simply replaces the software vendor.

Same trap with AI itself. If the agentic pipeline that produces your software depends on one vendor frontier model, the dependency has just moved one level up, into the tooling instead of the product.

#### The Orchestration Gap

Agentic workflows are not free to run. They need context engineering, evaluation, guardrails, cost control, reproducible pipelines, and somebody on call for a system that is not deterministic. Most customers do not have a team for that, and most of them will not hire one. Without those skills you end up with fragile automation that is harder to trust than the manual process it replaced.

### From Consumer to Actor

All of this only works if customers change their posture. Being a passive consumer is not compatible with the sovereignty they are asking for. Being an actor means keeping real engineering skills in house: running your own deployments, reading the code you depend on, sending your fixes upstream, and being able to fork if one day you have to.

The realistic alternative, and probably the most common one, is to delegate to a regional trusted partner. Integrators, hosting providers, cooperatives, public shared services, whose whole value is to operate open stacks inside a jurisdiction the customer trusts. You keep most of the sovereignty argument and you outsource the pain. I think this is where a good part of the market will move in the coming years.

The bad answer is the third one: write an open source policy, keep consuming exactly like before, and discover during the first dispute that the escape door was never tested. A fork you have never done is a fork you cannot do.

### Conclusion

Open source is not dead, it is the layer everything else sits on. AI is removing the economic reason to keep the code closed, and geopolitics is removing the willingness to accept it.

Also, being open is now the easy part. The hard part is the capability: operating what you own, judging what the machine writes, and keeping the skills either in your own team or in a partner you have chosen on purpose. Those who build that capability get a real exit door. The others will still be dependent, only on a different lord, with the paperwork of freedom instead of the freedom itself.

This is my current thinking on the subject, if you see where, I would be happy to read about it.
