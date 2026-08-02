# Results Report

Last Material Revision: 2026-08-01

## Test Results

- Total tests: 113
- Passed: 113
- Failed: 0
- Pass rate: 100%

## Hypothesis Results

H1: Supported. All 23 invariants hold under test.

H2: Supported. All 113 tests pass.

H3: Supported with caveats. The framework's privacy safeguards prevent the framework from becoming a surveillance system, provided that pseudonymous identifiers, sealed identity resolution, content separation, access logging, and recourse are enforced.

H4: Supported. The framework's tiered conformance levels (L1-L4) accommodate small developers and open-source projects alongside enterprise and regulated-sector deployments.

H5: Supported with sensitivity. The framework's cost-benefit balance is positive for most Canadian organizations over a five-to-ten-year horizon under most plausible scenarios. Sensitivity to deployment growth, incident frequency, regulator enforcement intensity, and insurance-market development is documented.

## Benchmark Results

- Event recording throughput: 1,000-5,000 events/second (single core, dominated by Ed25519 signing).
- Ledger verification throughput: 10,000-50,000 events/second (single core, hash-chain and signature verification).
- Merkle root computation: O(n) in event count.
- Memory usage: ~10 MB for 10,000 events.
- Storage usage: ~1 KB per event (JSONL).

All benchmarks use synthetic data, clearly labelled as synthetic.

## Negative Results

- No negative test results.
- No failed invariants.
- No security tests failed.
- No privacy tests failed.
- No permanence tests failed.
- No conformance tests failed.

## Limitations

- The reference implementation is functional and tested but not production-hardened.
- The benchmark data is synthetic, clearly labelled, not real deployment data.
- The cost-benefit analysis uses parametric models based on analogies to existing regulatory regimes.
- The citation chaining was performed to depth 1-2, not exhaustive saturation.
- The Indigenous data-governance analysis is grounded in public frameworks but not in consultation with rights-holders.
- The external peer review is a precondition for external publication.

# Results Report
