# WIS-Ω Read-Only Shadow Evaluation

Agent output is a candidate action, not a write grant. Missing recomputable evidence, incomplete identity/endpoint/effect/recovery binding, Permit replay, or consumer-side effect drift must fail closed.

Read-only Shadow evaluator: Agent actions stay candidates until a single-use Permit is bound to identity, endpoint, effect and recomputable evidence. `WorldWriteback=0`.

This combined package has two deliberately separate layers:

- `layer-a/`: default path. Preview `SAMPLE_REPORT.html` or watch `demo.mp4`. Stopping here is complete.
- `layer-b/`: optional reproduction only. Windows users may double-click `RUN_EVALUATION.cmd`; macOS/Linux users may run `./RUN_EVALUATION.sh`.

The runnable layer produces `SUMMARY.txt`, `report.html`, hash-linked receipts and run metadata under its local `out/` directory.

No Docker. No network request. No credential. No persistent service. `WorldWriteback=0`.

If a work computer should not run an unfamiliar script, do not run it. The provider can execute the same command during a 15-minute screen share while the reviewer only observes the result.

This package is an evaluation candidate, not production software or independent validation. The local Permit object is not a cryptographic capability and is not KMS/HSM-signed.

## 中文

只读 Shadow 判定：Agent 动作保持候选；无绑定身份、端点、效果与可重算证据的一次性 Permit，不得获得世界写权限。写回=0。

默认只打开 `layer-a/SAMPLE_REPORT.html` 或 90 秒演示，到此即完成。只有自愿复现时才进入 `layer-b/`；工作电脑不便运行外来脚本时，可由提供方在 15 分钟屏幕共享中代跑。
