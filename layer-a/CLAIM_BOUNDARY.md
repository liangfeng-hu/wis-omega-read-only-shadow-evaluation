# Claim Boundary / 声明边界

## This package can establish

- the included standard-library evaluator deterministically applies the declared Shadow rules to five frozen cases;
- missing evidence, incomplete binding, replay and consumer-side drift fail closed;
- a complete case can create and consume one Shadow Permit once;
- the generated receipts are hash-linked and independently recomputable;
- the packaged run loads no credential, makes no network request, starts no persistent service, and performs no world writeback.

## This package cannot establish

- production readiness, runtime closure or production closure;
- physical single ingress, real KMS/HSM integration or a production credential boundary;
- independent third-party reproduction or measurement of any external product;
- safety of unrestricted Agent world writeback;
- implementation, deployment, procurement, certification or compliance approval.

The “illustrative unprotected reference path” is code in this evaluation package. It is not a benchmark result for any company, model, framework or production system.

The Permit in this package is a deterministic local Shadow object. It is not a cryptographic capability, is not signed by KMS/HSM, and cannot authorize an external or production effect.

## Permanent Shadow invariants

- Agent output is candidate-only.
- A rejection does not create an accepted Permit.
- A Shadow Permit is single-use and bound to identity, endpoint, effect and recovery evidence.
- Validation and consumption are separated; the consumer independently recalculates effect binding.
- Missing or damaged evidence fails closed.
- `CredentialsLoaded=0`; `WorldWriteback=0`.

---

本包只能证明五条冻结 Shadow 用例由随包同一条谓词管线确定性执行，并生成可重算的哈希链收据。包内 Permit 只是未由 KMS/HSM 签名的本地 Shadow 对象，不是密码学能力。它不能证明生产就绪、生产闭环、真实物理单入口、真实 KMS/HSM、第三方独立验证或无限制世界写回安全。
