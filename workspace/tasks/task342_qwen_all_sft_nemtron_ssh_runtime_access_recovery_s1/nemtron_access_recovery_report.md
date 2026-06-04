# task342 NemTron SSH/runtime access recovery report

<!-- METADATA:STATUS=ReadyForPR,DISPOSITION=BLOCK_NEMTRON_ACCESS,SESSION=91 -->

Generated: 2026-06-04T12:45:10Z

## Decision

`BLOCK_NEMTRON_ACCESS`.

The current `NemTron` SSH alias still cannot reach the target runtime host.
The proxy hop is reachable and authenticates, but the configured target
`10.100.2.62:33808` refuses TCP connections from that proxy. This appears to be
a target host/port or LTP target service issue, not a local SSH alias, local
auth, DNS, or proxy-hop auth failure.

Because the `NemTron` route is blocked, I could not verify `/root` access,
task337 runtime target readability, task298 checkpoint candidate readability,
task339 train-only root readability, or remote runtime imports. task341 should
not be rerun until the target service/port is restored or a replacement
lead-approved route is provided.

## Scope And Artifacts

- Branch:
  `intern_nemotron_worker_4/task342_qwen_all_sft_nemtron_ssh_runtime_access_recovery_s1`
- Base: `origin/main`
  `371aea491776cc258e1cbb59a081d28be0530438`
- Lead docs:
  `origin/intern_nemotron_lead/session1-recovery-task-docs`
  `c7a417d11cde7935be6f7abdc463426504dfbd33`
- Local artifact root:
  `/work-agents/intern_nemotron_worker_4/outputs/task342_qwen_all_sft_nemtron_ssh_runtime_access_recovery_s1/run_20260604T124233Z`
- Artifact checksum manifest:
  `/work-agents/intern_nemotron_worker_4/outputs/task342_qwen_all_sft_nemtron_ssh_runtime_access_recovery_s1/run_20260604T124233Z/manifests/artifact_checksums.sha256`

## Commands And Results

Commands were run from
`/work-agents/intern_nemotron_worker_4/Nemotron_task342` unless noted.

### Non-secret SSH route inspection

```bash
ssh -G NemTron
```

Captured raw output and stderr:

- `logs/ssh_g_raw.log`
- `logs/ssh_g_stderr.log`
- `logs/ssh_g.rc`

Sanitized/non-secret route summary:

```text
host NemTron
user root
hostname 10.100.2.62
port 33808
identityfile /root/.ssh/id_ed25519
proxycommand ssh -i /root/.ssh/ltp_ssh_key  -p 30222 -W %h:%p sshuser@10.100.197.19
```

`ssh -G` returned rc `0`. It printed only the standard no-tty message on
stderr.

### Required NemTron connectivity probe

```bash
ssh -o ConnectTimeout=10 NemTron 'hostname; date -u +%Y-%m-%dT%H:%M:%SZ'
```

Artifacts:

- `logs/ssh_connectivity_probe.stdout`
- `logs/ssh_connectivity_probe.stderr`
- `logs/ssh_connectivity_probe.rc`
- `manifests/ssh_connectivity_probe_summary.txt`

Result:

- rc: `255`
- stdout: empty
- stderr:

```text
channel 0: open failed: connect failed: Connection refused
stdio forwarding failed
Connection closed by UNKNOWN port 65535
```

### Proxy-hop classification probe

The `ProxyCommand` target was inspected without exposing key material or
changing SSH config. First probe confirmed the proxy hop is reachable but
`python3` is not available on the proxy host:

```bash
ssh -i /root/.ssh/ltp_ssh_key -p 30222 -o BatchMode=yes -o ConnectTimeout=10 sshuser@10.100.197.19 '<hostname/date/python tcp probe>'
```

Artifacts:

- `logs/proxy_target_port_probe.stdout`
- `logs/proxy_target_port_probe.stderr`
- `logs/proxy_target_port_probe.rc`

Result:

- rc: `127`
- stdout included proxy hostname
  `ssh-proxy-deployment-64fbf5f7d5-4flbz` and timestamp
  `2026-06-04T12:43:37Z`.
- stderr: `bash: line 1: python3: command not found`.

Second probe used Bash `/dev/tcp` from the proxy hop to the configured target:

```bash
ssh -i /root/.ssh/ltp_ssh_key -p 30222 -o BatchMode=yes -o ConnectTimeout=10 sshuser@10.100.197.19 \
  'hostname; date -u +%Y-%m-%dT%H:%M:%SZ; timeout 5 bash -lc "</dev/tcp/10.100.2.62/33808" ...'
```

Artifacts:

- `logs/proxy_target_port_probe_bash_tcp.stdout`
- `logs/proxy_target_port_probe_bash_tcp.stderr`
- `logs/proxy_target_port_probe_bash_tcp.rc`
- `manifests/proxy_target_port_probe_bash_tcp_summary.txt`

Result:

- rc: `1`
- stdout:

```text
ssh-proxy-deployment-64fbf5f7d5-4flbz
2026-06-04T12:44:07Z
TCP_CONNECT 10.100.2.62:33808 FAIL rc=1
```

- stderr:

```text
bash: connect: Connection refused
bash: line 1: /dev/tcp/10.100.2.62/33808: Connection refused
```

This confirms the proxy hop authenticates and runs commands, while the target
host/port behind the proxy refuses the TCP connection.

## Blocker Classification

- Local SSH alias/config parse: `PASS`.
- Local private key material inspection: not performed.
- Proxy-hop auth/connectivity: `PASS`.
- Target host/port from proxy hop: `BLOCK`, connection refused.
- Required `ssh NemTron` command: `BLOCK`, rc `255`.
- `/root` access: not testable because SSH route does not reach target.
- task337 runtime target: not testable because SSH route does not reach target.
- task298 checkpoint candidate: not testable because SSH route does not reach
  target.
- task339 train-only root: not testable because SSH route does not reach
  target.
- Runtime imports: not testable because SSH route does not reach target.

Likely required owner/action: coordinator or infrastructure owner needs to
restore or replace the LTP/NemTron target service behind
`10.100.2.62:33808`, or provide a new lead-approved host/port/alias. This
worker should not mutate SSH config, LTP job state, shared runtime roots, or
network/system state to remediate it.

## Artifact Checksum Verdict

From the artifact root:

```bash
sha256sum -c manifests/artifact_checksums.sha256
```

Result: `PASS`, 16 entries.

Important hashes:

- `logs/ssh_connectivity_probe.stderr`:
  `7b8f4b70c99b5e871dd61cfe3c21ccd21a73ce243c8199a780f594c8086ecc90`
- `logs/proxy_target_port_probe_bash_tcp.stdout`:
  `f38a3326621effc9570b110728b97f1e9bd9777ad45472d3ee0f08148f582b44`
- `logs/proxy_target_port_probe_bash_tcp.stderr`:
  `e5aee70c3881f8772ec7c65f7f0c919ed711d3e18f438745d563d5adda813309`
- `manifests/ssh_route_summary_nonsecret.txt`:
  `7729ef2c32268eae0db74aaa81769ccd13cc630cbfe187ac093f35391109e800`
- `manifests/command_env_manifest.txt`:
  `b79c29e6a0b6d2a480a6fcb80b6f66f5f0018315114abb3e4dab0aa59636bd60`

## Boundary Confirmation

Confirmed from commands and artifacts:

- No optimizer steps or training loop.
- No benchmark eval, AIME eval, or task243 eval.
- No export, endpoint, promotion, task310 release, task255 reuse, or AIME2025
  train rows.
- No shared deletion/mutation and no product/source code edits.
- No destructive SSH config changes.
- No main push, merge, or self-merge.
