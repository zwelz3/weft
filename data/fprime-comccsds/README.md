# F Prime ComCcsds dataset

Public data for the spike's data request ([zwelz3/weft#1](https://github.com/zwelz3/weft/issues/1)), taken from NASA's F Prime flight software framework ([nasa/fprime](https://github.com/nasa/fprime)) at commit `433db6e24b6509130ff50ebf7d27920ab60b04e8`. The component is the `ComCcsds` communications subtopology, its parent system is F Prime's `Ref` test deployment, and the traced child is the `Svc::ComQueue` component.

## License

F Prime is distributed under the Apache License 2.0. Its license and notice files are copied unchanged in `source/LICENSE.txt` and `source/NOTICE.txt`, and every file under `source/` is an unmodified copy from the commit above. The notice restricts use of the names Caltech and the Jet Propulsion Laboratory to endorse derived products. The tables at the top level and under `instance/` and `trace/` are derived from those files and from the repository's commit history by `generate.py`, except `trace/issues.csv` (below).

## Coverage of the data request

| Item in #1 | What covers it | Gaps |
|---|---|---|
| 1. The component | `source/Svc/Subtopologies/ComCcsds/` (design document, FPP model, configuration). Requirements SVC-COMCCSDS-001 to 007 and SVC-COMQUEUE-001 to 013 are in `requirements.csv`, with text and verification method. Interfaces are the ports declared in `ComCcsds.fpp` and `ComQueue.fpp`; the protocols are CCSDS Space Packet and TM/TC transfer frames. The parent system is `source/TestDeploymentsProject/Ref/Top/topology.fpp`, which instantiates the subtopology. The decomposition one level down is the design document's instance summary and its traceability matrix. | No requirement carries a numeric parameter, so `sysmlv2 verify` has nothing to decide. All ComCcsds requirements are verified by inspection. |
| 2. Instance data | `instance/comccsds-dictionary.csv`: the 35 ComCcsds rows (11 telemetry channels, 3 commands, 21 events) of the `Ref` deployment's dictionary, generated with `fpp-to-dict`. `source/TestDeploymentsProject/Ref/Top/instances.fpp` lists 21 component instances with base identifier, queue size, stack size, and priority, blank for passive components, which serves as a second table. | `format` is empty on every telemetry and command row (events carry format strings), and limits appear on two rows, which keeps the missing values the request asks for. No row has units. |
| 3. Trace data | `trace/satisfied-by.csv` (the ComCcsds design document's requirement-to-instance table), `trace/tests.csv` (31 unit tests; 5 carry `REQUIREMENT("SVC-COMQUEUE-013")` tags), `trace/commits.csv` (5 commits, with the requirement rows and tests each one added, computed from the diff), and `trace/issues.csv` (6 issues). | No issue names a requirement identifier. Issue-to-requirement links go through the closing commit, and two of them are inferred from content; `link_basis` says which. Only SVC-COMQUEUE-013 has tests tagged with its identifier. |
| 4. Adapter ontology excerpt | `source/docs/reference/fpp-json-dict.md`, the specification of the dictionary format the instance table comes from, with field tables for commands, telemetry channels, events, parameters, and packets. | It is not RDF. The mapping to an RDF vocabulary has to be written. |
| 5. Existing model | The FPP files are a textual architecture model of the component. | No SysML or Capella model exists. |

## How the tables were produced

`generate.py` regenerates every table except `trace/issues.csv` from a checkout of nasa/fprime at the commit above, with `fpp-to-dict` from fprime-fpp 4.0.0a2 (the version F Prime pins in its `requirements.txt`) on the path:

```sh
git clone https://github.com/nasa/fprime && git -C fprime checkout 433db6e24b6509130ff50ebf7d27920ab60b04e8
pip install fprime-fpp==4.0.0a2
python generate.py fprime
```

The script reads only the checkout. The repository's history must be present, because `trace/commits.csv` is computed from five commits' diffs.

`trace/issues.csv` was written by hand from the six issue pages on github.com, read on 2026-11-26, because the issues are not part of the git repository. It records each issue's title, state, and closing pull request, and no author names.

## Sanitization

The tables hold no personal data. Commit authors, co-author trailers, and issue authors are left out; commits are identified by hash and subject only.
