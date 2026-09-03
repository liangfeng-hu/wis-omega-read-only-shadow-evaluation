# WIS-Ω Read-Only Shadow Evaluation

## Start here — no setup required

1. **[Watch the 90-second demo](layer-a/demo.mp4)**
2. **[Read the one-minute result](layer-b/SAMPLE_SUMMARY.txt)**
3. **[Optional: reproduce locally](layer-b/README.md)**

Watching the demo or reading the result is a complete first review. No account,
installation, Docker, credential, company data, reply, or meeting is required.
Local reproduction is entirely optional, makes no network requests, and keeps
`WorldWriteback=0`.

For scope and limitations, see the [Security FAQ](SECURITY_FAQ.md) and
[claim boundary](layer-a/CLAIM_BOUNDARY.md).

Agent output is a candidate action, not a write grant.
A missing evidence hash, incomplete binding, replayed Permit, or
consumer-side effect drift must fail closed.

Mode: `SHADOW / NO_CREDENTIALS / WorldWriteback=0`.

All five frozen cases use one ID-independent predicate pipeline. Case IDs are
labels and expected outcomes are test data, not hardcoded control flow. The
local Shadow Permit is unsigned, is not a KMS/HSM capability, and cannot
authorize an external or production effect.

No Docker, network request, credential, persistent service, or world writeback.
This is a local proof of mechanism, not production security, a vendor
benchmark, or independent validation.

## 中文｜无需准备，直接查看

1. **[观看 90 秒演示](layer-a/demo.mp4)**
2. **[阅读一分钟结果](layer-b/SAMPLE_SUMMARY.txt)**
3. **[可选：本地复现](layer-b/README.md)**

观看视频或阅读结果即完成首次评审。无需账号、安装、Docker、凭证、
公司数据、回复或会议；本地复现完全自愿，不发出网络请求，
`WorldWriteback=0`。

安全范围与限制见 [安全问答](SECURITY_FAQ.md) 和
[声明边界](layer-a/CLAIM_BOUNDARY.md)。

Agent 输出只是候选动作，不是写授权。证据无法重算、绑定不完整、
Permit 重放或消费侧效果漂移时必须 fail-closed。

五条冻结用例使用同一条不读取用例编号的谓词管线。
本地 Shadow Permit 未签名，不是 KMS/HSM 能力，不能授权外部或生产效果。
无 Docker、无网络请求、无凭证、无常驻服务，世界写回为 0。
这是本地机制验证，不代表生产安全、供应商基准测试或独立验证。
