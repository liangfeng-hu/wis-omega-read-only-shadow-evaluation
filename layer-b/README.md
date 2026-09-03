# WIS-Ω Read-Only Shadow Evaluation

Agent output is a candidate action, not a write grant. A missing evidence hash, an incomplete identity/endpoint/effect/recovery binding, a replayed Permit, or consumer-side effect drift must fail closed.

The same ID-independent predicate pipeline evaluates all five frozen cases. Case IDs are labels only; expected decisions are data, not hardcoded control flow.

Five frozen cases. One standard-library evaluator. No Docker, network, credential, service, or production writeback.

Windows: double-click `RUN_EVALUATION.cmd`.

macOS/Linux:

```bash
./RUN_EVALUATION.sh
```

Canonical interface:

```text
wisomega-eval run --pack cases-shadow-v1 --out out/
```

Outputs: `out/SUMMARY.txt`, `out/report.html`, `out/receipts.jsonl`, and `out/run_metadata.json`.

Mode: `SHADOW / NO_CREDENTIALS / WorldWriteback=0`.

The evaluator reads one frozen JSON pack and writes only to the selected output directory. It uses the Python standard library, starts no service, imports no network client, loads no credential, and performs no external effect.

The report compares WIS-Ω with an intentionally minimal unprotected reference path contained in this package. That path is an illustration, not a measurement of any third-party product, organization, model, or production system.

The Permit is a deterministic local Shadow object. It is not a cryptographic capability, has no KMS/HSM signature, and cannot authorize an external or production effect.

## 中文

五条冻结用例、一个标准库判定器；不需要 Docker，不连接网络，不加载凭证，不启动常驻服务，不写任何生产系统。

Windows 双击 `RUN_EVALUATION.cmd`；macOS/Linux 运行 `./RUN_EVALUATION.sh`。结果只写入 `out/`。

同一条不读取用例编号的谓词管线处理全部五条用例；用例编号只作标签，期望结果也不写死在控制流中。本包中的“无保护参考路径”只是明确声明的最小对照实现，不代表任何第三方产品或公司。Permit 只是未由 KMS/HSM 签名的本地 Shadow 对象，不是密码学能力。
