# --- Hardening da imagem do frontend ---
# nginx-unprivileged: ja roda como usuario sem root (uid 101) na porta 8080
FROM nginxinc/nginx-unprivileged:1.29-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html app.js style.css /usr/share/nginx/html/

EXPOSE 8080
