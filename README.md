# WIS-Ω Read-Only Shadow Evaluation

Agent output is a candidate action, not a write grant.
A missing evidence hash, incomplete binding, replayed Permit, or
consumer-side effect drift must fail closed.

Mode: `SHADOW / NO_CREDENTIALS / WorldWriteback=0`.

View first: open `layer-a/SAMPLE_REPORT.html` or watch `layer-a/demo.mp4`.
Stopping after the report is a complete review.

Optional local reproduction:

```bash
cd layer-b
./RUN_EVALUATION.sh
```

Canonical interface: `wisomega-eval run --pack cases-shadow-v1 --out out/`.

All five frozen cases use one ID-independent predicate pipeline. Case IDs are
labels and expected outcomes are test data, not hardcoded control flow. The
local Shadow Permit is unsigned, is not a KMS/HSM capability, and cannot
authorize an external or production effect.

No Docker, network request, credential, persistent service, or world writeback.
This is a local proof of mechanism, not production security, a vendor
benchmark, or independent validation.

## 中文

Agent 输出只是候选动作，不是写授权。证据无法重算、绑定不完整、
Permit 重放或消费侧效果漂移时必须 fail-closed。

默认先打开 `layer-a/SAMPLE_REPORT.html`；本地运行完全自愿。
五条冻结用例使用同一条不读取用例编号的谓词管线。
无 Docker、无网络、无凭证、无常驻服务，世界写回为 0。
