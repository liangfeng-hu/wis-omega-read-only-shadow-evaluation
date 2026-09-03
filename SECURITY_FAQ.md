# Six answers for security review / 安全转发六问

1. **Must this enter an internal network?** No. Viewing the HTML is enough. Optional reproduction writes only to the operator-selected local `out/` directory.
2. **Does it use a network, dependency install, Docker, or service?** No. It uses the Python standard library, imports no network client, starts no persistent service, and requires no Docker.
3. **Does it request a model key, credential, source code, traffic, or business data?** No. Do not add any such material.
4. **Will the result be described as a measurement of the recipient?** No. The unprotected path is a function in this package, not a vendor or recipient baseline.
5. **Is the Permit a production or cryptographic capability?** No. It is an unsigned local Shadow object, not a KMS/HSM capability, and `WorldWriteback=0`.
6. **Must the reviewer run it or attend a meeting?** No. The report is complete by itself. An optional 15-minute provider-run screen share is available if local execution is inconvenient.

中文摘要：无需进内网、联网、安装依赖、Docker、密钥、流量或业务数据；不会把结果写成对收件方产品的测量；Permit 只是未签名的本地 Shadow 对象；不要求运行或参加会议。
