from pharma_help.agents.retrieval import retrieve_docs
hits = retrieve_docs('imatinib chronic myeloid leukemia', k=3)
for h in hits:
    print(h.id)
    print(f'[{h.score:.3f}] {h.id} — {h.title[:80]}')