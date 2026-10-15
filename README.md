# 🍕 Pizzaria do Hacker — Missão 2

App de estudo para cloud security: frontend (nginx) + API (Python/FastAPI) rodando em Kubernetes local com hardening.

```
Navegador ──► frontend (nginx :8080, NodePort 30080) ──► /api ──► pizzaria-api (:8000, só dentro do cluster)
```

## Pré-requisitos
- Docker Desktop com Kubernetes ligado (Settings → Kubernetes → Enable Kubernetes)
- `kubectl get nodes` mostrando um nó **Ready**

## Fase A — Rodar com Docker (aquecimento)
```powershell
cd pizzaria-do-hacker
docker compose up --build
```
Abra http://localhost:8080 e faça um pedido. Depois `Ctrl+C` e `docker compose down`.

## Fase B — Rodar no Kubernetes
```powershell
docker build -t pizzaria-api:v1 ./api
docker build -t pizzaria-frontend:v1 ./frontend
kubectl apply -f k8s/
kubectl get pods -n pizzaria -w      # espere os 2 pods ficarem Running (Ctrl+C para sair)
```
Abra http://localhost:30080

> Se os pods ficarem em `ErrImagePull`/`ImagePullBackOff`, o cluster não está enxergando as imagens locais.
> No Docker Desktop, em Settings → Kubernetes, escolha o modo **kubeadm** e reconstrua as imagens.

## Checklist de hardening (o que cada coisa faz)
| Controle | Onde | Protege contra |
|---|---|---|
| Imagem slim / alpine | Dockerfiles | Menos pacotes = menos CVEs |
| Usuário não-root | Dockerfiles + `runAsNonRoot` | Escalada para root no host |
| `readOnlyRootFilesystem` | Deployments | Atacante não grava malware no container |
| `capabilities: drop ALL` | Deployments | Remove poderes especiais do kernel |
| `allowPrivilegeEscalation: false` | Deployments | Bloqueia setuid/sudo dentro do container |
| `seccompProfile: RuntimeDefault` | Deployments | Filtra chamadas de sistema perigosas |
| `automountServiceAccountToken: false` | Deployments | Sem token para atacar a API do Kubernetes |
| Limits de CPU/memória | Deployments | Negação de serviço / cryptominer |
| Pod Security Admission `restricted` | Namespace | O cluster recusa pods inseguros |
| NetworkPolicy default-deny | k8s/30 | Movimento lateral (aplica no AKS, Missão 5) |
| API como ClusterIP | Service | API não exposta para fora |
| Security headers + CSP | nginx.conf | XSS, clickjacking, sniffing |
| Query parametrizada / `textContent` | app.py / app.js | SQL injection / XSS |

---

# 🚦 Missão 3 — Pipeline com gates de segurança

Arquivo: `.github/workflows/security-gates.yml` (roda no GitHub Actions a cada push e pull request).

| Gate | Ferramenta | Procura | Config |
|---|---|---|---|
| Secrets | Gitleaks | Senhas, tokens e chaves no código **e no histórico do Git** | padrão |
| SAST | Semgrep | Código perigoso (SQL injection, XSS, eval...) | regras públicas + `.semgrep/` |
| SCA | pip-audit | Bibliotecas Python com CVE conhecida | `api/requirements.txt` |
| IaC | Checkov | Erros de segurança em manifests K8s e Dockerfiles | `.checkov.yaml` |
| Imagem | Trivy | CVEs nos pacotes das imagens Docker (HIGH/CRITICAL corrigíveis) | no workflow |

Boas práticas aplicadas no próprio pipeline:
- `permissions: contents: read` — o token do pipeline só lê o código (least privilege).
- Actions de terceiros fixadas por **SHA**, não por tag (tags podem ser movidas, como no ataque ao trivy-action em março/2026).
- Ferramentas com **versão fixa** e download do Gitleaks com **verificação de checksum**.
- `persist-credentials: false` — o token não fica salvo no disco do runner.
- Dependabot (`.github/dependabot.yml`) abre PRs quando há atualização de libs, imagens base e Actions.
