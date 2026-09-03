# WIS-Ω Read-Only Shadow Evaluation

> Agent output is a candidate action, not a write grant. A missing evidence hash, an incomplete binding, a replayed Permit, or consumer-side effect drift must fail closed.

## What this evaluates

Whether a candidate Agent action fails closed when recomputable evidence or an exact binding is missing, when a Permit is replayed, or when the consumer observes effect drift.

## What you will see

Five frozen cases produce either `PERMIT` or `FAIL_CLOSED`, plus independently recomputable, hash-linked Shadow receipts. One valid case is included so the evaluator is not a deny-only demonstration.

## What you do not need to provide

No gateway installation, Docker, service account, model key, production traffic, credential, network access, or production write permission. The runnable layer writes only to the selected local `out/` folder.

## Default path: view only

Open `SAMPLE_REPORT.html`, or watch `demo.mp4`. Stopping here is a complete review; running code is not required.

## Optional reproduction and support

- If you received the combined package and voluntarily want to reproduce the result, the separate `layer-b/` folder contains the one-entry evaluator.
- If a work computer should not run an unfamiliar script, the provider can run the same command during a 15-minute screen share while you only observe the output.
- No response, environment preparation, feedback form, model access, traffic, key, or follow-up meeting is required.

Current mode: `SHADOW / NO_CREDENTIALS / WorldWriteback=0`.

---

# WIS-Ω 只读对照评估

Agent 只能提出候选动作。没有绑定身份、端点、效果和恢复证据的一次性 Permit，就不能获得世界写权限。

本包用五条冻结用例检查：缺少可重算证据、绑定不完整、合法通过、重复消费以及消费侧效果漂移。无需 Docker、模型密钥、生产流量或真实凭证；运行结果只写入本地 `out/`。

默认只打开 `SAMPLE_REPORT.html` 或 90 秒 `demo.mp4`，到此即完成。若您自愿复现，合并包中的独立 `layer-b/` 才提供单入口；工作电脑不便运行时，可由提供方在 15 分钟屏幕共享中代跑，您只看结果。
